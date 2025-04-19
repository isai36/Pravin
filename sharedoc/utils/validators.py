def format_malaysian_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "")
    if phone.startswith('+60'):
        return phone
    elif phone.startswith('0'):
        return '+60' + phone[1:]
    return phone