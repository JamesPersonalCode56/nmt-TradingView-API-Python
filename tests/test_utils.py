from tradingview_api.utils import gen_auth_cookies, gen_session_id


def test_gen_session_id_prefix():
    session_id = gen_session_id("cs")
    assert session_id.startswith("cs_")
    assert len(session_id) > 3


def test_gen_auth_cookies():
    assert gen_auth_cookies("", "") == ""
    assert gen_auth_cookies("abc", "") == "sessionid=abc"
    assert gen_auth_cookies("abc", "sig") == "sessionid=abc;sessionid_sign=sig"
