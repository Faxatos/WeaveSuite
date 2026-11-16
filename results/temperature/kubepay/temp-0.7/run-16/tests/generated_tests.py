# Tests generated in iteration 16
# Captured: 2026-07-01T23:20:46
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=420  name='Auth Duplicate Signup' ---
def test_auth_duplicate_signup():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Duplicate signup
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=418  name='Auth And User Info' ---
def test_auth_and_user_info():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token, "Token should not be empty"

    # Follow-up GET: User Info
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info.get("user") == username
    assert "name" in user_info
    assert "enabled" in user_info

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token, "Token should not be empty"

# --- id=419  name='Auth Negative' ---
def test_auth_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    signup_url = get_url("gateway", "/auth/signup")

    # Missing password
    resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Create valid user for login test
    password = "ValidPassword1!"
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Invalid login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=421  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert wallet_info["balance"] == 0
    address = wallet_info["address"]
    assert address, "Wallet address should not be empty"

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    assert topup_info["address"] == address
    new_balance = topup_info["balance"]
    assert new_balance > 0

    # Verify balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Topup again -> 400 (only once per wallet)
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=422  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # Setup User 1
    u1 = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": u1, "password": "pwd"}, timeout=10)
    assert resp.status_code == 200
    h1 = {"Authorization": f"Bearer {resp.json()['token']}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=h1, timeout=10)
    assert resp.status_code == 200
    b1_initial = resp.json()["balance"]

    # Setup User 2
    u2 = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": u2, "password": "pwd"}, timeout=10)
    assert resp.status_code == 200
    h2 = {"Authorization": f"Bearer {resp.json()['token']}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=h2, timeout=10)
    assert resp.status_code == 200
    addr2 = resp.json()["address"]

    # Transfer u1 -> u2
    transfer_amount = b1_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=h1, json={"to": addr2, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == b1_initial - transfer_amount

    # Verify u1 balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=h1, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == b1_initial - transfer_amount

    # Verify u2 balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=h2, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == transfer_amount

# --- id=423  name='Wallet Transfer Negative' ---
def test_wallet_transfer_negative():
    # Setup User 1 (no topup, balance 0)
    u1 = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": u1, "password": "pwd"}, timeout=10)
    assert resp.status_code == 200
    h1 = {"Authorization": f"Bearer {resp.json()['token']}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=h1, timeout=10)
    assert resp.status_code == 200
    addr1 = resp.json()["address"]

    # Setup User 2
    u2 = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": u2, "password": "pwd"}, timeout=10)
    assert resp.status_code == 200
    h2 = {"Authorization": f"Bearer {resp.json()['token']}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=h2, timeout=10)
    assert resp.status_code == 200
    addr2 = resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Insufficient funds
    resp = requests.post(transfer_url, headers=h1, json={"to": addr2, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative amount
    resp = requests.post(transfer_url, headers=h1, json={"to": addr2, "amount": -5}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'to'
    resp = requests.post(transfer_url, headers=h1, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Recipient not found
    fake_addr = "fake_address_" + uuid.uuid4().hex
    resp = requests.post(transfer_url, headers=h1, json={"to": fake_addr, "amount": 0}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Transfer to self -> 200 no-op
    resp = requests.post(transfer_url, headers=h1, json={"to": addr1, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == 0

    # Verify balances unchanged
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=h1, timeout=10)
    assert resp.status_code == 200
    assert resp.json()["balance"] == 0

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=h2, timeout=10)
    assert resp.status_code == 200
    assert resp.json()["balance"] == 0

# --- id=424  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
