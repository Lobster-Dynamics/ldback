from functools import wraps

def exclude_verify_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper._exclude_verify_token = True
    return wrapper