__GLOBAL_REGISTRY = {}

def register(transform):
    global __GLOBAL_REGISTRY
    name = '{}.{}'.format(transform.category, transform.name)
    if name in __GLOBAL_REGISTRY:
        raise Exception("Transform with the name {} already exists".format(name))
    __GLOBAL_REGISTRY[name] = transform

def lookup(name, category=""):
    if category:
        name = '{}.{}'.format(category, name)
    if name in __GLOBAL_REGISTRY:
        return __GLOBAL_REGISTRY[name]
    return None

def getall(category=""):
    #return [k for k in __GLOBAL_REGISTRY if not category or k.startswith(category)]
    return [v.key for k, v in __GLOBAL_REGISTRY.iteritems() if not category or category == k.category]

def make_registry():
    from transforms import string # NOQA
