def checkAgrumentType(obj, arg):
    if isinstance(obj, arg):
        return True
    if obj is None:  # TODO:
        return True
    if arg == object:
        return True
    if arg in obj.__class__.__bases__:
        return True
    return False


class Callback(object):
    _args = None
    _callback = None

    def __init__(self, *args):
        self._args = args

    def connect(self, callback):
        self._callback = callback

    def emit(self, *args):
        if len(args) != len(self._args):
            raise Exception('Callback::Argument Length Mismatch')
        arglen = len(args)
        if arglen > 0:
            validTypes = [checkAgrumentType(args[i], self._args[i]) for i in range(arglen)]
            if sum(validTypes) != arglen:
                raise Exception('Callback::Argument Type Mismatch (Definition: {}, Call: {}, Result: {})'.format(
                    self._args, args, validTypes))
        if self._callback is not None:
            self._callback(*args)
