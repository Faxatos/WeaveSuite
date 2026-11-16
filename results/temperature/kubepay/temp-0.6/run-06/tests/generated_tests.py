# Tests generated in iteration 06
# Captured: 2026-07-03T00:11:23
# Count:    19
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=846  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # Login
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]

    # Verify User Info
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

# --- id=847  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": "nonexistent", "password": "wrongpassword"}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=848  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=849  name='Auth Login Missing Password' ---
def test_auth_login_missing_password():
    url = get_url("gateway", "/auth/login")
    resp = requests.post(url, json={"user": "testuser"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=850  name='User Me Success' ---
def test_user_me_success():
    username, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=851  name='User Unauthorized Me' ---
def test_user_unauthorized_me():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=852  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance should be 0
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    data = resp_balance.json()
    assert data["balance"] == 0
    address = data["address"]
    assert address is not None

    # Topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    resp_balance2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance2.status_code == 200, f"Expected 200, got {resp_balance2.status_code}: {resp_balance2.text}"
    assert resp_balance2.json()["balance"] == new_balance
    assert resp_balance2.json()["address"] == address

# --- id=853  name='Wallet Topup Twice Conflict' ---
def test_wallet_topup_twice_conflict():
    _, _, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup1 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json()

# --- id=854  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    _, _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    # Get B's address and initial balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]
    balance_b_initial = resp_balance_b.json()["balance"]

    transfer_amount = 1.0
    if balance_a_initial < transfer_amount:
        transfer_amount = balance_a_initial

    # Transfer A to B
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount
    assert resp_transfer.json()["address"] == address_a

    # Verify A's balance
    resp_balance_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json()["balance"] == balance_a_initial - transfer_amount
    assert resp_balance_a2.json()["address"] == address_a

    # Verify B's balance
    resp_balance_b2 = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b2.status_code == 200, f"Expected 200, got {resp_balance_b2.status_code}: {resp_balance_b2.text}"
    assert resp_balance_b2.json()["balance"] == balance_b_initial + transfer_amount
    assert resp_balance_b2.json()["address"] == address_b

# --- id=855  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    _, _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get A's balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_a = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a.status_code == 200, f"Expected 200, got {resp_balance_a.status_code}: {resp_balance_a.text}"
    balance_a = resp_balance_a.json()["balance"]

    # Get B's address
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    # Transfer A to B with insufficient funds
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": balance_a + 100.0}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=856  name='Wallet Transfer Invalid Address' ---
def test_wallet_transfer_invalid_address():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    url_topup = get_url("gateway", "/wallet/topup")
    requests.get(url_topup, headers=headers_a, timeout=10)

    # Transfer A to invalid address
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_address_123", "amount": 1.0}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=857  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    _, _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"

    # Get B's address
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    # Transfer A to B with negative amount
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -1.0}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=858  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = register_user()
    _, _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]

    # Get B's address
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_b = requests.get(url_balance, headers=headers_b, timeout=10)
    assert resp_balance_b.status_code == 200, f"Expected 200, got {resp_balance_b.status_code}: {resp_balance_b.text}"
    address_b = resp_balance_b.json()["address"]

    # Transfer A to B with 0 amount
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 0.0}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's balance unchanged
    resp_balance_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json()["balance"] == balance_a_initial

# --- id=859  name='Wallet Transfer Own Address' ---
def test_wallet_transfer_own_address():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(url_topup, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    # Transfer A to A
    url_transfer = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_a, "amount": 10.0}
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's balance unchanged
    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance_a2 = requests.get(url_balance, headers=headers_a, timeout=10)
    assert resp_balance_a2.status_code == 200, f"Expected 200, got {resp_balance_a2.status_code}: {resp_balance_a2.text}"
    assert resp_balance_a2.json()["balance"] == balance_a_initial

# --- id=860  name='Wallet Transfer Missing To Field' ---
def test_wallet_transfer_missing_to_field():
    _, _, token = register_user()
    url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json={"amount": 10.0}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=861  name='Wallet Transfer Missing Amount Field' ---
def test_wallet_transfer_missing_amount_field():
    _, _, token = register_user()
    url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json={"to": "some_address"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=862  name='Wallet Unauthorized Balance' ---
def test_wallet_unauthorized_balance():
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=863  name='Wallet Unauthorized Topup' ---
def test_wallet_unauthorized_topup():
    url = get_url("gateway", "/wallet/topup")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=864  name='Wallet Unauthorized Transfer' ---
def test_wallet_unauthorized_transfer():
    url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url, json={"to": "some_address", "amount": 10.0}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
