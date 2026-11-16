# Tests generated in iteration 12
# Captured: 2026-07-01T13:25:44
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=195  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "Password123!"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    signup_data = signup_resp.json()
    assert "token" in signup_data

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_data = login_resp.json()
    assert "token" in login_data

    # Follow up: verify user info
    token = login_data["token"]
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data.get("user") == username

# --- id=196  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": "nonexistent_user", "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=197  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert balance_data.get("balance") == 0
    assert "address" in balance_data

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    new_balance = topup_data.get("balance")
    assert new_balance > 0

    # Follow up: verify balance
    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json().get("balance") == new_balance

# --- id=198  name='Wallet Topup Repetition Conflict' ---
def test_wallet_topup_repetition_conflict():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    # Second topup should fail
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=199  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json().get("balance")
    assert balance_a_initial >= 1, "Topup did not provide enough balance for transfer"

    # Get B's address and balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json().get("address")
    balance_b_initial = balance_resp_b.json().get("balance")

    # Transfer from A to B
    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    transfer_data = transfer_resp.json()
    assert transfer_data.get("balance") == balance_a_initial - transfer_amount

    # Follow up: Verify A's balance
    balance_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json().get("balance") == balance_a_initial - transfer_amount

    # Follow up: Verify B's balance
    balance_resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_resp_b2.status_code == 200, f"Expected 200, got {balance_resp_b2.status_code}: {balance_resp_b2.text}"
    assert balance_resp_b2.json().get("balance") == balance_b_initial + transfer_amount

# --- id=200  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json().get("address")

    # Transfer from A to B without topup (A has 0 balance)
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=201  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Transfer to invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 1}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=202  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    # Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=203  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user_and_get_token()
    _, _, token_b = create_user_and_get_token()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get A's balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    balance_a_initial = balance_resp_a.json().get("balance")

    # Get B's address and balance
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")
    balance_b_initial = balance_resp_b.json().get("balance")

    # Transfer zero amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow up: check balances unchanged
    balance_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_resp_a2.json().get("balance") == balance_a_initial

    balance_resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_resp_b2.json().get("balance") == balance_b_initial

# --- id=204  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, timeout=10)
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"
