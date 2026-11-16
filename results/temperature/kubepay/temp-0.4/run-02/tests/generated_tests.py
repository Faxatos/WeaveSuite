# Tests generated in iteration 02
# Captured: 2026-07-01T08:54:52
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=95  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=96  name='Auth Signup Missing Fields' ---
def test_auth_signup_missing_fields():
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

# --- id=97  name='Auth Login Invalid Password' ---
def test_auth_login_invalid_password():
    username, password, _ = create_user_and_get_token()

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": "WrongPassword!"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"
    assert "message" in resp_login.json() or "type" in resp_login.json()

# --- id=98  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"

    data = resp_me.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=99  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == 0
    address = resp_bal.json()["address"]
    assert address is not None

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    new_balance = resp_topup.json()["balance"]
    assert new_balance > 0
    assert resp_topup.json()["address"] == address

    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == new_balance

    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=100  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200
    balance_a = resp_topup.json()["balance"]

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]
    assert balance_b == 0

    transfer_amount = round(balance_a / 2.0, 2)
    if transfer_amount <= 0:
        transfer_amount = 1.0

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, json=payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200
    assert resp_bal_a2.json()["balance"] == balance_a - transfer_amount

    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200
    assert resp_bal_b2.json()["balance"] == balance_b + transfer_amount

# --- id=101  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 1000000.0}
    resp_transfer = requests.post(transfer_url, json=payload, headers=headers_a, timeout=10)

    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=102  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -5.0}
    resp_transfer = requests.post(transfer_url, json=payload, headers=headers_a, timeout=10)

    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=103  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"amount": 10.0}
    resp_transfer = requests.post(transfer_url, json=payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=104  name='Wallet Transfer Own Address' ---
def test_wallet_transfer_own_address():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200
    balance_a = resp_topup.json()["balance"]
    address_a = resp_topup.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": balance_a / 2.0}
    resp_transfer = requests.post(transfer_url, json=payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.json()["balance"] == balance_a

# --- id=105  name='Unauthorized Access' ---
def test_unauthorized_access():
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"

    headers = {"Authorization": "Bearer invalid_token_123"}
    resp_bal_invalid = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal_invalid.status_code == 401, f"Expected 401, got {resp_bal_invalid.status_code}: {resp_bal_invalid.text}"
