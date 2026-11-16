# Tests generated in iteration 10
# Captured: 2026-07-01T12:42:27
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=181  name='Auth Signup And Login' ---
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

# --- id=182  name='User Me' ---
def test_user_get_me():
    username, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert data["user"] == username
    assert "enabled" in data

# --- id=183  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]

    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] > 0
    assert data["address"] == address

    topup_balance = data["balance"]

    resp = requests.get(url_balance, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == topup_balance

    resp = requests.get(url_topup, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=184  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_initial = resp.json()["balance"]

    _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b_initial = resp.json()["balance"]

    transfer_amount = balance_a_initial / 2

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_b_initial + transfer_amount

# --- id=185  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 10}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=186  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -10}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=187  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_address_12345", "amount": 10}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=188  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    balance_a_initial = wallet_a["balance"]
    address_a = wallet_a["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")

    payload = {"to": address_a, "amount": 0}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

# --- id=189  name='Wallet Unauthorized Access' ---
def test_wallet_unauthorized_access():
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
