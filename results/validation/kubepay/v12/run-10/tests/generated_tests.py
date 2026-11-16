# Tests generated in iteration 10
# Captured: 2026-06-14T22:16:46
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1011  name='Auth Signup Success' ---
def test_auth_signup_success():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    url = get_url("gateway", "/auth/signup")
    payload = {"user": username, "password": password}
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Follow-up GET
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

# --- id=1012  name='Auth Signup Bad Request' ---
def test_auth_signup_bad_request():
    url = get_url("gateway", "/auth/signup")
    payload = {"user": "testuser"}
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1013  name='Auth Login Success' ---
def test_auth_login_success():
    token, username, password = create_user()
    url = get_url("gateway", "/auth/login")
    payload = {"user": username, "password": password}
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    new_token = resp.json().get("token")
    assert new_token is not None

    # Follow-up GET
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {new_token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

# --- id=1014  name='Auth Login Bad Request' ---
def test_auth_login_bad_request():
    url = get_url("gateway", "/auth/login")
    payload = {"user": "nonexistent", "password": "wrongpassword"}
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1015  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1016  name='Wallet Balance Success' ---
def test_wallet_balance_success():
    token, _, _ = create_user()
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data.get("balance") == 0

# --- id=1017  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1018  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    token, _, _ = create_user()
    url = get_url("gateway", "/wallet/topup")
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data.get("balance") > 0

    # Follow-up GET
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json().get("balance") == data.get("balance")

# --- id=1019  name='Wallet Topup Bad Request' ---
def test_wallet_topup_bad_request():
    token, _, _ = create_user()
    url = get_url("gateway", "/wallet/topup")
    # First topup
    resp1 = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Second topup should fail
    resp2 = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=1020  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    url = get_url("gateway", "/wallet/topup")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1021  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    token_a, _, _ = create_user()
    token_b, _, _ = create_user()

    # Topup user A
    topup_a = topup_wallet(token_a)
    initial_balance_a = topup_a.get("balance")

    # Get user B address
    info_b = get_wallet_info(token_b)
    address_b = info_b.get("address")
    initial_balance_b = info_b.get("balance")

    # Transfer
    transfer_amount = 10
    url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify response
    data = resp.json()
    assert data.get("balance") == initial_balance_a - transfer_amount

    # Follow-up GET for user A
    balance_a_resp = get_wallet_info(token_a)
    assert balance_a_resp.get("balance") == initial_balance_a - transfer_amount

    # Follow-up GET for user B
    balance_b_resp = get_wallet_info(token_b)
    assert balance_b_resp.get("balance") == initial_balance_b + transfer_amount

# --- id=1022  name='Wallet Transfer Bad Request Insufficient Funds' ---
def test_wallet_transfer_bad_request_insufficient_funds():
    token_a, _, _ = create_user()
    token_b, _, _ = create_user()

    info_b = get_wallet_info(token_b)
    address_b = info_b.get("address")

    # Transfer without topup (balance 0)
    url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 10}
    resp = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1023  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    url = get_url("gateway", "/wallet/transfer")
    payload = {"to": "some_address", "amount": 10}
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
