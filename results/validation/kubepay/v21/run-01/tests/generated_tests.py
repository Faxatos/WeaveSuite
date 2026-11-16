# Tests generated in iteration 01
# Captured: 2026-06-16T01:37:13
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1395  name='Auth Signup Login And User Info' ---
def test_auth_signup_login_and_user_info():
    username, password, token = create_user_and_verify()

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]

    # Follow-up GET /user/me with new token
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["user"] == username
    assert "name" in me_data
    assert "enabled" in me_data

# --- id=1396  name='Auth Failures' ---
def test_auth_failures():
    # Missing password
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Login missing password
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1397  name='Wallet Topup Success And Duplicate Failure' ---
def test_wallet_topup_success_and_duplicate_failure():
    _, _, token = create_user_and_verify()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    initial_data = balance_resp.json()
    assert initial_data["balance"] == 0
    address = initial_data["address"]

    # Top-up (State changing GET)
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Follow-up GET
    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json()["balance"] == new_balance

    # Duplicate Top-up
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"
    err_data = topup_resp2.json()
    assert "message" in err_data

# --- id=1398  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user_and_verify()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Top-up User A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    # User B
    _, _, token_b = create_user_and_verify()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]
    balance_b = balance_b_resp.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a / 2.0

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    transfer_data = transfer_resp.json()
    assert transfer_data["balance"] == balance_a - transfer_amount

    # Follow-up GET User A
    balance_a_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_a_resp2.status_code == 200, f"Expected 200, got {balance_a_resp2.status_code}: {balance_a_resp2.text}"
    assert balance_a_resp2.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET User B
    balance_b_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_b_resp2.status_code == 200, f"Expected 200, got {balance_b_resp2.status_code}: {balance_b_resp2.text}"
    assert balance_b_resp2.json()["balance"] == balance_b + transfer_amount

# --- id=1399  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = create_user_and_verify()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]
    address_a = topup_a.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer 0
    resp1 = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"
    assert resp1.json()["balance"] == balance_a

    # Follow-up GET
    balance_resp1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp1.status_code == 200, f"Expected 200, got {balance_resp1.status_code}: {balance_resp1.text}"
    assert balance_resp1.json()["balance"] == balance_a

    # Transfer to self
    resp2 = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": balance_a / 2.0}, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json()["balance"] == balance_a

    # Follow-up GET
    balance_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json()["balance"] == balance_a

# --- id=1400  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, _, token_a = create_user_and_verify()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_a.status_code == 200, f"Expected 200, got {topup_a.status_code}: {topup_a.text}"
    balance_a = topup_a.json()["balance"]

    _, _, token_b = create_user_and_verify()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Missing 'amount'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative amount
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Insufficient funds
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a + 1000}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Recipient not found
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1401  name='Unauthorized Access' ---
def test_unauthorized_access():
    # Missing token
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token_123"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
