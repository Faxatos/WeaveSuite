# Tests generated in iteration 11
# Captured: 2026-07-01T21:19:01
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=369  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{generate_random_string()}"
    password = f"Pass_{generate_random_string()}!"
    payload = {"user": username, "password": password}

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json=payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    signup_token = signup_resp.json().get("token")
    assert signup_token is not None

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json=payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json().get("token")
    assert login_token is not None

    # Verify User Info
    user_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {login_token}"}
    user_resp = requests.get(user_url, headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    user_data = user_resp.json()
    assert user_data.get("user") == username
    assert "name" in user_data
    assert "enabled" in user_data

# --- id=370  name='Auth Login Failure' ---
def test_auth_login_failure():
    payload = {"user": "nonexistent_user", "password": "wrongpassword"}
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=371  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = register_user()

    # Initial balance should be 0
    wallet_info = get_wallet_info(token)
    assert wallet_info.get("balance") == 0
    assert "address" in wallet_info

    # Topup
    topup_info = topup_wallet(token)
    topup_balance = topup_info.get("balance")
    assert topup_balance > 0
    assert topup_info.get("address") == wallet_info.get("address")

    # Verify balance
    updated_wallet_info = get_wallet_info(token)
    assert updated_wallet_info.get("balance") == topup_balance

    # Repeat topup should fail
    topup_url = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}
    repeat_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert repeat_resp.status_code == 400, f"Expected 400, got {repeat_resp.status_code}: {repeat_resp.text}"

# --- id=372  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # Setup User A
    _, _, token_a = register_user()
    topup_info_a = topup_wallet(token_a)
    balance_a_initial = topup_info_a.get("balance")
    address_a = topup_info_a.get("address")

    # Setup User B
    _, _, token_b = register_user()
    wallet_info_b = get_wallet_info(token_b)
    balance_b_initial = wallet_info_b.get("balance")
    address_b = wallet_info_b.get("address")

    # Transfer A -> B
    transfer_amount = 10
    assert balance_a_initial >= transfer_amount, "Insufficient topup balance for test"

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": transfer_amount}

    transfer_resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    transfer_data = transfer_resp.json()
    assert transfer_data.get("balance") == balance_a_initial - transfer_amount
    assert transfer_data.get("address") == address_a

    # Verify User A balance
    final_info_a = get_wallet_info(token_a)
    assert final_info_a.get("balance") == balance_a_initial - transfer_amount

    # Verify User B balance
    final_info_b = get_wallet_info(token_b)
    assert final_info_b.get("balance") == balance_b_initial + transfer_amount

# --- id=373  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # Setup User A without topup (balance 0)
    _, _, token_a = register_user()
    wallet_info_a = get_wallet_info(token_a)
    balance_a_initial = wallet_info_a.get("balance")
    assert balance_a_initial == 0

    # Setup User B
    _, _, token_b = register_user()
    wallet_info_b = get_wallet_info(token_b)
    address_b = wallet_info_b.get("address")

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": 10}

    transfer_resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify User A balance unchanged
    final_info_a = get_wallet_info(token_a)
    assert final_info_a.get("balance") == 0

# --- id=374  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    topup_wallet(token_a)

    _, _, token_b = register_user()
    address_b = get_wallet_info(token_b).get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": -10}

    transfer_resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=375  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = register_user()
    topup_wallet(token_a)

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": "invalid_address_123", "amount": 10}

    transfer_resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=376  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = register_user()
    topup_wallet(token_a)

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Missing 'amount'
    payload_missing_amount = {"to": "some_address"}
    resp1 = requests.post(transfer_url, headers=headers_a, json=payload_missing_amount, timeout=10)
    assert resp1.status_code == 400, f"Expected 400, got {resp1.status_code}: {resp1.text}"

    # Missing 'to'
    payload_missing_to = {"amount": 10}
    resp2 = requests.post(transfer_url, headers=headers_a, json=payload_missing_to, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=377  name='Wallet Transfer Zero Amount No Op' ---
def test_wallet_transfer_zero_amount_no_op():
    _, _, token_a = register_user()
    topup_info_a = topup_wallet(token_a)
    balance_a_initial = topup_info_a.get("balance")

    _, _, token_b = register_user()
    wallet_info_b = get_wallet_info(token_b)
    balance_b_initial = wallet_info_b.get("balance")
    address_b = wallet_info_b.get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": 0}

    transfer_resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify balances unchanged
    final_info_a = get_wallet_info(token_a)
    assert final_info_a.get("balance") == balance_a_initial

    final_info_b = get_wallet_info(token_b)
    assert final_info_b.get("balance") == balance_b_initial

# --- id=378  name='Wallet Unauthorized Access' ---
def test_wallet_unauthorized_access():
    wallet_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(wallet_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=379  name='User Unauthorized Access' ---
def test_user_unauthorized_access():
    user_url = get_url("gateway", "/user/me")
    resp = requests.get(user_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
