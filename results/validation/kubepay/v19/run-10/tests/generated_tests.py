# Tests generated in iteration 10
# Captured: 2026-06-15T19:12:14
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1300  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    session = requests.Session()
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = session.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    signup_data = resp.json()
    assert "token" in signup_data, "Expected token in signup response"
    signup_token = signup_data["token"]

    # Follow-up GET
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {signup_token}"}
    resp = session.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = session.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_data = resp.json()
    assert "token" in login_data, "Expected token in login response"
    login_token = login_data["token"]

    # Follow-up GET
    headers = {"Authorization": f"Bearer {login_token}"}
    resp = session.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("user") == username

# --- id=1301  name='Auth Negative Scenarios' ---
def test_auth_negative_scenarios():
    session = requests.Session()

    # Signup missing password
    signup_url = get_url("gateway", "/auth/signup")
    resp = session.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Login with non-existent user
    login_url = get_url("gateway", "/auth/login")
    resp = session.post(login_url, json={"user": "nonexistent", "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Access /user/me without token
    me_url = get_url("gateway", "/user/me")
    resp = session.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Access /wallet/balance without token
    balance_url = get_url("gateway", "/wallet/balance")
    resp = session.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Access /wallet/topup without token
    topup_url = get_url("gateway", "/wallet/topup")
    resp = session.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1302  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    session = requests.Session()
    _, _, token = create_user(session)
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = session.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_data = resp.json()
    assert balance_data.get("balance") == 0, "Expected initial balance to be 0"
    address = balance_data.get("address")
    assert address is not None, "Expected address in balance response"

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = session.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("address") == address, "Address should not change"
    topup_balance = topup_data.get("balance")
    assert topup_balance > 0, "Expected balance > 0 after topup"

    # Verify balance updated
    resp = session.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == topup_balance, "Balance should match topup amount"

    # Topup again should fail
    resp = session.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1303  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    session = requests.Session()

    # User A
    _, _, token_a = create_user(session)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user(session)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = session.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Topup User A
    balance_url = get_url("gateway", "/wallet/balance")
    resp = session.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")
    address_a = resp.json().get("address")
    assert balance_a > 0, "User A balance should be > 0 after topup"

    # Get User B address and balance
    resp = session.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b = resp.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = session.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    assert transfer_data.get("balance") == balance_a - transfer_amount, "User A balance should decrease by transfer amount"

    # Verify User A balance via GET
    resp = session.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount, "User A balance should decrease by transfer amount"

    # Verify User B balance via GET
    resp = session.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == transfer_amount, "User B balance should increase by transfer amount"

    # Transfer 0 A -> B
    resp = session.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify User A balance via GET
    resp = session.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount, "User A balance should remain unchanged"

    # Transfer to self A -> A
    resp = session.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": transfer_amount / 2.0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify User A balance via GET
    resp = session.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount, "User A balance should remain unchanged when transferring to self"

# --- id=1304  name='Wallet Transfer Negative' ---
def test_wallet_transfer_negative():
    session = requests.Session()

    # User A
    _, _, token_a = create_user(session)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user(session)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = session.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Topup User A
    balance_url = get_url("gateway", "/wallet/balance")
    resp = session.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_a = resp.json().get("address")

    # Get User B address
    resp = session.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # User B tries to transfer to User A (insufficient funds)
    resp = session.post(transfer_url, headers=headers_b, json={"to": address_a, "amount": 100}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # User A tries to transfer to non-existent address
    resp = session.post(transfer_url, headers=headers_a, json={"to": "invalid_address", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # User A tries to transfer negative amount
    resp = session.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # User A tries to transfer missing 'to'
    resp = session.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Unauthorized transfer
    resp = session.post(transfer_url, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
