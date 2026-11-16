# Tests generated in iteration 04
# Captured: 2026-06-14T19:14:11
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=924  name='Auth Signup Success' ---
def test_auth_signup_success():
    user = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    payload = {"user": user, "password": password}
    resp = requests.post(get_url("gateway", "/auth/signup"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == user

# --- id=925  name='Auth Signup Bad Request' ---
def test_auth_signup_bad_request():
    user = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    payload = {"user": user}  # Missing required password
    resp = requests.post(get_url("gateway", "/auth/signup"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=926  name='Auth Login Success' ---
def test_auth_login_success():
    token, user = create_user_and_get_token()
    payload = {"user": user, "password": "password123"}
    resp = requests.post(get_url("gateway", "/auth/login"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    new_token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {new_token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == user

# --- id=927  name='Auth Login Bad Request' ---
def test_auth_login_bad_request():
    token, user = create_user_and_get_token()
    payload = {"user": user, "password": "wrongpassword"}
    resp = requests.post(get_url("gateway", "/auth/login"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=928  name='User Me Success' ---
def test_user_me_success():
    token, user = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data

# --- id=929  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=930  name='Wallet Balance Success' ---
def test_wallet_balance_success():
    token, user = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] == 0

# --- id=931  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=932  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    token, user = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] > 0

    balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json()["balance"] == data["balance"]

# --- id=933  name='Wallet Topup Bad Request' ---
def test_wallet_topup_bad_request():
    token, user = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp1 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"
    assert "message" in resp2.json()

# --- id=934  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=935  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    token_a, user_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, user_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    initial_balance_a = topup_resp.json()["balance"]

    balance_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]
    initial_balance_b = balance_b_resp.json()["balance"]

    transfer_amount = 10
    payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == initial_balance_a - transfer_amount

    verify_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert verify_a.status_code == 200, f"Expected 200, got {verify_a.status_code}: {verify_a.text}"
    assert verify_a.json()["balance"] == initial_balance_a - transfer_amount

    verify_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert verify_b.status_code == 200, f"Expected 200, got {verify_b.status_code}: {verify_b.text}"
    assert verify_b.json()["balance"] == initial_balance_b + transfer_amount

# --- id=936  name='Wallet Transfer Bad Request' ---
def test_wallet_transfer_bad_request():
    token_a, user_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, user_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]

    # Attempt transfer without topup (insufficient funds)
    payload = {"to": address_b, "amount": 100}
    transfer_resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert "message" in transfer_resp.json()

# --- id=937  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    token_b, user_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json()["address"]

    payload = {"to": address_b, "amount": 10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
