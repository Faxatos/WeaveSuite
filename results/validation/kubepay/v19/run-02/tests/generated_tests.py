# Tests generated in iteration 02
# Captured: 2026-06-15T16:12:50
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1246  name='Auth And User Workflow' ---
def test_auth_and_user_workflow():
    # Signup
    username = f"user_{generate_random_string()}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    token = resp.json()["token"]

    # Verify user creation via /user/me
    user_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info["user"] == username
    assert "name" in user_info
    assert isinstance(user_info["enabled"], bool)

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    login_token = resp.json()["token"]

    # Verify login token works
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp = requests.get(user_url, headers=headers_login, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["user"] == username

# --- id=1247  name='Wallet Workflow' ---
def test_wallet_workflow():
    user_a, _, token_a = create_user()
    user_b, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Initial balance A
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a = resp.json()
    assert wallet_a["balance"] == 0
    address_a = wallet_a["address"]

    # Initial balance B
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_b = resp.json()
    assert wallet_b["balance"] == 0
    address_b = wallet_b["address"]

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_a_topup = resp.json()
    assert wallet_a_topup["balance"] > 0
    assert wallet_a_topup["address"] == address_a
    topup_amount = wallet_a_topup["balance"]

    # Verify Topup A via balance
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == topup_amount

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = topup_amount / 2.0
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == topup_amount - transfer_amount

    # Verify Transfer via balance A
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == topup_amount - transfer_amount

    # Verify Transfer via balance B
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == transfer_amount

    # No-op transfer A -> A (amount 0)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == topup_amount - transfer_amount

    # Verify No-op via balance A
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == topup_amount - transfer_amount

# --- id=1248  name='Wallet Errors' ---
def test_wallet_errors():
    user_a, _, token_a = create_user()
    user_b, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]

    # Error: Topup A again -> 400
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Error: Transfer with insufficient funds
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a + 100}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Error: Transfer negative amount
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Error: Transfer missing 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Error: Transfer missing 'amount'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1249  name='Auth Errors' ---
def test_auth_errors():
    # Error: Auth without password
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Error: Login with non-existent user / wrong password
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "nonexistent", "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Error: Unauthorized access to protected endpoints
    endpoints = [
        ("GET", "/user/me"),
        ("GET", "/wallet/balance"),
        ("GET", "/wallet/topup"),
        ("POST", "/wallet/transfer")
    ]

    for method, path in endpoints:
        url = get_url("gateway", path)
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json={"to": "someone", "amount": 10}, timeout=10)
        assert resp.status_code == 401, f"Expected 401 for {path}, got {resp.status_code}: {resp.text}"
