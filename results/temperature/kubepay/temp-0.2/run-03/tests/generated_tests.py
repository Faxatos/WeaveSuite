# Tests generated in iteration 03
# Captured: 2026-06-22T09:54:49
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=235  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = generate_random_string()
    password = generate_random_string()
    payload = {"user": username, "password": password}

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Follow-up GET for signup
    me_url = get_url("gateway", "/user/me")
    me_resp1 = requests.get(me_url, headers={"Authorization": f"Bearer {resp.json().get('token')}"}, timeout=10)
    assert me_resp1.status_code == 200, f"Expected 200, got {me_resp1.status_code}: {me_resp1.text}"
    assert me_resp1.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json=payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json().get("token")
    assert token is not None

    # Follow-up GET for login
    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json().get("user") == username

# --- id=236  name='Auth Invalid Login' ---
def test_auth_invalid_login():
    username, password, _ = create_user_and_get_token()

    login_url = get_url("gateway", "/auth/login")
    payload = {"user": username, "password": "wrongpassword"}
    login_resp = requests.post(login_url, json=payload, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=237  name='Auth Missing Fields' ---
def test_auth_missing_fields():
    signup_url = get_url("gateway", "/auth/signup")
    payload = {"user": generate_random_string()} # missing password
    resp = requests.post(signup_url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=238  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data.get("balance") == 0
    address = bal_data.get("address")
    assert address is not None

    # Topup
    new_balance, topup_address = topup_wallet(token)
    assert new_balance > 0
    assert topup_address == address

    # Topup again (conflict/repetition)
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=239  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_a_initial, address_a = topup_wallet(token_a)

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")
    balance_b_initial = bal_resp_b.json().get("balance")

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A balance
    bal_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json().get("balance") == pytest.approx(balance_a_initial - transfer_amount)

    # Verify B balance
    bal_resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200, f"Expected 200, got {bal_resp_b2.status_code}: {bal_resp_b2.text}"
    assert bal_resp_b2.json().get("balance") == pytest.approx(balance_b_initial + transfer_amount)

# --- id=240  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_a_initial, _ = topup_wallet(token_a)

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")

    # Transfer A -> B with amount > balance
    transfer_amount = balance_a_initial + 100.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=241  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_wallet(token_a)

    # Transfer A -> invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "invalid_address_123", "amount": 10.0}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=242  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")

    # Transfer A -> B with negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -50.0}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=243  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_a_initial, _ = topup_wallet(token_a)

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")

    # Transfer A -> B with 0 amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 0}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A balance unchanged
    bal_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json().get("balance") == balance_a_initial

# --- id=244  name='Wallet Transfer Self' ---
def test_wallet_transfer_self():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    balance_a_initial, address_a = topup_wallet(token_a)

    # Transfer A -> A with some amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_a, "amount": 10.0}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json().get("balance") == balance_a_initial

# --- id=245  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    # User me
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, timeout=10)
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"

    # Wallet balance
    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(balance_url, timeout=10)
    assert bal_resp.status_code == 401, f"Expected 401, got {bal_resp.status_code}: {bal_resp.text}"
