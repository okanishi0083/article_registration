from datetime import datetime, timedelta


def get_cutoff_date(days=2):
    """Returns the cutoff date for filtering recent entries.

    Args:
        days (int): The number of days to subtract from the current date. Defaults to 2.

    Returns:
        datetime: The cutoff date.
    """
    return datetime.now() - timedelta(days=days)


def format_datetime(date_obj, format_str="%Y-%m-%d"):
    """Formats a datetime object into a string based on the given format.

    Args:
        date_obj (datetime): The datetime object to format.
        format_str (str): The format string. Defaults to "%Y-%m-%d".

    Returns:
        str: The formatted date string.
    """
    return date_obj.strftime(format_str)
