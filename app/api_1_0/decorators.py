from functools import wraps
from .errors import forbidden
from flask import g

def permission_required(permission):
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kw):
			if not g.current_user.can(permission):
				return forbidden('Insufficient permissions')
			return func(*args, **kw)
		return wrapper
	return decorator













