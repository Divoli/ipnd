def flatten(items):
    for item in items:
        try:
            yield from flatten(item)
        except TypeError:
            yield item
