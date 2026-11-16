# Tests generated in iteration 04
# Captured: 2026-07-01T18:27:41
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=303  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")

    # Negative: Signup missing password
    resp_no_pass = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp_no_pass.status_code == 400, f"Expected 400, got {resp_no_pass.status_code}: {resp_no_pass.text}"

    # Positive: Signup
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json(), "Signup response should contain token"
    token = resp.json()["token"]

    # Verification: GET /user/me
    me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Positive: Login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json(), "Login response should contain token"

    # Negative: Login with wrong password
    resp_wrong = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_wrong.status_code == 400, f"Expected 400, got {resp_wrong.status_code}: {resp_wrong.text}"

# --- id=304  name='User Me' ---
def test_user_get_me():
    username, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert data["user"] == username, "User info should match the logged-in user"
    assert "name" in data
    assert "enabled" in data

    # Negative: Missing token
    resp_unauth = requests.get(me_url, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

    # Negative: Invalid token
    resp_invalid = requests.get(me_url, headers={"Authorization": "Bearer invalidtoken123"}, timeout=10)
    assert resp_invalid.status_code == 401, f"Expected 401, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=305  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0, "Newly created wallet should have balance 0"
    assert "address" in data
    address = data["address"]

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0, "Balance should be greater than 0 after topup"
    assert topup_data["address"] == address
    new_balance = topup_data["balance"]

    # Verification
    resp_check = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert resp_check.json()["balance"] == new_balance, "Balance should match topup response"
    assert resp_check.json()["address"] == address

    # Negative: Top up again
    resp_conflict = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=306  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    balance_url = get_url("gateway", "/wallet/balance")
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    data_a = resp_a.json()
    balance_a = data_a["balance"]
    address_a = data_a["address"]
    assert balance_a >= 1, "Expected topup to provide at least 1 unit"

    _, _, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    data_b = resp_b.json()
    balance_b = data_b["balance"]
    address_b = data_b["address"]
    assert balance_b == 0

    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    assert resp_transfer.json()["balance"] == balance_a - transfer_amount
    assert resp_transfer.json()["address"] == address_a

    resp_a_after = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_after.json()["balance"] == balance_a - transfer_amount
    assert resp_a_after.json()["address"] == address_a

    resp_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_after.json()["balance"] == transfer_amount
    assert resp_b_after.json()["address"] == address_b

# --- id=307  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_a.json()["balance"]

    _, _, token_b = create_user_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative: Transfer negative amount
    resp_neg = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -5}, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    # Negative: Insufficient funds
    resp_insuf = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a + 100}, timeout=10)
    assert resp_insuf.status_code == 400, f"Expected 400, got {resp_insuf.status_code}: {resp_insuf.text}"

    # Negative: Missing required field
    resp_miss = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp_miss.status_code == 400, f"Expected 400, got {resp_miss.status_code}: {resp_miss.text}"

# --- id=308  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    data_a = resp_a.json()
    balance_a = data_a["balance"]
    address_a = data_a["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Transfer 0 to own address
    resp_noop = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert resp_noop.status_code == 200, f"Expected 200, got {resp_noop.status_code}: {resp_noop.text}"
    assert resp_noop.json()["balance"] == balance_a

    resp_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a_after.json()["balance"] == balance_a

# --- id=309  name='Wallet Unauthorized' ---
def test_wallet_unauthorized():
    username, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    address = resp.json()["address"]

    balance_url = get_url("gateway", "/wallet/balance")
    topup_url = get_url("gateway", "/wallet/topup")
    transfer_url = get_url("gateway", "/wallet/transfer")

    resp_balance = requests.get(balance_url, timeout=10)
    assert resp_balance.status_code == 401, f"Expected 401, got {resp_balance.status_code}: {resp_balance.text}"

    resp_topup = requests.get(topup_url, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    resp_transfer = requests.post(transfer_url, json={"to": address, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
