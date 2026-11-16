# Tests generated in iteration 02
# Captured: 2026-06-17T01:08:46
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1695  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    assert token

    # Follow-up GET to verify user creation
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Duplicate signup
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1696  name='User Me' ---
def test_user_me():
    username, _, token = register_user()
    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=1697  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["address"] == address
    new_balance = topup_data["balance"]
    assert new_balance > 0

    # Verify balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Topup again (Negative)
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1698  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get addresses
    balance_url = get_url("gateway", "/wallet/balance")
    addr_a = requests.get(balance_url, headers=headers_a, timeout=10).json()["address"]
    addr_b = requests.get(balance_url, headers=headers_b, timeout=10).json()["address"]

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    balance_a = resp.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": addr_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify A balance from transfer response
    expected_balance_a = 0
    assert resp.json()["balance"] == expected_balance_a

    # Verify A balance from follow-up GET
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.json()["balance"] == expected_balance_a

    # Verify B balance from follow-up GET
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.json()["balance"] == transfer_amount

# --- id=1699  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Get address and topup
    balance_url = get_url("gateway", "/wallet/balance")
    addr = requests.get(balance_url, headers=headers, timeout=10).json()["address"]

    topup_url = get_url("gateway", "/wallet/topup")
    balance = requests.get(topup_url, headers=headers, timeout=10).json()["balance"]

    # Transfer to self
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers, json={"to": addr, "amount": balance}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance

    # Verify balance unchanged
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.json()["balance"] == balance

    # Transfer 0 to another user
    _, _, token_b = register_user()
    addr_b = requests.get(balance_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10).json()["address"]

    resp = requests.post(transfer_url, headers=headers, json={"to": addr_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance

    # Verify balance unchanged
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.json()["balance"] == balance

# --- id=1700  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    addr_b = requests.get(balance_url, headers=headers_b, timeout=10).json()["address"]

    # A has 0 balance
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": addr_b, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1701  name='Wallet Transfer Invalid Input' ---
def test_wallet_transfer_invalid_input():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp = requests.post(transfer_url, headers=headers, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative amount
    resp = requests.post(transfer_url, headers=headers, json={"to": "some_address", "amount": -5}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1702  name='Unauthorized Access' ---
def test_unauthorized_access():
    # No token
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
