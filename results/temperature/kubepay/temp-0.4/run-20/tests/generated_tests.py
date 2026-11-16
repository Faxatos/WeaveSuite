# Tests generated in iteration 20
# Captured: 2026-07-01T16:36:45
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=268  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == username

# --- id=269  name='Auth Signup Conflict' ---
def test_auth_signup_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp2 = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=270  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=271  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "nonexistent", "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=272  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user()

    balance_url = get_url("gateway", "/wallet/balance")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] == 0

# --- id=273  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    _, _, token = create_user()

    topup_url = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["balance"] > 0

    balance_url = get_url("gateway", "/wallet/balance")
    resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    balance_data = resp2.json()
    assert balance_data["balance"] == topup_data["balance"]
    assert balance_data["address"] == topup_data["address"]

# --- id=274  name='Wallet Topup Repetition' ---
def test_wallet_topup_repetition():
    _, _, token = create_user()

    topup_url = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=275  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json()["balance"]
    assert balance_a_initial > 0

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b_initial = resp.json()["balance"]

    transfer_amount = max(1, int(balance_a_initial / 2))
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    assert transfer_data["balance"] == balance_a_initial - transfer_amount

    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_b_initial + transfer_amount

# --- id=276  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 1000}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=277  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -10}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=278  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_address_123", "amount": 10}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=279  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    balance_a_initial = resp.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

# --- id=280  name='Wallet Transfer Own Address' ---
def test_wallet_transfer_own_address():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    address_a = resp.json()["address"]
    balance_a_initial = resp.json()["balance"]

    transfer_amount = max(1, int(balance_a_initial / 2))
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

# --- id=281  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")

    payload_no_to = {"amount": 10}
    resp = requests.post(transfer_url, headers=headers_a, json=payload_no_to, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    payload_no_amount = {"to": "some_address"}
    resp = requests.post(transfer_url, headers=headers_a, json=payload_no_amount, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=282  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=283  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=284  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=285  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
