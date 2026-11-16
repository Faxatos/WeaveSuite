# Tests generated in iteration 15
# Captured: 2026-07-03T03:59:33
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=938  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Follow-up GET
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

    # Follow-up GET for login
    resp_me_login = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == username

# --- id=939  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": f"user_{uuid.uuid4().hex[:8]}", "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=940  name='User Me' ---
def test_user_me():
    token, username = setup_user()

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=941  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    token, _ = setup_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    address = data.get("address")
    assert address is not None
    assert data.get("balance") == 0

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("address") == address
    topup_balance = topup_data.get("balance")
    assert topup_balance > 0

    # Verify balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == topup_balance

    # Topup again -> 400
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=942  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    token_a, _ = setup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10).json()
    address_a = topup_a["address"]
    balance_a_initial = topup_a["balance"]

    token_b, _ = setup_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Balance User B
    resp_b_initial = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()
    balance_b_initial = resp_b_initial["balance"]
    address_b = resp_b_initial["address"]

    # Transfer A -> B
    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    assert transfer_data["address"] == address_a
    assert transfer_data["balance"] == balance_a_initial - transfer_amount

    # Verify A balance
    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    assert resp_a.json()["balance"] == balance_a_initial - transfer_amount

    # Verify B balance
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    assert resp_b.json()["balance"] == balance_b_initial + transfer_amount

# --- id=943  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    token_a, _ = setup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, _ = setup_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    address_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()["address"]

    # Transfer A -> B (A has 0 balance)
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=944  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    token_a, _ = setup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    token_b, _ = setup_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    address_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()["address"]

    transfer_amount = -10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=945  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    token_a, _ = setup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=946  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    token_a, _ = setup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=947  name='Wallet Transfer To Self' ---
def test_wallet_transfer_to_self():
    token_a, _ = setup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10).json()
    address_a = topup_a["address"]
    balance_a_initial = topup_a["balance"]

    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify A balance unchanged
    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    assert resp_a.json()["balance"] == balance_a_initial

# --- id=948  name='Auth Unauthorized' ---
def test_auth_unauthorized():
    # Wallet balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # User me
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
