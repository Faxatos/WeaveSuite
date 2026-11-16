# Tests generated in iteration 13
# Captured: 2026-07-02T06:25:51
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=585  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    # /user/me
    user_url = get_url("gateway", "/user/me")
    user_resp = requests.get(user_url, timeout=10)
    assert user_resp.status_code == 401, f"Expected 401, got {user_resp.status_code}: {user_resp.text}"

    # /wallet/balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, timeout=10)
    assert balance_resp.status_code == 401, f"Expected 401, got {balance_resp.status_code}: {balance_resp.text}"

    # /wallet/topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, timeout=10)
    assert topup_resp.status_code == 401, f"Expected 401, got {topup_resp.status_code}: {topup_resp.text}"

    # /wallet/transfer
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "some_address", "amount": 10}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=577  name='Auth Signup Login And User Info' ---
def test_auth_signup_login_and_user_info():
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_payload = {"user": username, "password": password}
    signup_resp = requests.post(signup_url, json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_payload = {"user": username, "password": password}
    login_resp = requests.post(login_url, json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json().get("token")
    assert token is not None

    # Get User Info
    user_url = get_url("gateway", "/user/me")
    user_resp = requests.get(user_url, headers=get_auth_headers(token), timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    user_data = user_resp.json()
    assert user_data.get("user") == username
    assert "enabled" in user_data

# --- id=578  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username, password, _ = create_user()

    login_url = get_url("gateway", "/auth/login")
    login_payload = {"user": username, "password": "wrongpassword"}
    login_resp = requests.post(login_url, json=login_payload, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=579  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = get_auth_headers(token)

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert balance_data.get("balance") == 0
    address = balance_data.get("address")
    assert address is not None

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data.get("address") == address
    new_balance = topup_data.get("balance")
    assert new_balance > 0

    # Verify balance
    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json().get("balance") == new_balance

    # Topup again should fail
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=580  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json().get("balance")

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    balance_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json().get("address")
    balance_b_initial = balance_b_resp.json().get("balance")

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A balance in response
    assert transfer_resp.json().get("balance") == balance_a_initial - transfer_amount

    # Verify A balance via GET
    balance_a_resp2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_a_resp2.status_code == 200, f"Expected 200, got {balance_a_resp2.status_code}: {balance_a_resp2.text}"
    assert balance_a_resp2.json().get("balance") == balance_a_initial - transfer_amount

    # Verify B balance via GET
    balance_b_resp2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp2.status_code == 200, f"Expected 200, got {balance_b_resp2.status_code}: {balance_b_resp2.text}"
    assert balance_b_resp2.json().get("balance") == balance_b_initial + transfer_amount

# --- id=581  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    balance_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_b_resp.status_code == 200, f"Expected 200, got {balance_b_resp.status_code}: {balance_b_resp.text}"
    address_b = balance_b_resp.json().get("address")

    # Transfer A -> B (A has 0 balance)
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 10}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=582  name='Wallet Transfer Invalid Address' ---
def test_wallet_transfer_invalid_address():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Transfer to invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "invalid_address_123", "amount": 10}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=583  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    balance_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = balance_b_resp.json().get("address")

    # Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -10}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=584  name='Wallet Transfer Zero Amount And Self' ---
def test_wallet_transfer_zero_amount_and_self():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    balance_a_initial = topup_resp.json().get("balance")
    address_a = topup_resp.json().get("address")

    # Transfer 0 to self
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_a, "amount": 0}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify balance unchanged
    assert transfer_resp.json().get("balance") == balance_a_initial

    # Verify via GET
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_resp.json().get("balance") == balance_a_initial
