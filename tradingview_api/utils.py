import random
import string


def gen_session_id(prefix="xs"):
    chars = string.ascii_letters + string.digits
    return f"{prefix}_{''.join(random.choice(chars) for _ in range(12))}"


def gen_auth_cookies(session_id="", signature=""):
    if not session_id:
        return ""
    if not signature:
        return f"sessionid={session_id}"
    return f"sessionid={session_id};sessionid_sign={signature}"
