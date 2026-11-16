# Tests generated in iteration 07
# Captured: 2026-06-14T20:49:54
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=967  name='Auth Signup And Login Success' ---
def test_auth_signup_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()
    token = signup_resp.json()["token"]

    # Follow-up GET to verify user creation
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()
    login_token = login_resp.json()["token"]

    # Verify login token works
    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=968  name='Auth Signup Bad Request' ---
def test_auth_signup_bad_request():
    username = f"user_{uuid.uuid4().hex[:8]}"
    signup_url = get_url("gateway", "/auth/signup")
    # Missing password
    signup_resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert signup_resp.status_code == 400, f"Expected 400, got {signup_resp.status_code}: {signup_resp.text}"

# --- id=969  name='Auth Login Bad Request' ---
def test_auth_login_bad_request():
    username, password, _ = create_user()
    login_url = get_url("gateway", "/auth/login")
    # Wrong password
    login_resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=970  name='User Me Success' ---
def test_user_me_success():
    username, _, token = create_user()
    url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=971  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=972  name='Wallet Balance Success' ---
def test_wallet_balance_success():
    _, _, token = create_user()
    url = get_url("gateway", "/wallet/balance")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "address" in data
    assert data["balance"] == 0

# --- id=973  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    url = get_url("gateway", "/wallet/balance")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=974  name='Wallet Topup Success' ---
def test_wallet_topup_success():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["balance"] > 0

    # Verify balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    assert balance_resp.json()["balance"] == topup_data["balance"]

# --- id=975  name='Wallet Topup Bad Request Already Topped Up' ---
def test_wallet_topup_bad_request_already_topped_up():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    topup_url = get_url("gateway", "/wallet/topup")
    first_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert first_resp.status_code == 200, f"Expected 200, got {first_resp.status_code}: {first_resp.text}"

    # Second topup
    second_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert second_resp.status_code == 400, f"Expected 400, got {second_resp.status_code}: {second_resp.text}"

# --- id=976  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    url = get_url("gateway", "/wallet/topup")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=977  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    # Transfer A -> B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Verify A's balance in response
    assert transfer_resp.json()["balance"] == balance_a_initial - transfer_amount

    # Verify A's balance via GET
    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json()["balance"] == balance_a_initial - transfer_amount

    # Verify B's balance via GET
    resp_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_after.status_code == 200, f"Expected 200, got {resp_b_after.status_code}: {resp_b_after.text}"
    assert resp_b_after.json()["balance"] == transfer_amount

# --- id=978  name='Wallet Transfer Bad Request Insufficient Funds' ---
def test_wallet_transfer_bad_request_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    # Transfer A -> B without topup (balance 0)
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": 10}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=979  name='Wallet Transfer Bad Request Missing Fields' ---
def test_wallet_transfer_bad_request_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")
    # Missing 'to'
    transfer_payload = {"amount": 10}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=980  name='Wallet Transfer Bad Request Negative Amount' ---
def test_wallet_transfer_bad_request_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Transfer A -> B with negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": address_b, "amount": -10}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=981  name='Wallet Transfer Bad Request Recipient Not Found' ---
def test_wallet_transfer_bad_request_recipient_not_found():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)

    # Transfer A -> nonexistent address
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "nonexistent_address_12345", "amount": 10}
    transfer_resp = requests.post(transfer_url, headers=headers_a, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=982  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_payload = {"to": "some_address", "amount": 10}
    transfer_resp = requests.post(transfer_url, json=transfer_payload, timeout=10)
    assert transfer_resp.status_code == 401, f"Expected 401, got {transfer_resp.status_code}: {transfer_resp.text}"
