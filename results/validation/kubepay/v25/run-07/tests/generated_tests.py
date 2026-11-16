# Tests generated in iteration 07
# Captured: 2026-06-17T03:07:30
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1741  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{generate_random_string()}"
    password = generate_random_string(12)

    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_signup = resp.json().get("token")
    assert token_signup is not None

    # Follow-up GET for signup
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers={"Authorization": f"Bearer {token_signup}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"

    # Login
    url_login = get_url("gateway", "/auth/login")
    resp = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_login = resp.json().get("token")
    assert token_login is not None

    # Follow-up GET for login
    resp_me_login = requests.get(url_me, headers={"Authorization": f"Bearer {token_login}"}, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == username

# --- id=1742  name='Auth Signup Bad Request' ---
def test_auth_signup_bad_request():
    url_signup = get_url("gateway", "/auth/signup")
    # Missing password
    resp = requests.post(url_signup, json={"user": f"user_{generate_random_string()}"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1743  name='User Me' ---
def test_user_get_me():
    username, password, token = create_user()

    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert data.get("enabled") is True

# --- id=1744  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    address = data.get("address")
    assert address is not None

    # Topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    new_balance = topup_data.get("balance")
    assert new_balance > 0
    assert topup_data.get("address") == address

    # Verify balance
    resp = requests.get(url_balance, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance

# --- id=1745  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Second topup should fail
    resp = requests.get(url_topup, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1746  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    # Get User B address and balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b = resp.json().get("balance")
    assert balance_b == 0

    # Transfer from A to B
    transfer_amount = 10
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify A's balance in response
    new_balance_a = resp.json().get("balance")
    assert new_balance_a == balance_a - transfer_amount

    # Verify A's balance via GET
    resp = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    # Verify B's balance via GET
    resp = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_b + transfer_amount

# --- id=1747  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    # Transfer from A to B (A has 0 balance)
    transfer_amount = 10
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance is still 0
    resp = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0

# --- id=1748  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    # Get User B address
    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    # Transfer negative amount
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -10}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance unchanged
    resp = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

# --- id=1749  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    # Transfer to invalid address
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_address_12345", "amount": 10}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify A's balance unchanged
    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

# --- id=1750  name='Wallet Transfer Zero Amount And Self' ---
def test_wallet_transfer_zero_amount_and_self():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    url_topup = get_url("gateway", "/wallet/topup")
    resp = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")
    address_a = resp.json().get("address")

    # Transfer 0 to self
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": 0}
    resp = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

    # Verify balance unchanged
    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a

# --- id=1751  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_transfer = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    payload_no_to = {"amount": 10}
    resp = requests.post(url_transfer, headers=headers_a, json=payload_no_to, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'amount'
    payload_no_amount = {"to": "some_address"}
    resp = requests.post(url_transfer, headers=headers_a, json=payload_no_amount, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1752  name='Gateway Unauthorized Access' ---
def test_gateway_unauthorized_access():
    # Missing token for /user/me
    url_user = get_url("gateway", "/user/me")
    resp = requests.get(url_user, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Missing token for /wallet/balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Invalid token for /wallet/topup
    url_topup = get_url("gateway", "/wallet/topup")
    headers = {"Authorization": "Bearer invalid_token_123"}
    resp = requests.get(url_topup, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Missing token for /wallet/transfer
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": "some_address", "amount": 10}
    resp = requests.post(url_transfer, json=payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
