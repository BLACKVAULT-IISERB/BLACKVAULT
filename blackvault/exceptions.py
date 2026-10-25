class BlackvaultError(Exception):
    """Base application error."""

class ValidationError(BlackvaultError): pass
class PermitError(BlackvaultError): pass
