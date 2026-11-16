# Tests generated in iteration 04
# Captured: 2026-06-14T12:48:32
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=774  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()
    token = resp_signup.json()["token"]

    # Follow-up GET to verify signup
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()
    login_token = resp_login.json()["token"]

    # Follow-up GET to verify login token works
    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=775  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=776  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user()

    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=777  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user()

    # Initial balance should be 0
    info = get_wallet_info(token)
    assert info["balance"] == 0, f"Expected initial balance 0, got {info['balance']}"
    assert "address" in info

    # Top up
    url = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": f"Bearer {token}"}
    resp_topup = requests.get(url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    # Verify balance with GET
    new_info = get_wallet_info(token)
    assert new_info["balance"] > 0
    assert new_info["balance"] == resp_topup.json()["balance"]

    # Top up again should fail (negative test)
    resp_topup_again = requests.get(url, headers=headers, timeout=10)
    assert resp_topup_again.status_code == 400, f"Expected 400, got {resp_topup_again.status_code}: {resp_topup_again.text}"

# --- id=778  name='Wallet Transfer Success Multiple Times' ---
def test_wallet_transfer_success_multiple_times():
    # Create User A and top up
    _, _, token_a = create_user()
    topup_wallet(token_a)
    info_a_before = get_wallet_info(token_a)

    # Create User B
    _, _, token_b = create_user()
    info_b_before = get_wallet_info(token_b)
    address_b = info_b_before["address"]

    transfer_amount = 1

    # Transfer 1: A -> B
    url_transfer = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": transfer_amount}

    resp_transfer_1 = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer_1.status_code == 200, f"Expected 200, got {resp_transfer_1.status_code}: {resp_transfer_1.text}"

    # Follow-up GET for Transfer 1
    info_a_mid = get_wallet_info(token_a)
    assert info_a_mid["balance"] == info_a_before["balance"] - transfer_amount

    # Transfer 2: A -> B
    resp_transfer_2 = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer_2.status_code == 200, f"Expected 200, got {resp_transfer_2.status_code}: {resp_transfer_2.text}"

    # Follow-up GET for Transfer 2 (Cumulative state)
    info_a_after = get_wallet_info(token_a)
    info_b_after = get_wallet_info(token_b)

    assert info_a_after["balance"] == info_a_before["balance"] - (transfer_amount * 2)
    assert info_b_after["balance"] == info_b_before["balance"] + (transfer_amount * 2)

# --- id=779  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # Create User A (no top up, balance 0)
    _, _, token_a = create_user()

    # Create User B
    _, _, token_b = create_user()
    address_b = get_wallet_info(token_b)["address"]

    # Transfer A -> B
    url_transfer = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": 10}

    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    info_a_after = get_wallet_info(token_a)
    assert info_a_after["balance"] == 0

# --- id=780  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    # Create User A and top up
    _, _, token_a = create_user()
    info_a_before = topup_wallet(token_a)

    # Create User B
    _, _, token_b = create_user()
    address_b = get_wallet_info(token_b)["address"]

    # Transfer A -> B with negative amount
    url_transfer = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": -5}

    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    info_a_after = get_wallet_info(token_a)
    assert info_a_after["balance"] == info_a_before["balance"]

# --- id=781  name='Wallet Transfer Zero Amount No Op' ---
def test_wallet_transfer_zero_amount_no_op():
    # Create User A and top up
    _, _, token_a = create_user()
    info_a_before = topup_wallet(token_a)

    # Create User B
    _, _, token_b = create_user()
    info_b_before = get_wallet_info(token_b)
    address_b = info_b_before["address"]

    # Transfer 0: A -> B
    url_transfer = get_url("gateway", "/wallet/transfer")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    payload = {"to": address_b, "amount": 0}

    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balances unchanged
    info_a_after = get_wallet_info(token_a)
    info_b_after = get_wallet_info(token_b)

    assert info_a_after["balance"] == info_a_before["balance"]
    assert info_b_after["balance"] == info_b_before["balance"]

# --- id=782  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token = create_user()
    url = get_url("gateway", "/wallet/transfer")
    headers = {"Authorization": f"Bearer {token}"}

    # Missing 'to'
    resp1 = requests.post(url, headers=headers, json={"amount": 10}, timeout=10)
    assert resp1.status_code == 400, f"Expected 400, got {resp1.status_code}: {resp1.text}"

    # Missing 'amount'
    resp2 = requests.post(url, headers=headers, json={"to": "some_address"}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=783  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    # Try to access protected endpoints without token
    endpoints = [
        ("/user/me", requests.get),
        ("/wallet/balance", requests.get),
        ("/wallet/topup", requests.get),
        ("/wallet/transfer", requests.post)
    ]

    for path, method in endpoints:
        url = get_url("gateway", path)
        if method == requests.post:
            resp = method(url, json={"to": "some_address", "amount": 10}, timeout=10)
        else:
            resp = method(url, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {path}, got {resp.status_code}: {resp.text}"
