import javalang


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
            # here is where we can do advanced stuff such as making a list of method calls
            body = method.body
            if body is not None:
                for expression in body:
                    pass  # do advanced things here

            methods += [_make_method_dict(cls, method)]

    return methods


def _make_method_dict(cls, method):
    parameters = []
    for param in method.parameters:
        parameters += [{"name": param.name,
                        "type": param.type.name,
                        "modifiers": param.modifiers}]
    annotations = [ann.name for ann in method.annotations]
    if method.return_type is not None:
        return_type = method.return_type.name
    else:
        return_type = "null"
    return {"name": method.name,
            "return_type": return_type,
            "parameters": parameters,
            "class": cls.name,
            "annotations": annotations}


if __name__ == "__main__":
    print(find_methods(open("parser_test/ScalablePersistentHashedIndex.java", "r").read()))
