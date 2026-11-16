# Tests generated in iteration 08
# Captured: 2026-06-15T18:32:47
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1291  name='Auth Signup Login User Info' ---
def test_auth_signup_login_user_info():
    username = f"user_{generate_string()}"
    password = generate_string()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token, "Token missing in signup response"

    # Login (Follow-up to verify signup)
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token, "Token missing in login response"

    # Get User Info (Follow-up to verify user state)
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {login_token}"}
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info.get("user") == username
    assert "name" in user_info
    assert "enabled" in user_info

# --- id=1292  name='Wallet Topup And Transfer' ---
def test_wallet_topup_and_transfer():
    user_a, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")

    # Get User A initial balance
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    assert wallet_a.get("balance") == 0
    address_a = wallet_a.get("address")
    assert address_a

    # Get User B initial balance
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_b = resp.json()
    assert wallet_b.get("balance") == 0
    address_b = wallet_b.get("address")
    assert address_b

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_wallet_a = resp.json()
    assert topup_wallet_a.get("address") == address_a
    topup_balance_a = topup_wallet_a.get("balance")
    assert topup_balance_a > 0

    # Verify Topup with follow-up GET
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == topup_balance_a

    # Transfer from A to B
    transfer_amount = topup_balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_wallet_a = resp.json()
    expected_balance_a = topup_balance_a - transfer_amount
    assert transfer_wallet_a.get("balance") == expected_balance_a

    # Verify Transfer with follow-up GET for A
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == expected_balance_a

    # Verify Transfer with follow-up GET for B
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == transfer_amount

# --- id=1293  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    user_a, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    address_a = wallet_a.get("address")

    # Transfer to own address with 0 amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": address_a, "amount": 0}, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0

    # Verify balance remains 0
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0

# --- id=1294  name='Wallet Negative Scenarios' ---
def test_wallet_negative_scenarios():
    user_a, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    # Topup again -> 400
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Transfer to invalid address -> 400
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "invalid_address", "amount": 1}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Transfer negative amount -> 400
    user_b, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    resp = requests.post(transfer_url, json={"to": address_b, "amount": -10}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Transfer more than balance -> 400
    resp = requests.post(transfer_url, json={"to": address_b, "amount": balance_a + 1000}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Transfer missing fields -> 400
    resp = requests.post(transfer_url, json={"amount": 10}, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1295  name='Auth And Unauthorized Negative Scenarios' ---
def test_auth_and_unauthorized_negative_scenarios():
    # Signup missing password -> 400
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": f"user_{generate_string()}"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Login invalid user -> 400
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "nonexistent", "password": "pwd"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Unauthorized access to protected endpoints -> 401
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
