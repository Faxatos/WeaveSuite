# Tests generated in iteration 05
# Captured: 2026-06-16T03:09:49
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1432  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    assert "address" in data

# --- id=1433  name='Wallet Topup Success And Duplicate Failure' ---
def test_wallet_topup_success_and_duplicate_failure():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    initial_balance = resp.json().get("balance")
    assert initial_balance == 0

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("balance") > 0
    new_balance = topup_data.get("balance")

    # Verify balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance

    # Duplicate topup
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1434  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_before = resp.json().get("balance")

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b_before = resp.json().get("balance")

    # Transfer A -> B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a_before - transfer_amount

    # Verify A's balance with GET
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    assert resp_a.json().get("balance") == balance_a_before - transfer_amount

    # Verify B's balance with GET
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    assert resp_b.json().get("balance") == balance_b_before + transfer_amount

# --- id=1435  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    # Transfer A -> B (A has balance_a, transfer balance_a + 1)
    transfer_amount = balance_a + 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1436  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "someaddress", "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1437  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Transfer to invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1438  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = register_user()
    _, _, token_b = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_before = resp.json().get("balance")

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b_before = resp.json().get("balance")

    # Transfer 0 A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a_before

    # Verify A's balance
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    assert resp_a.json().get("balance") == balance_a_before

    # Verify B's balance
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    assert resp_b.json().get("balance") == balance_b_before

# --- id=1439  name='Wallet Transfer Own Address' ---
def test_wallet_transfer_own_address():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a_before = resp.json().get("balance")

    # Get A's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_a = resp.json().get("address")

    # Transfer A -> A
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a_before

    # Verify A's balance
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    assert resp_a.json().get("balance") == balance_a_before

# --- id=1440  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'amount'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "someaddress"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1427  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = generate_random_string()
    password = generate_random_string()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()
    token = signup_resp.json().get("token")

    # Verify with GET /user/me
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()
    login_token = login_resp.json().get("token")

    # Verify login token works
    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json().get("user") == username

# --- id=1428  name='Auth Signup Missing Fields' ---
def test_auth_signup_missing_fields():
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": "someuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1429  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": "nonexistent", "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=1430  name='User Me' ---
def test_user_get_me():
    username, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=1431  name='Unauthorized Access' ---
def test_unauthorized_access():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
