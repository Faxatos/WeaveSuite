# Tests generated in iteration 08
# Captured: 2026-06-16T16:38:26
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1608  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = generate_random_string()
    password = generate_random_string()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json(), "Missing token in signup response"

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json(), "Missing token in login response"

    # Negative: Signup with same username
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Login with wrong password
    resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1609  name='User Me' ---
def test_user_me():
    username, _, token = create_user_and_login()

    headers = {"Authorization": f"Bearer {token}"}
    me_url = get_url("gateway", "/user/me")

    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username, f"Expected user {username}, got {data.get('user')}"
    assert "name" in data, "Missing name in user info"
    assert "enabled" in data, "Missing enabled in user info"

    # Negative: Missing token
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1610  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0, f"Expected initial balance 0, got {data.get('balance')}"
    address = data.get("address")
    assert address is not None, "Missing address in wallet info"

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("address") == address, "Address changed after topup"
    new_balance = topup_data.get("balance")
    assert new_balance > 0, f"Expected balance > 0 after topup, got {new_balance}"

    # Follow-up balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance, "Balance mismatch in follow-up GET"

    # Negative: Topup again
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1611  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")

    # Get addresses
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    address_a = resp_a.json().get("address")

    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_b.json().get("address")

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    balance_a = resp.json().get("balance")

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 10
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    expected_balance_a = balance_a - transfer_amount
    assert transfer_data.get("balance") == expected_balance_a, f"Expected balance {expected_balance_a}, got {transfer_data.get('balance')}"

    # Follow-up A
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.json().get("balance") == expected_balance_a, "Follow-up balance A mismatch"

    # Follow-up B
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.json().get("balance") == transfer_amount, "Follow-up balance B mismatch"

    # Transfer 0 (no-op)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == expected_balance_a, "Balance should not change for 0 amount transfer"

    # Transfer to self (no-op)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == expected_balance_a, "Balance should not change for self transfer"

# --- id=1612  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative: Insufficient funds
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Negative: Negative amount
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -5}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Missing 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Empty 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Recipient not found
    fake_address = "fake_" + generate_random_string(10)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": fake_address, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Unauthorized
    resp = requests.post(transfer_url, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
