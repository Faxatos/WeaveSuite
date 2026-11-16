# Tests generated in iteration 12
# Captured: 2026-07-01T21:44:33
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=380  name='Auth Signup And User Info' ---
def test_auth_signup_and_user_info():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    signup_resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]
    assert "token" in signup_resp.json()

    me_resp = requests.get(
        get_url("gateway", "/user/me"),
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["user"] == username
    assert "enabled" in me_data

# --- id=381  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    login_resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"
    assert "message" in login_resp.json()

# --- id=382  name='Wallet Topup And Repetition' ---
def test_wallet_topup_and_repetition():
    _, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data["balance"] == 0
    address = bal_data["address"]

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    bal_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

    topup_resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"
    assert "message" in topup_resp2.json()

# --- id=383  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a_initial = topup_a.json()["balance"]

    bal_a_verify = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a_verify.status_code == 200, f"Expected 200, got {bal_a_verify.status_code}: {bal_a_verify.text}"
    assert bal_a_verify.json()["balance"] == balance_a_initial

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]
    balance_b_initial = bal_b.json()["balance"]

    transfer_amount = 1

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a_initial - transfer_amount

    bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a2.status_code == 200, f"Expected 200, got {bal_a2.status_code}: {bal_a2.text}"
    assert bal_a2.json()["balance"] == balance_a_initial - transfer_amount

    bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b2.status_code == 200, f"Expected 200, got {bal_b2.status_code}: {bal_b2.text}"
    assert bal_b2.json()["balance"] == balance_b_initial + transfer_amount

# --- id=384  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a.status_code == 200, f"Expected 200, got {bal_a.status_code}: {bal_a.text}"
    assert bal_a.json()["balance"] == 0

    bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_b.status_code == 200, f"Expected 200, got {bal_b.status_code}: {bal_b.text}"
    address_b = bal_b.json()["address"]

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert "message" in transfer_resp.json()

# --- id=385  name='Wallet Transfer Invalid Inputs' ---
def test_wallet_transfer_invalid_inputs():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "some_address", "amount": -5},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert "message" in transfer_resp.json()

    transfer_resp2 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 5},
        timeout=10
    )
    assert transfer_resp2.status_code == 400, f"Expected 400, got {transfer_resp2.status_code}: {transfer_resp2.text}"
    assert "message" in transfer_resp2.json()

    transfer_resp3 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "some_address"},
        timeout=10
    )
    assert transfer_resp3.status_code == 400, f"Expected 400, got {transfer_resp3.status_code}: {transfer_resp3.text}"
    assert "message" in transfer_resp3.json()

# --- id=386  name='Wallet Transfer Recipient Not Found' ---
def test_wallet_transfer_recipient_not_found():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "unknown_wallet_address_123", "amount": 1},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert "message" in transfer_resp.json()

# --- id=387  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a.status_code == 200, f"Expected 200, got {bal_a.status_code}: {bal_a.text}"
    address_a = bal_a.json()["address"]
    balance_a = bal_a.json()["balance"]

    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 0},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a

    bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_a2.status_code == 200, f"Expected 200, got {bal_a2.status_code}: {bal_a2.text}"
    assert bal_a2.json()["balance"] == balance_a

# --- id=388  name='User Unauthorized Access' ---
def test_user_unauthorized_access():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=389  name='Wallet Unauthorized Access' ---
def test_wallet_unauthorized_access():
    endpoints = [
        ("GET", "/wallet/balance"),
        ("GET", "/wallet/topup"),
        ("POST", "/wallet/transfer")
    ]

    for method, path in endpoints:
        url = get_url("gateway", path)
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json={"to": "addr", "amount": 10}, timeout=10)

        assert resp.status_code == 401, f"Expected 401 for {method} {path}, got {resp.status_code}: {resp.text}"
