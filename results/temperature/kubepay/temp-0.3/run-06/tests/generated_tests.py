# Tests generated in iteration 06
# Captured: 2026-07-02T03:34:26
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=510  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username, password, token, headers = create_user_and_get_token()

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

# --- id=511  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "nonexistent", "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=512  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, _, headers = create_user_and_get_token()

    address, initial_balance = get_wallet_info(headers)
    assert initial_balance == 0
    assert address is not None

    new_balance, topup_address = topup_wallet(headers)
    assert new_balance > 0
    assert topup_address == address

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=513  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, _, headers_a = create_user_and_get_token()
    balance_a_initial, address_a = topup_wallet(headers_a)

    _, _, _, headers_b = create_user_and_get_token()
    address_b, balance_b_initial = get_wallet_info(headers_b)

    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial - transfer_amount

    _, balance_a_final = get_wallet_info(headers_a)
    assert balance_a_final == balance_a_initial - transfer_amount

    _, balance_b_final = get_wallet_info(headers_b)
    assert balance_b_final == balance_b_initial + transfer_amount

# --- id=514  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, _, headers_a = create_user_and_get_token()

    _, _, _, headers_b = create_user_and_get_token()
    address_b, _ = get_wallet_info(headers_b)

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 100.0}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=515  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, _, headers_a = create_user_and_get_token()
    topup_wallet(headers_a)

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 10.0}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=516  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, _, headers_a = create_user_and_get_token()
    topup_wallet(headers_a)

    _, _, _, headers_b = create_user_and_get_token()
    address_b, _ = get_wallet_info(headers_b)

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10.0}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=517  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, _, headers_a = create_user_and_get_token()
    balance_a_initial, _ = topup_wallet(headers_a)

    _, _, _, headers_b = create_user_and_get_token()
    address_b, _ = get_wallet_info(headers_b)

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0.0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

    _, balance_a_final = get_wallet_info(headers_a)
    assert balance_a_final == balance_a_initial

# --- id=518  name='Wallet Transfer To Self' ---
def test_wallet_transfer_to_self():
    _, _, _, headers_a = create_user_and_get_token()
    balance_a_initial, address_a = topup_wallet(headers_a)

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10.0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

    _, balance_a_final = get_wallet_info(headers_a)
    assert balance_a_final == balance_a_initial

# --- id=519  name='Auth Unauthorized Access' ---
def test_auth_unauthorized_access():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
