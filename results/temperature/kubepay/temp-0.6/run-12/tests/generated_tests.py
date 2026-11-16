# Tests generated in iteration 12
# Captured: 2026-07-03T02:45:59
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=912  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Verify state via /user/me
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == user

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token is not None

    # Negative: Login wrong password
    resp = requests.post(login_url, json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Signup missing password (required field)
    resp = requests.post(signup_url, json={"user": f"user_{uuid.uuid4().hex[:8]}"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=913  name='User Me' ---
def test_user_me():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == user
    assert "name" in data
    assert "enabled" in data

    # Negative: No token
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Negative: Invalid token
    resp = requests.get(me_url, headers={"Authorization": "Bearer invalidtoken"}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=914  name='Wallet Lifecycle And Topup' ---
def test_wallet_lifecycle_and_topup():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    address = data.get("address")
    assert address is not None

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data.get("address") == address
    assert topup_data.get("balance") > 0
    new_balance = topup_data.get("balance")

    # Verify balance via follow-up GET
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance

    # Negative: Topup again (documented constraint)
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: Unauthorized balance
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Negative: Unauthorized topup
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=915  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # Setup User A
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_a = resp.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup User B
    user_b = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_b = resp.json().get("token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")
    address_a = resp.json().get("address")

    # Get B address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")
    balance_b = resp.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_data = resp.json()
    assert transfer_data.get("address") == address_a
    assert transfer_data.get("balance") == balance_a - transfer_amount

    # Verify A balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    # Verify B balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_b + transfer_amount

    # Transfer 0 (no-op)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    # Verify B balance remains unchanged
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_b + transfer_amount

    # Transfer to self (no-op)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 1}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

    # Verify A balance remains unchanged
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == balance_a - transfer_amount

# --- id=916  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    # Setup User A
    user_a = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_a = resp.json().get("token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    balance_a = resp.json().get("balance")

    # Setup User B
    user_b = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token_b = resp.json().get("token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_b = resp.json().get("address")

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing 'amount'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative amount
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Insufficient funds
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a + 1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Recipient not found
    fake_address = f"addr_{uuid.uuid4().hex}"
    resp = requests.post(transfer_url, headers=headers_a, json={"to": fake_address, "amount": 1}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Unauthorized
    resp = requests.post(transfer_url, json={"to": address_b, "amount": 1}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
