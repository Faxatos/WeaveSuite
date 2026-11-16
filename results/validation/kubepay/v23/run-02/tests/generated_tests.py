# Tests generated in iteration 02
# Captured: 2026-06-16T14:21:50
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1560  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    url_signup = get_url("gateway", "/auth/signup")

    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=1561  name='Auth Signup Duplicate' ---
def test_auth_signup_duplicate():
    username, password, _ = create_user()
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

# --- id=1562  name='Auth Login Invalid Password' ---
def test_auth_login_invalid_password():
    username, _, _ = create_user()
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=1563  name='User Me Success' ---
def test_user_me_success():
    username, _, token = create_user()
    url_me = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=1564  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

# --- id=1565  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user()
    url_balance = get_url("gateway", "/wallet/balance")
    headers = {"Authorization": f"Bearer {token}"}
    resp_balance = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    data = resp_balance.json()
    assert data["balance"] == 0
    assert "address" in data

# --- id=1566  name='Wallet Topup Success And Duplicate' ---
def test_wallet_topup_success_and_duplicate():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_initial = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance_initial.status_code == 200, f"Expected 200, got {resp_balance_initial.status_code}: {resp_balance_initial.text}"
    initial_data = resp_balance_initial.json()
    assert initial_data["balance"] == 0

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == initial_data["address"]

    resp_balance_after = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance_after.status_code == 200, f"Expected 200, got {resp_balance_after.status_code}: {resp_balance_after.text}"
    assert resp_balance_after.json()["balance"] == topup_data["balance"]

    resp_topup_duplicate = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup_duplicate.status_code == 400, f"Expected 400, got {resp_topup_duplicate.status_code}: {resp_topup_duplicate.text}"

# --- id=1567  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers=headers_a, timeout=10)

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a = resp_bal_a.json()["balance"]

    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]

    transfer_amount = balance_a / 2.0
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    transfer_data = resp_transfer.json()
    assert transfer_data["balance"] == balance_a - transfer_amount

    resp_bal_a_after = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a_after.status_code == 200, f"Expected 200, got {resp_bal_a_after.status_code}: {resp_bal_a_after.text}"
    assert resp_bal_a_after.json()["balance"] == balance_a - transfer_amount

    resp_bal_b_after = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b_after.status_code == 200, f"Expected 200, got {resp_bal_b_after.status_code}: {resp_bal_b_after.text}"
    assert resp_bal_b_after.json()["balance"] == balance_b + transfer_amount

# --- id=1568  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": 10.0}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1569  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers=headers_a, timeout=10)

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": "invalid_address_123", "amount": 1.0}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1570  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers=headers_a, timeout=10)

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": -5.0}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1571  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers=headers_a, timeout=10)

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer_missing_to = requests.post(url_transfer, headers=headers_a, json={"amount": 1.0}, timeout=10)
    assert resp_transfer_missing_to.status_code == 400, f"Expected 400, got {resp_transfer_missing_to.status_code}: {resp_transfer_missing_to.text}"

    resp_transfer_missing_amount = requests.post(url_transfer, headers=headers_a, json={"to": "some_address"}, timeout=10)
    assert resp_transfer_missing_amount.status_code == 400, f"Expected 400, got {resp_transfer_missing_amount.status_code}: {resp_transfer_missing_amount.text}"

# --- id=1572  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, json={"to": "some_address", "amount": 10.0}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1573  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    resp_bal_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    balance_a = resp_bal_a.json()["balance"]

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json={"to": address_b, "amount": 0.0}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp_bal_a_after = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_bal_a_after.status_code == 200, f"Expected 200, got {resp_bal_a_after.status_code}: {resp_bal_a_after.text}"
    assert resp_bal_a_after.json()["balance"] == balance_a
