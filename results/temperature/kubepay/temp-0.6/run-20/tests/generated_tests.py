# Tests generated in iteration 20
# Captured: 2026-07-03T06:04:47
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=988  name='Auth Signup And Login Successful' ---
def test_auth_signup_and_login_successful():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    assert token

    # Verify Me
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    me_data = resp_me.json()
    assert me_data["user"] == user
    assert "name" in me_data
    assert "enabled" in me_data

# --- id=989  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "nonexistent_user", "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=990  name='Auth Signup Missing Fields' ---
def test_auth_signup_missing_fields():
    signup_url = get_url("gateway", "/auth/signup")
    # Missing required 'password' field
    resp = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=991  name='Wallet Balance And Topup Successful' ---
def test_wallet_balance_and_topup_successful():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    bal_data = resp_bal.json()
    assert bal_data["balance"] == 0
    assert "address" in bal_data

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == bal_data["address"]
    new_balance = topup_data["balance"]

    # Verify balance
    resp_bal_after = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal_after.status_code == 200, f"Expected 200, got {resp_bal_after.status_code}: {resp_bal_after.text}"
    assert resp_bal_after.json()["balance"] == new_balance
    assert resp_bal_after.json()["address"] == bal_data["address"]

# --- id=992  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup1 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    # Second topup should fail
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json()

# --- id=993  name='Wallet Transfer Successful' ---
def test_wallet_transfer_successful():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]

    # Get user B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b_initial = resp_bal_b.json()["balance"]

    # Transfer from A to B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": address_b, "amount": transfer_amount}, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_data = resp_transfer.json()
    assert transfer_data["balance"] == balance_a_initial - transfer_amount

    # Verify user B balance
    resp_bal_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b_after.status_code == 200, f"Expected 200, got {resp_bal_b_after.status_code}: {resp_bal_b_after.text}"
    assert resp_bal_b_after.json()["balance"] == balance_b_initial + transfer_amount

# --- id=994  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get user B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    # Transfer from A to B (A has 0 balance)
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": address_b, "amount": 10}, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=995  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"

    # Transfer from A to invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": "invalid_address_123", "amount": 10}, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=996  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    # Missing amount
    resp_transfer1 = requests.post(transfer_url, json={"to": "some_address"}, headers=headers_a, timeout=10)
    assert resp_transfer1.status_code == 400, f"Expected 400, got {resp_transfer1.status_code}: {resp_transfer1.text}"
    assert "message" in resp_transfer1.json()

    # Missing to
    resp_transfer2 = requests.post(transfer_url, json={"amount": 10}, headers=headers_a, timeout=10)
    assert resp_transfer2.status_code == 400, f"Expected 400, got {resp_transfer2.status_code}: {resp_transfer2.text}"
    assert "message" in resp_transfer2.json()

# --- id=997  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get user B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": address_b, "amount": -10}, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=998  name='Wallet Transfer Zero Noop' ---
def test_wallet_transfer_zero_noop():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup user A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200
    balance_a_initial = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    # Transfer 0 to self
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": address_a, "amount": 0}, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial

    # Verify balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200
    assert resp_bal_a.json()["balance"] == balance_a_initial

# --- id=999  name='Unauthorized Access' ---
def test_unauthorized_access():
    endpoints = [
        ("GET", "/user/me"),
        ("GET", "/wallet/balance"),
        ("GET", "/wallet/topup"),
        ("POST", "/wallet/transfer")
    ]

    for method, path in endpoints:
        url = get_url("gateway", path)
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json={"to": "addr", "amount": 10}, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {path}, got {resp.status_code}: {resp.text}"
        assert not resp.text.strip(), f"Expected empty response body for 401 on {path}"
