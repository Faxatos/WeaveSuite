# Tests generated in iteration 14
# Captured: 2026-07-01T14:11:53
# Count:    17
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=212  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]

    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json()["token"]

    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=213  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=214  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "nonexistent", "password": "wrong"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=215  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=216  name='User Me Success' ---
def test_user_me_success():
    username, _, token = create_user()
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=217  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    assert "address" in data
    assert isinstance(data["address"], str)

# --- id=218  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=219  name='Wallet Topup Success And Conflict' ---
def test_wallet_topup_success_and_conflict():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    new_balance = data["balance"]
    assert new_balance > 0
    address = data["address"]

    balance_url = get_url("gateway", "/wallet/balance")
    resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json()["balance"] == new_balance
    assert resp2.json()["address"] == address

    resp3 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp3.status_code == 400, f"Expected 400, got {resp3.status_code}: {resp3.text}"

# --- id=220  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=221  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_initial = resp_topup.json()["balance"]
    address_a = resp_topup.json()["address"]

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]
    balance_b_initial = resp_b.json()["balance"]

    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    data_transfer = resp_transfer.json()
    assert data_transfer["balance"] == balance_a_initial - transfer_amount
    assert data_transfer["address"] == address_a

    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.status_code == 200, f"Expected 200, got {resp_a_after.status_code}: {resp_a_after.text}"
    assert resp_a_after.json()["balance"] == balance_a_initial - transfer_amount

    resp_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_after.status_code == 200, f"Expected 200, got {resp_b_after.status_code}: {resp_b_after.text}"
    assert resp_b_after.json()["balance"] == balance_b_initial + transfer_amount

# --- id=222  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    address_b = resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=223  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    address_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=224  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")

    resp1 = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp1.status_code == 400, f"Expected 400, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(transfer_url, headers=headers_a, json={"to": "some_address"}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=225  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": "invalid_address_123", "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=226  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = topup_resp.json()["balance"]

    _, _, token_b = create_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    address_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

    balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp.json()["balance"] == balance_a_initial

# --- id=227  name='Wallet Transfer Self' ---
def test_wallet_transfer_self():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = topup_resp.json()["balance"]
    address_a = topup_resp.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == balance_a_initial

    balance_resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp.json()["balance"] == balance_a_initial

# --- id=228  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
