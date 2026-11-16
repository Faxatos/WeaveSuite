# Tests generated in iteration 10
# Captured: 2026-06-22T12:57:09
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=300  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user, password = generate_credentials()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    assert token

    # Verify user info
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data.get("user") == user

# --- id=301  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    user, _ = generate_credentials()
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": user}, timeout=10)
    assert signup_resp.status_code == 400, f"Expected 400, got {signup_resp.status_code}: {signup_resp.text}"

# --- id=302  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    user, password, _ = register_user()
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": user, "password": password + "wrong"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=303  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    user, password, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert "address" in balance_data
    assert balance_data.get("balance") == 0

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data.get("address") == balance_data.get("address")
    new_balance = topup_data.get("balance")
    assert new_balance > 0

    # Verify balance updated
    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json().get("balance") == new_balance

    # Topup again should fail (one-time operation)
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=304  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json().get("balance")
    assert balance_a_initial >= 10, "Topup amount too small for test"

    # User B
    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json().get("address")
    balance_b_initial = balance_resp_b.json().get("balance")
    assert balance_b_initial == 0

    # Transfer A -> B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    transfer_data = transfer_resp.json()
    assert transfer_data.get("balance") == balance_a_initial - transfer_amount

    # Verify A balance
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json().get("balance") == balance_a_initial - transfer_amount

    # Verify B balance
    balance_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b2.status_code == 200, f"Expected 200, got {balance_resp_b2.status_code}: {balance_resp_b2.text}"
    assert balance_resp_b2.json().get("balance") == transfer_amount

# --- id=305  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json().get("balance")

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    transfer_amount = balance_a + 100
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A balance unchanged
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.json().get("balance") == balance_a

# --- id=306  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -50}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=307  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    transfer_resp1 = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert transfer_resp1.status_code == 400, f"Expected 400, got {transfer_resp1.status_code}: {transfer_resp1.text}"

    # Missing 'amount'
    transfer_resp2 = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert transfer_resp2.status_code == 400, f"Expected 400, got {transfer_resp2.status_code}: {transfer_resp2.text}"

# --- id=308  name='Wallet Transfer Zero Amount And Self' ---
def test_wallet_transfer_zero_amount_and_self():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json().get("balance")
    address_a = topup_resp.json().get("address")

    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer 0 to B
    transfer_payload_zero_b = {"to": address_b, "amount": 0}
    transfer_resp_zero_b = requests.post(transfer_url, headers=headers_a, json=transfer_payload_zero_b, timeout=10)
    assert transfer_resp_zero_b.status_code == 200, f"Expected 200, got {transfer_resp_zero_b.status_code}: {transfer_resp_zero_b.text}"
    assert transfer_resp_zero_b.json().get("balance") == balance_a

    # Transfer to self with amount > 0
    transfer_payload_self = {"to": address_a, "amount": 10}
    transfer_resp_self = requests.post(transfer_url, headers=headers_a, json=transfer_payload_self, timeout=10)
    assert transfer_resp_self.status_code == 200, f"Expected 200, got {transfer_resp_self.status_code}: {transfer_resp_self.text}"
    assert transfer_resp_self.json().get("balance") == balance_a

    # Verify balance unchanged
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.json().get("balance") == balance_a

# --- id=309  name='Unauthorized Access' ---
def test_unauthorized_access():
    endpoints = [
        ("GET", "/user/me"),
        ("GET", "/wallet/balance"),
        ("GET", "/wallet/topup")
    ]

    for method, path in endpoints:
        url = get_url("gateway", path)
        resp = requests.get(url, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {method} {path}, got {resp.status_code}: {resp.text}"

    # For POST /wallet/transfer, we need a valid payload but no token
    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, json={"to": address_b, "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"
