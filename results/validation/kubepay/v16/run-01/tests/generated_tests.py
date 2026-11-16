# Tests generated in iteration 01
# Captured: 2026-06-14T11:40:41
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=753  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    signup_resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]

    # Follow-up GET
    me_resp = requests.get(get_url("gateway", "/user/me"), headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username
    assert "password" not in me_resp.json()

    # Login
    login_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]

    # Follow-up GET
    me_resp2 = requests.get(get_url("gateway", "/user/me"), headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=754  name='Auth Login Invalid Credentials Negative' ---
def test_auth_login_invalid_credentials_negative():
    token, username, password = create_user_and_get_token()

    # Login with wrong password
    login_resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert login_resp.status_code == 400, f"Expected 400, got {login_resp.status_code}: {login_resp.text}"

# --- id=755  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    token_a, _, _ = create_user_and_get_token()
    token_b, _, _ = create_user_and_get_token()

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    # Follow-up GET for Topup
    bal_a_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert bal_a_resp.status_code == 200, f"Expected 200, got {bal_a_resp.status_code}: {bal_a_resp.text}"
    balance_a_initial = bal_a_resp.json()["balance"]
    assert balance_a_initial > 0

    # Get B's address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]
    balance_b_initial = bal_b_resp.json()["balance"]

    # Transfer
    transfer_amount = 10
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Follow-up GET for A
    bal_a_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert bal_a_resp2.status_code == 200, f"Expected 200, got {bal_a_resp2.status_code}: {bal_a_resp2.text}"
    assert bal_a_resp2.json()["balance"] == balance_a_initial - transfer_amount

    # Follow-up GET for B
    bal_b_resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert bal_b_resp2.status_code == 200, f"Expected 200, got {bal_b_resp2.status_code}: {bal_b_resp2.text}"
    assert bal_b_resp2.json()["balance"] == balance_b_initial + transfer_amount

# --- id=756  name='Wallet Transfer Multiple Times' ---
def test_wallet_transfer_multiple_times():
    token_a, _, _ = create_user_and_get_token()
    token_b, _, _ = create_user_and_get_token()

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    bal_a_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert bal_a_resp.status_code == 200, f"Expected 200, got {bal_a_resp.status_code}: {bal_a_resp.text}"
    balance_a_initial = bal_a_resp.json()["balance"]

    # Get B's address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]
    balance_b_initial = bal_b_resp.json()["balance"]

    # Transfer 1
    transfer_amount_1 = 5
    transfer_resp_1 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": transfer_amount_1},
        timeout=10
    )
    assert transfer_resp_1.status_code == 200, f"Expected 200, got {transfer_resp_1.status_code}: {transfer_resp_1.text}"

    # Follow-up GET for A
    bal_a_resp_1 = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert bal_a_resp_1.status_code == 200, f"Expected 200, got {bal_a_resp_1.status_code}: {bal_a_resp_1.text}"
    assert bal_a_resp_1.json()["balance"] == balance_a_initial - transfer_amount_1

    # Transfer 2
    transfer_amount_2 = 7
    transfer_resp_2 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": transfer_amount_2},
        timeout=10
    )
    assert transfer_resp_2.status_code == 200, f"Expected 200, got {transfer_resp_2.status_code}: {transfer_resp_2.text}"

    # Follow-up GET for A (cumulative)
    bal_a_resp_2 = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert bal_a_resp_2.status_code == 200, f"Expected 200, got {bal_a_resp_2.status_code}: {bal_a_resp_2.text}"
    assert bal_a_resp_2.json()["balance"] == balance_a_initial - transfer_amount_1 - transfer_amount_2

    # Follow-up GET for B (cumulative)
    bal_b_resp_2 = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert bal_b_resp_2.status_code == 200, f"Expected 200, got {bal_b_resp_2.status_code}: {bal_b_resp_2.text}"
    assert bal_b_resp_2.json()["balance"] == balance_b_initial + transfer_amount_1 + transfer_amount_2

# --- id=757  name='Wallet Topup Twice Negative' ---
def test_wallet_topup_twice_negative():
    token, _, _ = create_user_and_get_token()

    # First topup
    topup_resp_1 = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert topup_resp_1.status_code == 200, f"Expected 200, got {topup_resp_1.status_code}: {topup_resp_1.text}"

    # Follow-up GET
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] > 0

    # Second topup
    topup_resp_2 = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert topup_resp_2.status_code == 400, f"Expected 400, got {topup_resp_2.status_code}: {topup_resp_2.text}"

# --- id=758  name='Wallet Transfer Insufficient Funds Negative' ---
def test_wallet_transfer_insufficient_funds_negative():
    token_a, _, _ = create_user_and_get_token()
    token_b, _, _ = create_user_and_get_token()

    # Get B's address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    # Transfer from A (balance 0)
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": 100},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=759  name='Wallet Transfer Negative Amount Negative' ---
def test_wallet_transfer_negative_amount_negative():
    token_a, _, _ = create_user_and_get_token()
    token_b, _, _ = create_user_and_get_token()

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    # Follow-up GET
    bal_a_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert bal_a_resp.status_code == 200, f"Expected 200, got {bal_a_resp.status_code}: {bal_a_resp.text}"

    # Get B's address
    bal_b_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    address_b = bal_b_resp.json()["address"]

    # Transfer with negative amount
    transfer_resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": address_b, "amount": -10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=760  name='User Me Unauthorized Negative' ---
def test_user_me_unauthorized_negative():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
