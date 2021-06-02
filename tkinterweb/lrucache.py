from _thread import RLock
from functools import update_wrapper, _make_key


def _lru_cache_wrapper(user_function):
    """This function is a modified version of the one that comes built-in with functools
    It only adds to the cache if the data is not None.
    This means that if a page load is stopped, re-loading the page will not cause the page to be blank."""
    sentinel = object()
    make_key = _make_key 
    PREV, NEXT, KEY, RESULT = 0, 1, 2, 3 

    cache = {}
    hits = misses = 0
    maxsize = 128
    typed = False
    full = False
    cache_get = cache.get
    cache_len = cache.__len__
    lock = RLock()
    root = []
    root[:] = [root, root, None, None]

    def wrapper(*args, **kwds):
        nonlocal root, hits, misses, full
        key = make_key(args, kwds, typed)
        with lock:
            link = cache_get(key)
            if link is not None:
                link_prev, link_next, _key, result = link
                link_prev[NEXT] = link_next
                link_next[PREV] = link_prev
                last = root[PREV]
                last[NEXT] = root[PREV] = link
                link[PREV] = last
                link[NEXT] = root
                hits += 1
                return result
            misses += 1
        result = user_function(*args, **kwds)
        if result[0]:
            with lock:
                if key in cache:
                    pass
                elif full:
                    oldroot = root
                    oldroot[KEY] = key
                    oldroot[RESULT] = result
                    root = oldroot[NEXT]
                    oldkey = root[KEY]
                    oldresult = root[RESULT]
                    root[KEY] = root[RESULT] = None
                    del cache[oldkey]
                    cache[key] = oldroot
                else:
                    last = root[PREV]
                    link = [last, root, key, result]
                    last[NEXT] = root[PREV] = cache[key] = link
                    full = (cache_len() >= maxsize)
        return result
    return wrapper


def lru_cache():
    def decorator(func):
        wrapper = _lru_cache_wrapper(func)
        return update_wrapper(wrapper, func)
    return decorator
