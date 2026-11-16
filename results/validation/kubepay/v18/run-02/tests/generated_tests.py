# Tests generated in iteration 02
# Captured: 2026-06-15T08:46:22
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1178  name='Unauthorized Access' ---
def test_unauthorized_access():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    real_address = resp_bal.json()["address"]

    resp_user = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_user.status_code == 401, f"Expected 401, got {resp_user.status_code}: {resp_user.text}"

    resp_bal_unauth = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp_bal_unauth.status_code == 401, f"Expected 401, got {resp_bal_unauth.status_code}: {resp_bal_unauth.text}"

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": real_address, "amount": 10.0},
        timeout=10
    )
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1167  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token = resp_signup.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

# --- id=1168  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_signup = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username},
        timeout=10
    )
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

# --- id=1169  name='Auth Login Wrong Password' ---
def test_auth_login_wrong_password():
    username, _, _ = create_user_and_get_token()

    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": "wrongpassword"},
        timeout=10
    )
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=1170  name='User Me' ---
def test_user_me():
    username, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=1171  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp_bal1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal1.status_code == 200, f"Expected 200, got {resp_bal1.status_code}: {resp_bal1.text}"
    data_bal1 = resp_bal1.json()
    assert data_bal1["balance"] == 0
    assert "address" in data_bal1

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    data_topup = resp_topup.json()
    assert data_topup["balance"] > 0
    topup_balance = data_topup["balance"]

    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == topup_balance

    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1172  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token1 = create_user_and_get_token()
    headers1 = {"Authorization": f"Bearer {token1}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers1, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    sender_initial_balance = resp_topup.json()["balance"]

    _, _, token2 = create_user_and_get_token()
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers2, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    recipient_address = resp_bal2.json()["address"]
    recipient_initial_balance = resp_bal2.json()["balance"]

    transfer_amount = sender_initial_balance / 2.0
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers1,
        json={"to": recipient_address, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == sender_initial_balance - transfer_amount

    resp_bal1_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers1, timeout=10)
    assert resp_bal1_after.status_code == 200, f"Expected 200, got {resp_bal1_after.status_code}: {resp_bal1_after.text}"
    assert resp_bal1_after.json()["balance"] == sender_initial_balance - transfer_amount

    resp_bal2_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers2, timeout=10)
    assert resp_bal2_after.status_code == 200, f"Expected 200, got {resp_bal2_after.status_code}: {resp_bal2_after.text}"
    assert resp_bal2_after.json()["balance"] == recipient_initial_balance + transfer_amount

# --- id=1173  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token1 = create_user_and_get_token()
    headers1 = {"Authorization": f"Bearer {token1}"}

    _, _, token2 = create_user_and_get_token()
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers2, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    recipient_address = resp_bal2.json()["address"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers1,
        json={"to": recipient_address, "amount": 100.0},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1174  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token1 = create_user_and_get_token()
    headers1 = {"Authorization": f"Bearer {token1}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers1, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    _, _, token2 = create_user_and_get_token()
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers2, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    recipient_address = resp_bal2.json()["address"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers1,
        json={"to": recipient_address, "amount": -50.0},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1175  name='Wallet Transfer Missing To Field' ---
def test_wallet_transfer_missing_to_field():
    _, _, token1 = create_user_and_get_token()
    headers1 = {"Authorization": f"Bearer {token1}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers1, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers1,
        json={"amount": 10.0},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=1176  name='Wallet Transfer Self Noop' ---
def test_wallet_transfer_self_noop():
    _, _, token1 = create_user_and_get_token()
    headers1 = {"Authorization": f"Bearer {token1}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers1, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    sender_balance = resp_topup.json()["balance"]
    sender_address = resp_topup.json()["address"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers1,
        json={"to": sender_address, "amount": 10.0},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == sender_balance

    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers1, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == sender_balance

# --- id=1177  name='Wallet Transfer Zero Amount Noop' ---
def test_wallet_transfer_zero_amount_noop():
    _, _, token1 = create_user_and_get_token()
    headers1 = {"Authorization": f"Bearer {token1}"}

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers1, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    sender_balance = resp_topup.json()["balance"]

    _, _, token2 = create_user_and_get_token()
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers2, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    recipient_address = resp_bal2.json()["address"]
    recipient_balance = resp_bal2.json()["balance"]

    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers1,
        json={"to": recipient_address, "amount": 0.0},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == sender_balance

    resp_bal1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers1, timeout=10)
    assert resp_bal1.status_code == 200, f"Expected 200, got {resp_bal1.status_code}: {resp_bal1.text}"
    assert resp_bal1.json()["balance"] == sender_balance

    resp_bal2_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers2, timeout=10)
    assert resp_bal2_after.status_code == 200, f"Expected 200, got {resp_bal2_after.status_code}: {resp_bal2_after.text}"
    assert resp_bal2_after.json()["balance"] == recipient_balance
