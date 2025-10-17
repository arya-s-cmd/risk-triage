from email_validator import validate_email, EmailNotValidError
import phonenumbers
from dateutil import parser as dateparser

def norm_email(s):
    if not s: return None
    s=s.strip().lower()
    try: return validate_email(s, check_deliverability=False).normalized
    except EmailNotValidError: return None

def norm_phone(s):
    if not s: return None
    try:
        num = phonenumbers.parse(s, 'IN')
        if not phonenumbers.is_valid_number(num): return None
        return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None

def iso_datetime(s):
    if not s: return None
    try:
        dt = dateparser.parse(s)
        return dt.replace(microsecond=0).isoformat()
    except Exception:
        return None
