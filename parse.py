import javalang
import javalang.tree


def tokenize(s):
    result = []
    current = ""
    for c in s:
        if c in ["-", "_", ".", "@", "!", ",", "|", "+"]:
            if current != "":
                result.append(current)
                current = ""
            continue

        if c.isupper():
            if current == "":
                current += c
            elif current[-1].isupper():
                current += c
            else:
                # New token
                result.append(current)
                current = c
        else:
            if current == "":
                current += c
            elif current[-1].isupper() and len(current) > 1:
                # New token of uppercase letters
                result.append(current[:-1])
                current = current[-1]
                current += c
            else:
                current += c

    if len(current) > 0:
        result.append(current)

    results2 = []
    for s in result:
        s2 = ""
        for c in s:
            if c.isalpha() or c in "[]<>,":
                s2 += c

        if s2 != "":
            results2.append(s2.lower())

    return results2


def find_methods(code_str: str):
    """
    :param code_str: The code of the file to parse, as a string (that's the only thing javalang accepts)
    :return: A list of dicts, each of which represents a method
    """
    methods = []
    cu = javalang.parse.parse(code_str)

    # these might be useful later if we want to try some rudimentary name resolution
    package_name = cu.package.name if cu.package is not None else "default"
    imports = [imp.path for imp in cu.imports]

    classes = cu.types
    for cls in classes:
        if not isinstance(cls, javalang.tree.ClassDeclaration):
            continue

        # extra class metadata if we're interested
        superclass = cls.extends.name if cls.extends is not None else None
        interfaces = [interface.name for interface in (cls.implements or [])]

        for method in cls.methods:
            # Skip getters and setters (except for methods just named 'get', which may be more interesting)
            if (method.name.startswith("get") and method.name != "get") or method.name.startswith("set"):
                continue

            if method.body_position is not None:
                start, end = method.body_position
                _, _, start_of_start_token, _ = start
                _, _, _, end_of_start_token = end
                method_body = code_str[start_of_start_token:end_of_start_token]
            else:
                method_body = ""

            tags = []
            # here is where we can do advanced stuff such as making a list of method calls
            body = method.body
            references_method_with_same_name = False
            total_statements = 0
            if body is not None:
                for path, expression in javalang.ast.walk_tree(body):
                    if isinstance(expression, javalang.tree.Statement):
                        total_statements += 1

                    if isinstance(expression, javalang.tree.Primary):
                        if expression.qualifier is not None and expression.qualifier != "":
                            tags.append(expression.qualifier)
                    if isinstance(expression, javalang.tree.MemberReference):
                        tags.append(expression.member)
                    if isinstance(expression, javalang.tree.Creator):
                        tags.append(expression.type.name)
                    if isinstance(expression, javalang.tree.MethodInvocation):
                        tags.append(expression.member)
                        if expression.member == method.name:
                            references_method_with_same_name = True
                    if isinstance(expression, javalang.tree.SuperMethodInvocation):
                        tags.append(expression.member)
                        if expression.member == method.name:
                            references_method_with_same_name = True
                    if isinstance(expression, javalang.tree.SuperMemberReference):
                        tags.append(expression.member)
                    if isinstance(expression, javalang.tree.VariableDeclarator):
                        tags.append(expression.name)
                    # print(expression

            if total_statements <= 3 and references_method_with_same_name:
                # Ignoring method because it is likely just a wrapper
                continue

            score = 0

            # We like static functions, they are often self contained
            if "static" in cls.modifiers:
                score += 1

            name_tags = [package_name, cls.name, method.name]
            import_tags = []
            import_tags += imports

            inheritance_tags = []
            if superclass is not None:
                inheritance_tags.append(superclass)
            for interface in interfaces:
                inheritance_tags.append(interface)

            # Tokenize the individual tags and concatenate the resulting lists
            body_tags = sum((tokenize(s) for s in tags), [])
            inheritance_tags = sum((tokenize(s) for s in inheritance_tags), [])
            import_tags = sum((tokenize(s) for s in import_tags), [])
            name_tags = sum((tokenize(s) for s in name_tags), [])

            # Common parts of package names
            if "net" in name_tags:
                name_tags.remove("net")
            if "org" in name_tags:
                name_tags.remove("org")


            # Filter duplicates and sort
            body_tags = sorted(set(body_tags))
            inheritance_tags = sorted(set(inheritance_tags))
            import_tags = sorted(set(import_tags))
            name_tags = sorted(set(name_tags))
            # print(tags)

            # print(method_body)
            methods += [_make_method_dict(cls, method, score, method_body, body_tags, inheritance_tags, import_tags, name_tags)]

    return methods

def collapse_type(input_type):
    collapsed_type = input_type
    if input_type == "int":
        collapsed_type = "Integer"
    elif input_type.lower() == "long":
        collapsed_type = "Integer"
    elif input_type.lower() == "short":
        collapsed_type = "Integer"
    elif input_type.lower() == "double":
        collapsed_type = "Float"
    elif input_type == "float":
        collapsed_type = "Float"
    elif input_type == "String":
        collapsed_type = "CharSequence"
    elif input_type == "char[]":
        collapsed_type = "CharSequence"
    elif input_type == "Segment":
        collapsed_type = "CharSequence"
    elif input_type.endswith("[]"):
        type_param = collapse_type(input_type[:-2])
        collapsed_type = f"List<{type_param}>"
    # will fail for things like ArrayListWrqpper
    elif input_type.startswith("ArrayList"):
        collapsed_type = input_type[5:]
    return collapsed_type

def _make_method_dict(cls, method, score, method_body, body_tags, inheritance_tags, import_tags, name_tags):
    parameters = []
    for param in method.parameters:
        parameters += [{"name": param.name,
                        "type": collapse_type(param.type.name),
                        "modifiers": list(param.modifiers)}]
    annotations = [ann.name for ann in method.annotations]
    ret_type = method.return_type
    return_type = _type_to_str(ret_type)
    return {
        "name": method.name,
        "return_type": return_type,
        "parameters": parameters,
        "class": cls.name,
        "annotations": annotations,
        "body": method_body,
        "body_tags": body_tags,
        "inheritance_tags": inheritance_tags,
        "import_tags": import_tags,
        "name_tags": name_tags,
        "score": score,
    }


def _type_to_str(ret_type: javalang.tree.Type):
    if ret_type is not None:
        return_type_str = ret_type.name
        if isinstance(ret_type, javalang.tree.ReferenceType) and ret_type.arguments:
            type_params = [_type_to_str(arg.type) for arg in ret_type.arguments]
            return_type_str += f"<{', '.join(type_params)}>"
        if ret_type.dimensions:
            return_type_str += '[]' * len(ret_type.dimensions)
        return_type_str = collapse_type(return_type_str)
    else:
        return_type_str = "null"
    return return_type_str


def test():
    assert tokenize("HelloWorld") == ["hello", "world"]
    assert tokenize("GPSSatellite") == ["gps", "satellite"]
    assert tokenize("Whatever_Orange_BlueYellow") == ["whatever", "orange", "blue", "yellow"]
    assert tokenize("NotTheCD") == ["not", "the", "cd"]
    assert tokenize("Garbled-Text59WithGrεεk") == ["garbled", "text", "with", "grεεk"]
    assert tokenize("camelCase") == ["camel", "case"]
    assert tokenize("snake_case") == ["snake", "case"]
    assert tokenize("_Who_Uses_This_Naming_Convention_") == ["who", "uses", "this", "naming", "convention"]

    assert collapse_type("short") == "Integer"
    assert collapse_type("Float") == "Float"
    assert collapse_type("int[]") == "List<Integer>"
    assert collapse_type("int[][]") == "List<List<Integer>>"
    assert collapse_type("Double[][]") == "List<List<Float>>"
    assert collapse_type("ArrayList[]") == "List<List>"
    assert collapse_type("char[][]") == "List<CharSequence>"
    assert collapse_type("String") == "CharSequence"
    assert collapse_type("Segment") == "CharSequence"

    # assert collapse_type("List<String>") == "List<CharSequence>"  # fails


test()

if __name__ == "__main__":
    print(find_methods(open("repos/Acosix-alfresco-utility/share/src/main/java/de/acosix/alfresco/utility/share/surf/JSONAwareCssDependencyRule.java", "r").read()))
