# Tests generated in iteration 01
# Captured: 2026-06-21T19:28:54
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1  name='Auth Signup And Login' ---
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
    assert "token" in resp.json()

# --- id=2  name='Auth Negative Missing Password' ---
def test_auth_negative_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=3  name='User Me' ---
def test_user_me():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    token = resp.json()["token"]

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=4  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=5  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=6  name='Wallet Transfer' ---
def test_wallet_transfer():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b = resp.json()["balance"]

    transfer_amount = balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.json()["balance"] == balance_a - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.json()["balance"] == balance_b + transfer_amount

# --- id=7  name='Wallet Transfer Negative' ---
def test_wallet_transfer_negative():
    token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a + 100}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a
