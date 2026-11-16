# Tests generated in iteration 04
# Captured: 2026-07-01T03:46:36
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=26  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = generate_user()
    password = generate_password()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "token" in data
    token = data["token"]

    # Follow-up GET to verify state change
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == user

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

# --- id=27  name='User Me' ---
def test_user_me():
    user = generate_user()
    password = generate_password()

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    token = resp.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_url = get_url("gateway", "/user/me")

    # Success
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data

    # Unauthorized
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=28  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    user = generate_user()
    password = generate_password()

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]
    assert address

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_data = resp.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == new_balance

    # Duplicate topup
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=29  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a = generate_user()
    pass_a = generate_password()
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    token_a = resp.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = generate_user()
    pass_b = generate_password()
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pass_b}, timeout=10)
    token_b = resp.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp.json()["balance"]

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]
    balance_b = resp.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == pytest.approx(balance_a - transfer_amount)

    # Verify A's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.json()["balance"] == pytest.approx(balance_a - transfer_amount)

    # Verify B's balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp.json()["balance"] == pytest.approx(balance_b + transfer_amount)

# --- id=30  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    user_a = generate_user()
    pass_a = generate_password()
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    token_a = resp.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp.json()["balance"]
    address_a = resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer to self
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": balance_a / 2.0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == pytest.approx(balance_a)

    # Transfer 0
    user_b = generate_user()
    pass_b = generate_password()
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pass_b}, timeout=10)
    token_b = resp.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == pytest.approx(balance_a)

# --- id=31  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    # User A
    user_a = generate_user()
    pass_a = generate_password()
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    token_a = resp.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = generate_user()
    pass_b = generate_password()
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pass_b}, timeout=10)
    token_b = resp.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Insufficient funds (A has 0)
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Topup A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Negative amount
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -5}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing required field 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Empty required field 'to'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing required field 'amount'
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Recipient wallet not found
    fake_address = "fake_" + uuid.uuid4().hex
    resp = requests.post(transfer_url, headers=headers_a, json={"to": fake_address, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Unauthorized
    resp = requests.post(transfer_url, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=32  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
