# Tests generated in iteration 08
# Captured: 2026-06-21T22:18:49
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=59  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Login
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Negative: Signup missing password
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Login wrong password
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=60  name='User Me' ---
def test_user_me():
    user, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert isinstance(data["enabled"], bool)

    # Negative: No token
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=61  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]
    assert address

    # Topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Follow-up GET
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Negative: Topup again
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=62  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]
    address_a = resp.json()["address"]

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_b = resp.json()["balance"]
    address_b = resp.json()["address"]
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Follow-up A
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Follow-up B
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == transfer_amount

    # Transfer 0 (no-op)
    payload = {"to": address_b, "amount": 0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Transfer to own address (no-op)
    payload = {"to": address_a, "amount": transfer_amount / 2.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

# --- id=63  name='Wallet Transfer Negative' ---
def test_wallet_transfer_negative():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json()["balance"]

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]

    # Negative: Negative amount
    payload = {"to": address_b, "amount": -10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Insufficient funds
    payload = {"to": address_b, "amount": balance_a + 100}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Recipient not found
    payload = {"to": "non_existent_address_12345", "amount": 1}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Missing 'to'
    payload = {"amount": 1}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Missing 'amount'
    payload = {"to": address_b}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Unauthorized
    payload = {"to": address_b, "amount": 1}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json=payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
