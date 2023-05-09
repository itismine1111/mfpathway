class Cache_mem:
    def __init__(self, ):
        self.cache = dict()

    # we return the value of the key
    # that is queried in dict(key) and return False if we
    # don't find the key in out dict / cache.
    def get(self, key):
        if key not in self.cache:
            return False
        else:
            return self.cache[key]

    # we add / update the key by conventional methods.
    def put(self, key, value):
        self.cache[key] = value

    # delete the key value pair by conventional methods.
    def pop(self, key):
        if key not in self.cache:
            return False
        self.cache.pop(key)


Cache = Cache_mem()
