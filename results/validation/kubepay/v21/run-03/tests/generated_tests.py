# Tests generated in iteration 03
# Captured: 2026-06-16T02:20:07
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1407  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"
    payload = {"user": username, "password": password}

    # Signup
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json=payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json().get("token")
    assert token is not None

    # Follow-up GET to verify user creation
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    # Login
    resp_login = requests.post(get_url("gateway", "/auth/login"), json=payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=1408  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{generate_random_string()}"
    payload = {"user": username} # Missing password
    resp = requests.post(get_url("gateway", "/auth/signup"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1409  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"
    payload = {"user": username, "password": password}
    resp = requests.post(get_url("gateway", "/auth/login"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1410  name='User Me Success' ---
def test_user_get_me_success():
    username, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=1411  name='User Me Unauthorized' ---
def test_user_get_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1412  name='Wallet Balance And Topup Success' ---
def test_wallet_balance_and_topup_success():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    resp_balance = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    data_balance = resp_balance.json()
    assert data_balance.get("balance") == 0
    address = data_balance.get("address")
    assert address is not None

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup.get("address") == address
    new_balance = data_topup.get("balance")
    assert new_balance > 0

    # Verify balance updated
    resp_balance_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_balance_after.status_code == 200, f"Expected 200, got {resp_balance_after.status_code}: {resp_balance_after.text}"
    assert resp_balance_after.json().get("balance") == new_balance

# --- id=1413  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    resp_topup1 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    # Second topup
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json()

# --- id=1414  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup user A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json().get("balance")

    # Get user B address and balance
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")
    balance_b_initial = resp_balance_b.json().get("balance")

    # Transfer from A to B
    transfer_amount = balance_a_initial / 2
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's balance decreased in response
    balance_a_after = resp_transfer.json().get("balance")
    assert balance_a_after == balance_a_initial - transfer_amount

    # Follow-up GET on A's balance
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json().get("balance") == balance_a_after

    # Verify B's balance increased
    resp_balance_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b_after.status_code == 200, f"Expected 200, got {resp_balance_b_after.status_code}: {resp_balance_b_after.text}"
    balance_b_after = resp_balance_b_after.json().get("balance")
    assert balance_b_after == balance_b_initial + transfer_amount

# --- id=1415  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get user B address
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json().get("address")

    # Transfer from A to B without topup (balance 0)
    payload = {"to": address_b, "amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1416  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup user A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Transfer to invalid address
    payload = {"to": "invalid_address_123", "amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1417  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup user A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Get user B address
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_balance_b.json().get("address")

    # Transfer negative amount
    payload = {"to": address_b, "amount": -10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1418  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup user A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Transfer missing 'to'
    payload_missing_to = {"amount": 10}
    resp_transfer_1 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_missing_to, timeout=10)
    assert resp_transfer_1.status_code == 400, f"Expected 400, got {resp_transfer_1.status_code}: {resp_transfer_1.text}"

    # Transfer missing 'amount'
    payload_missing_amount = {"to": "some_address"}
    resp_transfer_2 = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload_missing_amount, timeout=10)
    assert resp_transfer_2.status_code == 400, f"Expected 400, got {resp_transfer_2.status_code}: {resp_transfer_2.text}"

# --- id=1419  name='Wallet Transfer Zero Amount Noop' ---
def test_wallet_transfer_zero_amount_noop():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup user A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup_a.json().get("balance")

    # Get user B address
    resp_balance_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_balance_b.json().get("address")
    balance_b_initial = resp_balance_b.json().get("balance")

    # Transfer zero amount
    payload = {"to": address_b, "amount": 0}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's balance unchanged in response
    balance_a_after = resp_transfer.json().get("balance")
    assert balance_a_after == balance_a_initial

    # Follow-up GET on A's balance
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json().get("balance") == balance_a_initial

    # Verify B's balance unchanged
    resp_balance_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    balance_b_after = resp_balance_b_after.json().get("balance")
    assert balance_b_after == balance_b_initial

# --- id=1420  name='Wallet Transfer To Self Noop' ---
def test_wallet_transfer_to_self_noop():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup user A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp_topup_a.json().get("balance")
    address_a = resp_topup_a.json().get("address")

    # Transfer to self
    payload = {"to": address_a, "amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's balance unchanged in response
    balance_a_after = resp_transfer.json().get("balance")
    assert balance_a_after == balance_a_initial

    # Follow-up GET on A's balance
    resp_balance_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_balance_a_after.status_code == 200, f"Expected 200, got {resp_balance_a_after.status_code}: {resp_balance_a_after.text}"
    assert resp_balance_a_after.json().get("balance") == balance_a_initial
