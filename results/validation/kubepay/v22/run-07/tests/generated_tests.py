# Tests generated in iteration 07
# Captured: 2026-06-16T10:55:06
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1516  name='Auth Login' ---
def test_auth_login():
    username, password, token = create_user()

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token, "Token missing in login response"

    # Follow-up GET
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {login_token}"}
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

# --- id=1517  name='Auth Invalid Request' ---
def test_auth_invalid_request():
    signup_url = get_url("gateway", "/auth/signup")

    # Missing password
    resp = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    error_data = resp.json()
    assert "message" in error_data

# --- id=1518  name='Wallet Transfer Workflow' ---
def test_wallet_transfer_workflow():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    addr_a, bal_a = get_wallet_info(token_a)
    assert bal_a == 0, "New wallet balance should be 0"

    addr_b, bal_b = get_wallet_info(token_b)
    assert bal_b == 0, "New wallet balance should be 0"

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    bal_a_after_topup = resp.json()["balance"]
    assert bal_a_after_topup > 0, "Topup should increase balance"

    # Follow-up GET
    _, bal_a_check = get_wallet_info(token_a)
    assert bal_a_check == bal_a_after_topup

    # Transfer A -> B
    transfer_amount = 1 if bal_a_after_topup >= 1 else bal_a_after_topup / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": addr_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    assert transfer_data["address"] == addr_a
    assert transfer_data["balance"] == bal_a_after_topup - transfer_amount

    # Follow-up GET A
    _, bal_a_post = get_wallet_info(token_a)
    assert bal_a_post == bal_a_after_topup - transfer_amount

    # Follow-up GET B
    _, bal_b_post = get_wallet_info(token_b)
    assert bal_b_post == transfer_amount

# --- id=1519  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    addr_a, bal_a = get_wallet_info(token_a)

    # Transfer 0 to self
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": addr_a, "amount": 0}
    resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    assert transfer_data["balance"] == bal_a

    # Follow-up GET
    _, bal_a_after = get_wallet_info(token_a)
    assert bal_a_after == bal_a

# --- id=1520  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    _, bal = get_wallet_info(token)
    assert bal > 0

    # Second topup
    resp_fail = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_fail.status_code == 400, f"Expected 400, got {resp_fail.status_code}: {resp_fail.text}"

    # Verify balance hasn't changed
    _, bal_after = get_wallet_info(token)
    assert bal_after == bal

# --- id=1521  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    addr_b, _ = get_wallet_info(token_b)

    # A has 0 balance. Transfer 10 to B.
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": addr_b, "amount": 10}
    resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance is still 0
    _, bal_a = get_wallet_info(token_a)
    assert bal_a == 0

# --- id=1522  name='Wallet Transfer Invalid Amount' ---
def test_wallet_transfer_invalid_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    addr_b, _ = get_wallet_info(token_b)

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    _, bal_a_before = get_wallet_info(token_a)

    # Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": addr_b, "amount": -5}
    resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance is unchanged
    _, bal_a_after = get_wallet_info(token_a)
    assert bal_a_after == bal_a_before

# --- id=1523  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    _, bal_a_before = get_wallet_info(token_a)

    # Transfer to non-existent address
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "non_existent_address_123", "amount": 1}
    resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance is unchanged
    _, bal_a_after = get_wallet_info(token_a)
    assert bal_a_after == bal_a_before

# --- id=1524  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp_no_to = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp_no_to.status_code == 400, f"Expected 400, got {resp_no_to.status_code}: {resp_no_to.text}"

    # Missing 'amount'
    resp_no_amount = requests.post(transfer_url, headers=headers_a, json={"to": "some_address"}, timeout=10)
    assert resp_no_amount.status_code == 400, f"Expected 400, got {resp_no_amount.status_code}: {resp_no_amount.text}"

# --- id=1525  name='Wallet Unauthorized Access' ---
def test_wallet_unauthorized_access():
    balance_url = get_url("gateway", "/wallet/balance")

    # Missing token
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token_123"}
    resp_invalid = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_invalid.status_code == 401, f"Expected 401, got {resp_invalid.status_code}: {resp_invalid.text}"
