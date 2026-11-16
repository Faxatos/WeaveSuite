# Tests generated in iteration 01
# Captured: 2026-07-02T21:58:41
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=796  name='Wallet Transfer Invalid Inputs' ---
def test_wallet_transfer_invalid_inputs():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative amount
    resp_neg = requests.post(transfer_url, headers=headers_a, json={"to": "some_address", "amount": -10}, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    # Missing 'to'
    resp_no_to = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp_no_to.status_code == 400, f"Expected 400, got {resp_no_to.status_code}: {resp_no_to.text}"

    # Missing 'amount'
    resp_no_amt = requests.post(transfer_url, headers=headers_a, json={"to": "some_address"}, timeout=10)
    assert resp_no_amt.status_code == 400, f"Expected 400, got {resp_no_amt.status_code}: {resp_no_amt.text}"

    # Non-existent recipient wallet
    resp_not_found = requests.post(transfer_url, headers=headers_a, json={"to": "non_existent_wallet_address", "amount": 10}, timeout=10)
    assert resp_not_found.status_code == 400, f"Expected 400, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=797  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    balance_a_initial = resp_topup.json()["balance"]
    address_a = resp_topup.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer to self
    resp_self = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp_self.status_code == 200, f"Expected 200, got {resp_self.status_code}: {resp_self.text}"
    assert resp_self.json()["balance"] == balance_a_initial

    # Transfer 0 amount
    _, _, token_b = create_user()
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    address_b = resp_b.json()["address"]

    resp_zero = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp_zero.status_code == 200, f"Expected 200, got {resp_zero.status_code}: {resp_zero.text}"
    assert resp_zero.json()["balance"] == balance_a_initial

# --- id=798  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    endpoints = [
        ("GET", "/user/me", None),
        ("GET", "/wallet/balance", None),
        ("GET", "/wallet/topup", None),
        ("POST", "/wallet/transfer", {"to": "address", "amount": 10})
    ]

    for method, path, body in endpoints:
        url = get_url("gateway", path)
        kwargs = {"timeout": 10}
        if body:
            kwargs["json"] = body

        # No token
        if method == "GET":
            resp = requests.get(url, **kwargs)
        else:
            resp = requests.post(url, **kwargs)
        assert resp.status_code == 401, f"Expected 401 for {path}, got {resp.status_code}: {resp.text}"

        # Invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        if method == "GET":
            resp = requests.get(url, headers=headers, **kwargs)
        else:
            resp = requests.post(url, headers=headers, **kwargs)
        assert resp.status_code == 401, f"Expected 401 for {path} with invalid token, got {resp.status_code}: {resp.text}"

# --- id=789  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Follow-up: Login to verify state change (user created)
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=790  name='Auth Login Failure' ---
def test_auth_login_failure():
    username, password, _ = create_user()
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=791  name='User Me Success' ---
def test_user_me_success():
    username, password, token = create_user()
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=792  name='Wallet Balance And Topup Success' ---
def test_wallet_balance_and_topup_success():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Check initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Follow-up: Verify balance
    resp_verify = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_verify.status_code == 200, f"Expected 200, got {resp_verify.status_code}: {resp_verify.text}"
    assert resp_verify.json()["balance"] == new_balance

# --- id=793  name='Wallet Topup Conflict' ---
def test_wallet_topup_conflict():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Second topup should fail
    resp_conflict = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"
    assert "message" in resp_conflict.json()

# --- id=794  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json()["balance"]

    # Get User B address and initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]
    balance_b_initial = resp_b.json()["balance"]

    # Transfer from A to B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = balance_a_initial / 2.0
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A balance returned in transfer response
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount

    # Follow-up: Verify A balance via GET
    resp_a_verify = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_verify.status_code == 200, f"Expected 200, got {resp_a_verify.status_code}: {resp_a_verify.text}"
    assert resp_a_verify.json()["balance"] == balance_a_initial - transfer_amount

    # Follow-up: Verify B balance via GET
    resp_b_verify = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_verify.status_code == 200, f"Expected 200, got {resp_b_verify.status_code}: {resp_b_verify.text}"
    assert resp_b_verify.json()["balance"] == balance_b_initial + transfer_amount

# --- id=795  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_b.json()["address"]

    # A has 0 balance. Transfer should fail.
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up: Verify A balance remains 0
    resp_a_verify = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_verify.json()["balance"] == 0
