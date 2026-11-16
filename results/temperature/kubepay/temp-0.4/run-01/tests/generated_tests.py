# Tests generated in iteration 01
# Captured: 2026-07-01T08:27:00
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=85  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user_data = generate_user()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token, "Expected token in signup response"

    # Verify via /user/me
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == user_data["user"], "User mismatch"

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json=user_data, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json().get("token")
    assert login_token, "Expected token in login response"

    # Negative Login (wrong password)
    bad_user_data = user_data.copy()
    bad_user_data["password"] = "wrongpass"
    bad_login_resp = requests.post(login_url, json=bad_user_data, timeout=10)
    assert bad_login_resp.status_code == 400, f"Expected 400, got {bad_login_resp.status_code}: {bad_login_resp.text}"

# --- id=86  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=87  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    user_data = generate_user()
    token = signup(user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    bal_data = bal_resp.json()
    assert bal_data.get("balance") == 0, "Initial balance should be 0"
    address = bal_data.get("address")
    assert address, "Expected address in balance response"

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    new_balance = topup_data.get("balance")
    assert new_balance > 0, "Balance should be greater than 0 after topup"
    assert topup_data.get("address") == address, "Address should not change"

    # Verify balance
    bal_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json().get("balance") == new_balance, "Balance mismatch after topup"

    # Negative: Topup again
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=88  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a = topup_resp_a.json().get("balance")

    # User B
    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json().get("address")
    balance_b = bal_resp_b.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = 1 if balance_a >= 1 else balance_a / 2.0
    if transfer_amount == 0:
        pytest.skip("Topup resulted in 0 balance, cannot test transfer")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A's balance decreased
    expected_balance_a = balance_a - transfer_amount
    bal_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200
    assert bal_resp_a2.json().get("balance") == expected_balance_a, "User A balance not updated correctly"

    # Verify B's balance increased
    expected_balance_b = balance_b + transfer_amount
    bal_resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200
    assert bal_resp_b2.json().get("balance") == expected_balance_b, "User B balance not updated correctly"

# --- id=89  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp_a.status_code == 200
    balance_a = topup_resp_a.json().get("balance")

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = bal_resp_b.json().get("address")

    transfer_amount = balance_a + 100
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A's balance unchanged
    bal_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a2.json().get("balance") == balance_a

# --- id=90  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = bal_resp_b.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -10}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=91  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "invalid_address_123", "amount": 1}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, headers=headers_a, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=92  name='Wallet Transfer No Op' ---
def test_wallet_transfer_no_op():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200
    balance_a = topup_resp.json().get("balance")
    address_a = topup_resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer to self
    transfer_payload_self = {"to": address_a, "amount": 1}
    transfer_resp_self = requests.post(transfer_url, json=transfer_payload_self, headers=headers_a, timeout=10)
    assert transfer_resp_self.status_code == 200, f"Expected 200, got {transfer_resp_self.status_code}: {transfer_resp_self.text}"

    # Transfer 0 amount
    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_url = get_url("gateway", "/wallet/balance")
    bal_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = bal_resp_b.json().get("address")

    transfer_payload_zero = {"to": address_b, "amount": 0}
    transfer_resp_zero = requests.post(transfer_url, json=transfer_payload_zero, headers=headers_a, timeout=10)
    assert transfer_resp_zero.status_code == 200, f"Expected 200, got {transfer_resp_zero.status_code}: {transfer_resp_zero.text}"

    # Verify balance unchanged
    bal_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert bal_resp_a2.json().get("balance") == balance_a, "Balance should be unchanged for no-op transfers"

# --- id=93  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    transfer_payload_no_to = {"amount": 1}
    resp1 = requests.post(transfer_url, json=transfer_payload_no_to, headers=headers_a, timeout=10)
    assert resp1.status_code == 400, f"Expected 400, got {resp1.status_code}: {resp1.text}"

    # Missing 'amount'
    transfer_payload_no_amount = {"to": "some_address"}
    resp2 = requests.post(transfer_url, json=transfer_payload_no_amount, headers=headers_a, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=94  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp1 = requests.get(balance_url, timeout=10)
    assert resp1.status_code == 401, f"Expected 401, got {resp1.status_code}: {resp1.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp2 = requests.get(topup_url, timeout=10)
    assert resp2.status_code == 401, f"Expected 401, got {resp2.status_code}: {resp2.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp3 = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp3.status_code == 401, f"Expected 401, got {resp3.status_code}: {resp3.text}"
