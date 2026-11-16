# Tests generated in iteration 07
# Captured: 2026-07-01T04:55:04
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=51  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    token = resp.json()["token"]

    # Verify user creation via GET /user/me
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == user

    # Login
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Negative: Login with wrong password
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=52  name='User Me' ---
def test_user_me():
    user, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data

    # Negative: No token
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=53  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data

    # Topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["balance"] > 0

    # Verify balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == topup_data["balance"]

    # Negative: Topup again (documented constraint)
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=54  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify topup
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    balance_a = resp_bal.json()["balance"]

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json()["address"]
    balance_b = resp.json()["balance"]

    transfer_amount = balance_a / 2.0

    # Transfer A -> B
    payload = {"to": address_b, "amount": transfer_amount}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Verify A's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Verify B's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_b + transfer_amount

    # Edge case: Transfer 0
    payload = {"to": address_b, "amount": 0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify A's balance unchanged
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

    # Edge case: Transfer to self
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    address_a = resp.json()["address"]
    payload = {"to": address_a, "amount": transfer_amount / 2.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify A's balance unchanged
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a - transfer_amount

# --- id=55  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify topup
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    balance_a = resp_bal.json()["balance"]

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    # Negative: Transfer negative amount
    payload = {"to": address_b, "amount": -10}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Transfer more than balance
    payload = {"to": address_b, "amount": balance_a + 100}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Transfer to non-existent address
    payload = {"to": "non_existent_address_123", "amount": balance_a / 2.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Missing 'to'
    payload = {"amount": balance_a / 2.0}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Missing 'amount'
    payload = {"to": address_b}
    resp = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
