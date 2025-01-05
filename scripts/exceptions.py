class FetchError(Exception):
    """Raised when there is an error fetching RSS feeds."""
    pass

class ParseError(Exception):
    """Raised when there is an error parsing RSS feeds."""
    pass

class NotionAPIError(Exception):
    """Raised when there is an error interacting with the Notion API."""
    pass

class UnexpectedError(Exception):
    """Raised when there is an error interacting with the UnexpectedError."""
    pass

class CompareAndUpdate(Exception):
    """Raised when there is an error interacting with the CompareAndUpdate."""
    pass
