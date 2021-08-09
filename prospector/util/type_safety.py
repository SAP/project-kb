def is_instance_of_either(collection, *types_to_check) -> bool:
    for item in collection:
        item_is_good = False
        for _type in types_to_check:
            if isinstance(item, _type):
                item_is_good = True
                break
        if not item_is_good:
            return False
    return True
