# Tests generated in iteration 07
# Captured: 2026-06-16T03:59:16
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1447  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    login_url = get_url("gateway", "/auth/login")

    # Signup
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Signup again -> 400
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Login
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Login invalid password
    resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Login non-existent user
    resp = requests.post(login_url, json={"user": f"nonexistent_{uuid.uuid4().hex[:8]}", "password": "password"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing password
    resp = requests.post(signup_url, json={"user": f"user_{uuid.uuid4().hex[:8]}"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1448  name='User Me' ---
def test_user_me():
    username, password, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info["user"] == username
    assert "name" in user_info
    assert "enabled" in user_info

    # Unauthorized
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1449  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username, password, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    topup_url = get_url("gateway", "/wallet/topup")

    # Initial balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert wallet_info["balance"] == 0
    address = wallet_info["address"]
    assert address is not None

    # Topup
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    assert topup_info["address"] == address
    assert topup_info["balance"] > 0
    new_balance = topup_info["balance"]

    # Verify balance via GET
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance
    assert resp.json()["address"] == address

    # Topup again -> 400
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Unauthorized balance
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Unauthorized topup
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1450  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    address_a = resp.json()["address"]
    assert balance_a >= 1, "Topup should provide at least 1 unit of balance"

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b = resp.json()["balance"]

    # Transfer A -> B
    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify A's response
    transfer_info = resp.json()
    expected_balance_a = balance_a - transfer_amount
    assert transfer_info["balance"] == expected_balance_a
    assert transfer_info["address"] == address_a

    # Verify A's balance via GET
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == expected_balance_a

    # Verify B's balance via GET
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    expected_balance_b = balance_b + transfer_amount
    assert resp.json()["balance"] == expected_balance_b

    # Transfer 0 (no-op)
    payload_zero = {"to": address_b, "amount": 0}
    resp = requests.post(transfer_url, headers=headers_a, json=payload_zero, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == expected_balance_a

    # Transfer to own address (no-op)
    payload_own = {"to": address_a, "amount": transfer_amount}
    resp = requests.post(transfer_url, headers=headers_a, json=payload_own, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == expected_balance_a

# --- id=1451  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # 1. Missing 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 2. Missing 'amount'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. Negative amount
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 4. Insufficient funds
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a + 100}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 5. Recipient not found
    fake_address = "fake_address_" + uuid.uuid4().hex
    resp = requests.post(transfer_url, headers=headers_a, json={"to": fake_address, "amount": 1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 6. Unauthorized
    resp = requests.post(transfer_url, json={"to": address_b, "amount": 1}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
