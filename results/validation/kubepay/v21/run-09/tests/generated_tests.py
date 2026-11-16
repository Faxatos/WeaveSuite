# Tests generated in iteration 09
# Captured: 2026-06-16T04:47:08
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1464  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Verify user creation via /user/me
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers=get_auth_headers(token), timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=1465  name='Auth Signup Duplicate User' ---
def test_auth_signup_duplicate_user():
    username, password, _ = create_user_and_get_token()
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1466  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "nonexistent", "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1467  name='User Me Success' ---
def test_user_me_success():
    username, _, token = create_user_and_get_token()
    headers = get_auth_headers(token)

    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert isinstance(data.get("enabled"), bool)

# --- id=1468  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1469  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user_and_get_token()
    headers = get_auth_headers(token)

    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    assert isinstance(data.get("address"), str)
    assert len(data.get("address")) > 0

# --- id=1470  name='Wallet Topup Success And Duplicate Failure' ---
def test_wallet_topup_success_and_duplicate_failure():
    _, _, token = create_user_and_get_token()
    headers = get_auth_headers(token)

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("balance") > 0

    # Verify balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json().get("balance") == topup_data.get("balance")

    # Duplicate topup
    resp3 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp3.status_code == 400, f"Expected 400, got {resp3.status_code}: {resp3.text}"

# --- id=1471  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User 1
    _, _, token1 = create_user_and_get_token()
    headers1 = get_auth_headers(token1)

    # Topup User 1
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers1, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    initial_balance1 = resp.json().get("balance")

    # User 2
    _, _, token2 = create_user_and_get_token()
    headers2 = get_auth_headers(token2)

    # Get User 2 address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers2, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address2 = resp.json().get("address")
    initial_balance2 = resp.json().get("balance")
    assert initial_balance2 == 0

    # Transfer
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers1, json={"to": address2, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance1 - transfer_amount

    # Verify User 1 balance
    resp = requests.get(balance_url, headers=headers1, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance1 - transfer_amount

    # Verify User 2 balance
    resp = requests.get(balance_url, headers=headers2, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == transfer_amount

# --- id=1472  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token1 = create_user_and_get_token()
    headers1 = get_auth_headers(token1)

    _, _, token2 = create_user_and_get_token()
    headers2 = get_auth_headers(token2)

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers2, timeout=10)
    address2 = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers1, json={"to": address2, "amount": 100}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1473  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token1 = create_user_and_get_token()
    headers1 = get_auth_headers(token1)

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers1, timeout=10)

    _, _, token2 = create_user_and_get_token()
    headers2 = get_auth_headers(token2)

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers2, timeout=10)
    address2 = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers1, json={"to": address2, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1474  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token1 = create_user_and_get_token()
    headers1 = get_auth_headers(token1)

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers1, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers1, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1475  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token1 = create_user_and_get_token()
    headers1 = get_auth_headers(token1)

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers1, timeout=10)

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers1, timeout=10)
    address1 = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp = requests.post(transfer_url, headers=headers1, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'amount'
    resp = requests.post(transfer_url, headers=headers1, json={"to": address1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1476  name='Wallet Transfer Zero And Self' ---
def test_wallet_transfer_zero_and_self():
    _, _, token1 = create_user_and_get_token()
    headers1 = get_auth_headers(token1)

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers1, timeout=10)
    initial_balance = resp.json().get("balance")

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers1, timeout=10)
    address1 = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer to self
    resp = requests.post(transfer_url, headers=headers1, json={"to": address1, "amount": 10}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance

    # Transfer zero
    resp = requests.post(transfer_url, headers=headers1, json={"to": address1, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == initial_balance

# --- id=1477  name='Wallet Unauthorized' ---
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
