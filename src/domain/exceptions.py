# Domain exceptions

class EntityError(Exception):
    def __init__(self, errors):
        self.errors = errors
        self.message = "Validation error"
        super().__init__(self.message)

class AuthError(Exception):
    def __init__(self, message="Authentication error"):
        self.message = message
        super().__init__(self.message)

class StatusError(Exception):
    def __init__(self, message="Error", status=500):
        self.message = message
        self.status = status
        super().__init__(self.message)

class ForbiddenError(Exception):
    def __init__(self, message="Forbidden"):
        self.message = message
        self.status = 403
        super().__init__(self.message)

