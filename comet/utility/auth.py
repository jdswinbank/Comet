from functools import wraps

def check_auth(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.must_auth or (self.must_auth and self.authenticated):
            return f(self, *args, **kwargs)
    return wrapper

