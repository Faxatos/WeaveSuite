# Tests generated in iteration 01
# Captured: 2026-07-03T08:54:02
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1000  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    assert isinstance(token, str) and len(token) > 0

    user_me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(user_me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    user_info = resp_me.json()
    assert user_info["user"] == user

# --- id=1001  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "wrongpassword"

    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"
    assert "message" in resp_login.json()

# --- id=1002  name='Wallet Topup And Transfer Success' ---
def test_wallet_topup_and_transfer_success():
    user_a, _, token_a = create_user_and_login()
    user_b, _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")

    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    wallet_a = resp_a.json()
    assert wallet_a["balance"] == 0
    address_a = wallet_a["address"]

    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    wallet_b = resp_b.json()
    assert wallet_b["balance"] == 0
    address_b = wallet_b["address"]

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    wallet_a_topped_up = resp_topup.json()
    assert wallet_a_topped_up["balance"] > 0
    assert wallet_a_topped_up["address"] == address_a
    topup_amount = wallet_a_topped_up["balance"]

    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    wallet_a_after_transfer = resp_transfer.json()
    assert wallet_a_after_transfer["balance"] == topup_amount - transfer_amount
    assert wallet_a_after_transfer["address"] == address_a

    resp_b_after = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_after.status_code == 200, f"Expected 200, got {resp_b_after.status_code}: {resp_b_after.text}"
    wallet_b_after = resp_b_after.json()
    assert wallet_b_after["balance"] == transfer_amount
    assert wallet_b_after["address"] == address_b

# --- id=1003  name='Wallet Topup Twice Fails' ---
def test_wallet_topup_twice_fails():
    _, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")

    resp1 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"
    assert "message" in resp2.json()

# --- id=1004  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=1005  name='Wallet Transfer Invalid Address' ---
def test_wallet_transfer_invalid_address():
    _, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers, json={"to": "invalid_address_123", "amount": 1}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=1006  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user_and_login()
    _, _, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -5}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=1007  name='Wallet Transfer Missing Required Field' ---
def test_wallet_transfer_missing_required_field():
    _, _, token_a = create_user_and_login()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert "message" in resp_transfer.json()

# --- id=1008  name='Wallet Transfer Noop Self' ---
def test_wallet_transfer_noop_self():
    _, _, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    wallet = resp_balance.json()
    address = wallet["address"]
    initial_balance = wallet["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, headers=headers, json={"to": address, "amount": 0}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    updated_wallet = resp_transfer.json()
    assert updated_wallet["balance"] == initial_balance

# --- id=1009  name='Unauthorized Access' ---
def test_unauthorized_access():
    user_me_url = get_url("gateway", "/user/me")
    resp_me = requests.get(user_me_url, timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

    balance_url = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(balance_url, timeout=10)
    assert resp_balance.status_code == 401, f"Expected 401, got {resp_balance.status_code}: {resp_balance.text}"

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(transfer_url, json={"to": "dummy", "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
