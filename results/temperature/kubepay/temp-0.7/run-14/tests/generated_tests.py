# Tests generated in iteration 14
# Captured: 2026-07-01T22:31:50
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=408  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_url = get_url("gateway", "/wallet/balance")
    address_b = requests.get(balance_url, headers=headers_b, timeout=10).json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": -10}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=409  name='Wallet Transfer Zero Amount' ---
def test_wallet_transfer_zero_amount():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)
    balance_url = get_url("gateway", "/wallet/balance")
    bal_a_initial = requests.get(balance_url, headers=headers_a, timeout=10).json()["balance"]
    address_a = requests.get(balance_url, headers=headers_a, timeout=10).json()["address"]

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    bal_b_initial = requests.get(balance_url, headers=headers_b, timeout=10).json()["balance"]
    address_b = requests.get(balance_url, headers=headers_b, timeout=10).json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 0}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    data = resp_transfer.json()
    assert data["balance"] == bal_a_initial
    assert data["address"] == address_a

    bal_b_final = requests.get(balance_url, headers=headers_b, timeout=10).json()["balance"]
    assert bal_b_final == bal_b_initial

# --- id=410  name='Wallet Transfer To Self' ---
def test_wallet_transfer_to_self():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers, timeout=10)

    balance_url = get_url("gateway", "/wallet/balance")
    bal_initial = requests.get(balance_url, headers=headers, timeout=10).json()["balance"]
    address = requests.get(balance_url, headers=headers, timeout=10).json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address, "amount": 5}
    resp_transfer = requests.post(transfer_url, headers=headers, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    data = resp_transfer.json()
    assert data["balance"] == bal_initial
    assert data["address"] == address

# --- id=411  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    transfer_url = get_url("gateway", "/wallet/transfer")

    payload = {"amount": 10}
    resp = requests.post(transfer_url, headers=headers, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=412  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=398  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=399  name='Auth Signup Duplicate User' ---
def test_auth_signup_duplicate_user():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_dup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"
    assert "message" in resp_dup.json()

# --- id=400  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": "nonexistent", "password": "bad"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=401  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user_and_get_token()
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=402  name='User Me Unauthorized' ---
def test_user_get_me_unauthorized():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=403  name='Wallet Balance Initial' ---
def test_wallet_balance_initial():
    _, _, token = create_user_and_get_token()
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("balance") == 0
    assert "address" in data
    assert isinstance(data["address"], str)

# --- id=404  name='Wallet Topup Success And Duplicate' ---
def test_wallet_topup_success_and_duplicate():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    address = resp_bal.json()["address"]

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data = resp_topup.json()
    new_balance = data.get("balance")
    assert new_balance > 0
    assert data.get("address") == address

    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == new_balance

    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json()

# --- id=405  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers_a, timeout=10)
    balance_url = get_url("gateway", "/wallet/balance")
    bal_a_resp = requests.get(balance_url, headers=headers_a, timeout=10)
    bal_a_initial = bal_a_resp.json()["balance"]
    address_a = bal_a_resp.json()["address"]

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    bal_b_resp = requests.get(balance_url, headers=headers_b, timeout=10)
    bal_b_initial = bal_b_resp.json()["balance"]
    address_b = bal_b_resp.json()["address"]

    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    data = resp_transfer.json()
    assert data["address"] == address_a
    assert data["balance"] == bal_a_initial - transfer_amount

    bal_a_final = requests.get(balance_url, headers=headers_a, timeout=10).json()["balance"]
    assert bal_a_final == bal_a_initial - transfer_amount

    bal_b_final = requests.get(balance_url, headers=headers_b, timeout=10).json()["balance"]
    assert bal_b_final == bal_b_initial + transfer_amount

# --- id=406  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    balance_url = get_url("gateway", "/wallet/balance")
    address_b = requests.get(balance_url, headers=headers_b, timeout=10).json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": 100}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

    bal_a_final = requests.get(balance_url, headers=headers_a, timeout=10).json()["balance"]
    assert bal_a_final == 0

# --- id=407  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers=headers, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": "invalid_address_123", "amount": 10}
    resp_transfer = requests.post(transfer_url, headers=headers, json=payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
