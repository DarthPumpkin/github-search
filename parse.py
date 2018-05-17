import javalang


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
            if c.isalpha():
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

            tags = []
            # here is where we can do advanced stuff such as making a list of method calls
            body = method.body
            if body is not None:
                for path, expression in javalang.ast.walk_tree(body):
                    if isinstance(expression, javalang.tree.Primary):
                        if expression.qualifier is not None and expression.qualifier != "":
                            tags.append(expression.qualifier)
                    if isinstance(expression, javalang.tree.MemberReference):
                        tags.append(expression.member)
                    if isinstance(expression, javalang.tree.Creator):
                        tags.append(expression.type.name)
                    if isinstance(expression, javalang.tree.MethodInvocation):
                        tags.append(expression.member)
                    if isinstance(expression, javalang.tree.SuperMethodInvocation):
                        tags.append(expression.member)
                    if isinstance(expression, javalang.tree.SuperMemberReference):
                        tags.append(expression.member)
                    if isinstance(expression, javalang.tree.VariableDeclarator):
                        tags.append(expression.name)
                    # print(expression

            score = 0

            # We like static functions, they are often self contained
            if "static" in cls.modifiers:
                score += 1

            name_tags = [package_name, cls.name]
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


            # Filter duplicates and sort
            body_tags = sorted(set(body_tags))
            inheritance_tags = sorted(set(inheritance_tags))
            import_tags = sorted(set(import_tags))
            name_tags = sorted(set(name_tags))
            # print(tags)

            if method.body_position is not None:
                start, end = method.body_position
                _, _, start_of_start_token, _ = start
                _, _, _, end_of_start_token = end
                method_body = code_str[start_of_start_token:end_of_start_token]
            else:
                method_body = ""
            # print(method_body)
            methods += [_make_method_dict(cls, method, score, method_body, body_tags, inheritance_tags, import_tags, name_tags)]

    return methods

def collapse_type(input_type):
    collapsed_type = input_type
    if input_type == "Integer":
        collapsed_type = "int"
    elif input_type == "long":
        collapsed_type = "int"
    elif input_type == "short":
        collapsed_type = "int"
    elif input_type == "double":
        collapsed_type = "float"
    return collapsed_type

def _make_method_dict(cls, method, score, method_body, body_tags, inheritance_tags, import_tags, name_tags):
    parameters = []
    for param in method.parameters:
        parameters += [{"name": param.name,
                        "type": collapse_type(param.type.name),
                        "modifiers": list(param.modifiers)}]
    annotations = [ann.name for ann in method.annotations]
    if method.return_type is not None:
        return_type = collapse_type(method.return_type.name)
    else:
        return_type = "null"
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

def test():
    assert tokenize("HelloWorld") == ["hello", "world"]
    assert tokenize("GPSSatellite") == ["gps", "satellite"]
    assert tokenize("Whatever_Orange_BlueYellow") == ["whatever", "orange", "blue", "yellow"]
    assert tokenize("NotTheCD") == ["not", "the", "cd"]
    assert tokenize("Garbled-Text59WithGrεεk") == ["garbled", "text", "with", "grεεk"]
    assert tokenize("camelCase") == ["camel", "case"]
    assert tokenize("snake_case") == ["snake", "case"]
    assert tokenize("_Who_Uses_This_Naming_Convention_") == ["who", "uses", "this", "naming", "convention"]


test()

if __name__ == "__main__":
    print(find_methods(open("repos/Acosix-alfresco-utility/share/src/main/java/de/acosix/alfresco/utility/share/surf/JSONAwareCssDependencyRule.java", "r").read()))
