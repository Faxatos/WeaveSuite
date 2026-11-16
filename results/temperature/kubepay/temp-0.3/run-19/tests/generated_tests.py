# Tests generated in iteration 19
# Captured: 2026-07-02T08:43:56
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=626  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    token = resp.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] == 0

# --- id=627  name='Wallet Topup' ---
def test_wallet_topup():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] > 0
    new_balance = data["balance"]

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

# --- id=628  name='Wallet Topup Duplicate' ---
def test_wallet_topup_duplicate():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=629  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp.json()["balance"]

    user_b = f"user_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]
    balance_b_initial = resp.json()["balance"]

    transfer_amount = 10
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.json()["balance"] == balance_b_initial + transfer_amount

# --- id=630  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = f"user_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    transfer_amount = 10
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=631  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": "dummy_address", "amount": -5}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=632  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=633  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    address_a = resp.json()["address"]
    balance_a_initial = resp.json()["balance"]

    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

# --- id=634  name='Unauthorized Access' ---
def test_unauthorized_access():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=624  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == user

    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token2 = resp.json().get("token")
    assert token2 is not None

# --- id=625  name='Auth Signup Duplicate' ---
def test_auth_signup_duplicate():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()
