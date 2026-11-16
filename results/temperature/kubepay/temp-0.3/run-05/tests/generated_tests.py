# Tests generated in iteration 05
# Captured: 2026-07-02T03:06:39
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=497  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    # Follow-up: Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()

    # Follow-up for Login: Get User Info
    token = login_resp.json()["token"]
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

# --- id=498  name='Auth Signup Missing Fields' ---
def test_auth_signup_missing_fields():
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": "testuser"}, timeout=10)
    assert signup_resp.status_code == 400, f"Expected 400, got {signup_resp.status_code}: {signup_resp.text}"

# --- id=499  name='Auth Login Invalid Password' ---
def test_auth_login_invalid_password():
    username, _, _ = create_user_and_get_token()
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=500  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=501  name='User Me Unauthorized' ---
def test_user_get_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=502  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert balance_data.get("balance") == 0
    assert "address" in balance_data

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data.get("balance") > 0
    assert topup_data.get("address") == balance_data.get("address")

    # Verify balance updated
    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json().get("balance") == topup_data.get("balance")

    # Negative: Topup again (should be 400)
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=503  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json().get("balance")

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json().get("address")
    balance_b_initial = balance_resp_b.json().get("balance")

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify User A balance
    balance_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json().get("balance") == balance_a_initial - transfer_amount

    # Verify User B balance
    balance_resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert balance_resp_b2.status_code == 200, f"Expected 200, got {balance_resp_b2.status_code}: {balance_resp_b2.text}"
    assert balance_resp_b2.json().get("balance") == balance_b_initial + transfer_amount

# --- id=504  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    # User A (no topup, balance 0)
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=505  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Transfer to invalid address
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=506  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    # Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=507  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Transfer with empty body
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=508  name='Wallet Transfer Zero Amount No Op' ---
def test_wallet_transfer_zero_amount_no_op():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    balance_a_initial = topup_resp.json().get("balance")

    # User B
    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = balance_resp_b.json().get("address")

    # Transfer 0 amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify User A balance unchanged
    balance_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_resp_a2.json().get("balance") == balance_a_initial

# --- id=509  name='Wallet Transfer To Self No Op' ---
def test_wallet_transfer_to_self_no_op():
    # User A
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    balance_a_initial = topup_resp.json().get("balance")
    address_a = topup_resp.json().get("address")

    # Transfer to self
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify User A balance unchanged
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert balance_resp_a2.json().get("balance") == balance_a_initial
