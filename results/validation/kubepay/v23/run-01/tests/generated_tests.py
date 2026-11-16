# Tests generated in iteration 01
# Captured: 2026-06-16T13:53:10
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1546  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Follow-up GET to verify user creation
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=1547  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{generate_random_string()}"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1548  name='Auth Login Invalid User' ---
def test_auth_login_invalid_user():
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1549  name='User Me Success' ---
def test_user_me_success():
    username, _, token = create_user()
    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=1550  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1551  name='Wallet Balance Initial Zero' ---
def test_wallet_balance_initial_zero():
    _, _, token = create_user()
    url = get_url("gateway", "/wallet/balance")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    assert "address" in data

# --- id=1552  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1553  name='Wallet Topup Success And Duplicate Fails' ---
def test_wallet_topup_success_and_duplicate_fails():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") > 0
    new_balance = data.get("balance")

    # Verify balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json().get("balance") == new_balance

    # Duplicate topup fails
    resp3 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp3.status_code == 400, f"Expected 400, got {resp3.status_code}: {resp3.text}"

# --- id=1554  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json().get("balance")

    # User B
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json().get("address")
    balance_b_initial = resp_b.json().get("balance")

    # Transfer A -> B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance decreased
    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json().get("balance") == balance_a_initial - transfer_amount

    # Verify B balance increased
    resp_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_after.status_code == 200, f"Expected 200, got {resp_b_after.status_code}: {resp_b_after.text}"
    assert resp_b_after.json().get("balance") == balance_b_initial + transfer_amount

# --- id=1555  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A (no topup, balance 0)
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json().get("address")

    # Transfer A -> B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance unchanged
    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json().get("balance") == 0

# --- id=1556  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json().get("balance")

    # User B
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json().get("address")

    # Transfer A -> B with negative amount
    transfer_amount = -10
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance unchanged
    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json().get("balance") == balance_a_initial

# --- id=1557  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json().get("balance")

    # Transfer A -> B with missing 'to'
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json().get("balance") == balance_a_initial

# --- id=1558  name='Wallet Transfer Recipient Not Found' ---
def test_wallet_transfer_recipient_not_found():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json().get("balance")

    # Transfer A -> non-existent address
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": "non_existent_address_12345", "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json().get("balance") == balance_a_initial

# --- id=1559  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json().get("balance")
    address_a = resp_topup.json().get("address")

    # Transfer A -> A (self transfer)
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json().get("balance") == balance_a_initial
