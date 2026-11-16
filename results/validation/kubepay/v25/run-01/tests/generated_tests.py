# Tests generated in iteration 01
# Captured: 2026-06-17T00:47:09
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1688  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{generate_random_string()}"
    password = f"pass_{generate_random_string()}"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Invalid login
    resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1689  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    user_url = get_url("gateway", "/user/me")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info["user"] == username
    assert user_info["enabled"] is True

# --- id=1690  name='Wallet Topup' ---
def test_wallet_topup():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial wallet balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert wallet_info["balance"] == 0
    address = wallet_info["address"]
    assert address is not None

    # Topup wallet
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    new_balance = topup_info["balance"]
    assert new_balance > 0
    assert topup_info["address"] == address

    # Verify balance updated
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Topup again should fail
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1691  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    address_a = resp.json()["address"]

    # User B
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b = resp.json()["balance"]
    assert balance_b == 0

    # Transfer from A to B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_info = resp.json()
    expected_balance_a = balance_a - transfer_amount
    assert transfer_info["balance"] == expected_balance_a

    # Verify A's balance
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == expected_balance_a

    # Verify B's balance
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == transfer_amount

    # Transfer 0 to B (no-op)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == expected_balance_a

    # Transfer to own address (no-op)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == expected_balance_a

# --- id=1692  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]

    # User B
    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    # Transfer from A to B with insufficient funds
    transfer_amount = balance_a + 100
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance unchanged
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

# --- id=1693  name='Wallet Transfer Invalid Amount And Recipient' ---
def test_wallet_transfer_invalid_amount_and_recipient():
    # User A
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative amount
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "some_address", "amount": -10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Non-existent recipient
    non_existent_address = f"addr_{generate_random_string()}"
    resp = requests.post(transfer_url, headers=headers_a, json={"to": non_existent_address, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a

# --- id=1694  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    # No token
    user_url = get_url("gateway", "/user/me")
    resp = requests.get(user_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
