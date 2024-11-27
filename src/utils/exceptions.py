class APIException(Exception):
    """Base exception for all API errors"""
    def __init__(self, message, status_code=None, code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code

class ValidationError(APIException):
    """Raised when input validation fails"""
    def __init__(self, message):
        super().__init__(message, status_code=400, code='INVALID_REQUEST')

class AuthenticationError(APIException):
    """Raised when authentication fails"""
    def __init__(self, message="Authentication required"):
        super().__init__(message, status_code=401, code='UNAUTHORIZED')

class AuthorizationError(APIException):
    """Raised when user doesn't have permission for an action"""
    def __init__(self, message="Permission denied"):
        super().__init__(message, status_code=403, code='FORBIDDEN')

class ResourceNotFoundError(APIException):
    """Raised when a requested resource is not found"""
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404, code='NOT_FOUND')

class RateLimitError(APIException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message="Rate limit exceeded"):
        super().__init__(message, status_code=429, code='RATE_LIMITED')

class LLMError(APIException):
    """Raised when there's an error with LLM service"""
    def __init__(self, message="Error processing LLM request"):
        super().__init__(message, status_code=500, code='LLM_ERROR')

class FileUploadError(APIException):
    """Raised when there's an error with file upload"""
    def __init__(self, message="Error uploading file"):
        super().__init__(message, status_code=500, code='FILE_UPLOAD_ERROR')