def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def format_number(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"
