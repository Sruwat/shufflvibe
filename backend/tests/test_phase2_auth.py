def test_register_login_me_and_logout(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    from app.main import (
        AuthLoginRequest,
        AuthRegisterRequest,
        _auth_accounts,
        _auth_tokens,
        _auth_user,
        login,
        logout,
        register,
    )

    _auth_accounts.clear()
    _auth_tokens.clear()
    created = register(AuthRegisterRequest(email="phase2@example.com", password="strong-pass-123", name="Phase Two"))
    token = created["access_token"]
    assert token

    try:
        register(AuthRegisterRequest(email="PHASE2@example.com", password="strong-pass-123"))
    except Exception as error:
        assert getattr(error, "status_code", None) == 409
    else:
        raise AssertionError("duplicate registration should fail")

    assert _auth_user(f"Bearer {token}")["email"] == "phase2@example.com"

    logged_in = login(AuthLoginRequest(email="phase2@example.com", password="strong-pass-123"))
    second_token = logged_in["access_token"]
    assert second_token != token

    try:
        login(AuthLoginRequest(email="phase2@example.com", password="wrong-pass-123"))
    except Exception as error:
        assert getattr(error, "status_code", None) == 401
    else:
        raise AssertionError("wrong password should fail")

    assert logout(f"Bearer {token}") == {"logged_out": True}
    assert _auth_user(f"Bearer {token}") is None
