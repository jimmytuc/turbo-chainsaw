import re
import arrow

def match_date(s):
    matches = re.findall("[\\d-]{8,10}", s)
    if matches:
        return matches[0]
    else:
        return False

def str_to_date(s):
    try:
        return str(arrow.get(s, "YYYY-M-D").format("YYYY-MM-DD"))
    except Exception:
        return False

def process_url(s):
    if len(s) < 255:
        return s
    return ""
