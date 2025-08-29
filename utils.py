# utils.py
from config import ALLOWED_EXTENSIONS
from num2words import num2words

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_currency(amount):
    return f"{amount:,.0f}".replace(",", ".")

def number_to_words(n):
    if n <= 0:
        return "không"
    try:
        return num2words(n, lang='vi')
    except Exception:
        return "không xác định"

def capitalize_first(s):
    return s[0].upper() + s[1:] if s else s