# Tests generated in iteration 07
# Captured: 2026-06-16T23:04:25
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1663  name='Gateway Auth Workflow' ---
def test_gateway_auth_workflow():
    # 1. Signup
    username, password, token, headers = register_user()

    # 2. Signup with existing user (Conflict/Repetition)
    resp_conflict = requests.post(
        get_url("gateway", "/auth/signup"), 
        json={"user": username, "password": password}, 
        timeout=10
    )
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"

    # 3. Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"), 
        json={"user": username, "password": password}, 
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

    # Follow-up GET for login
    login_headers = {"Authorization": f"Bearer {login_token}"}
    me_resp = requests.get(get_url("gateway", "/user/me"), headers=login_headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

    # 4. Login with wrong password
    resp_bad_login = requests.post(
        get_url("gateway", "/auth/login"), 
        json={"user": username, "password": "wrongpassword"}, 
        timeout=10
    )
    assert resp_bad_login.status_code == 400, f"Expected 400, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=1664  name='Gateway Wallet Topup Workflow' ---
def test_gateway_wallet_topup_workflow():
    _, _, _, headers = register_user()

    # Initial balance should be 0
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json().get("balance") == 0
    address = bal_resp.json().get("address")
    assert address is not None

    # Topup
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    new_balance = topup_resp.json().get("balance")
    assert new_balance > 0
    assert topup_resp.json().get("address") == address

    # Follow-up GET to verify balance
    bal_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json().get("balance") == new_balance

    # Topup again (should fail as it is a one-time operation)
    topup_resp2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=1665  name='Gateway Wallet Transfer Workflow' ---
def test_gateway_wallet_transfer_workflow():
    # Setup User A
    _, _, _, headers_a = register_user()
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json().get("balance")

    # Setup User B
    _, _, _, headers_b = register_user()
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")
    balance_b = bal_resp_b.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    expected_balance_a = balance_a - transfer_amount
    assert transfer_resp.json().get("balance") == expected_balance_a

    # Follow-up GET for A
    bal_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json().get("balance") == expected_balance_a

    # Follow-up GET for B
    bal_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200, f"Expected 200, got {bal_resp_b2.status_code}: {bal_resp_b2.text}"
    assert bal_resp_b2.json().get("balance") == transfer_amount

    # Transfer A -> A (amount 0, no-op)
    bal_resp_a_info = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    address_a = bal_resp_a_info.json().get("address")

    transfer_noop = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 0},
        timeout=10
    )
    assert transfer_noop.status_code == 200, f"Expected 200, got {transfer_noop.status_code}: {transfer_noop.text}"
    assert transfer_noop.json().get("balance") == expected_balance_a

    # Follow-up GET for no-op transfer
    bal_resp_a3 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a3.status_code == 200, f"Expected 200, got {bal_resp_a3.status_code}: {bal_resp_a3.text}"
    assert bal_resp_a3.json().get("balance") == expected_balance_a

# --- id=1666  name='Gateway Wallet Transfer Errors' ---
def test_gateway_wallet_transfer_errors():
    # Setup User A
    _, _, _, headers_a = register_user()
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json().get("balance")

    # Setup User B
    _, _, _, headers_b = register_user()
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")

    # 1. Insufficient funds
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance_a + 100},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # 2. Negative amount
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # 3. Invalid recipient address
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # 4. Missing 'amount'
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # 5. Missing 'to'
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=1667  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    # Missing token
    headers = {}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers,
        json={"to": "some_address", "amount": 10},
        timeout=10
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token_123"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
