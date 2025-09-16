import re

patterns = {
    "IdentityId": r"^(?:\d{9}|\d{12})$",
    "Phone": r"^(?:\+84|0)(?:\d{9})$",
    "LicensePlateNumber": r"^\d{2}[A-Z]{1,2}-\d{3}\.\d{2}$",
    "TaxCode": r"^\d{10}(?:-\d{3})?$",
    "ElectricWaterId": r"^[A-Z0-9]{5,10}\d{5}$",
    "BankAccount": r"^\d{9,16}$",
    "Passport": r"^[A-Z]\d{7,8}$",
    "SocialInsurance": r"^\d{10}$",
    "HealthInsurance": r"^[A-Z]{2}\d{13}$",
}


def detect_id(value):
    for pattern in patterns.values():
        if re.fullmatch(pattern, value):
            return True
    return False


def filter_id(value):
    value_ = re.sub(r'[.,]', '', value)
    vals = re.split(r'\s+', value_)
    for v in vals:
        if detect_id(v):
            return v
    return ""


def filter_ids(values):
    return [x for val in values if (x := filter_id(val))]


def classify_ids(values):
    results = {}
    for val in values:
        matches = [name for name, pattern in patterns.items() if re.fullmatch(pattern, val)]
        results[val] = matches if matches else None
    return results