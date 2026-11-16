# Tests generated in iteration 06
# Captured: 2026-07-10T23:25:34
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=27  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    signup_url = get_url("gateway", "/auth/signup")

    # Negative: Missing required field
    resp_missing = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp_missing.status_code == 400, f"Expected 400, got {resp_missing.status_code}: {resp_missing.text}"

    # Positive: Signup
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Negative: Conflict / Duplicate user
    resp_conflict = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"

    login_url = get_url("gateway", "/auth/login")

    # Positive: Login
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Negative: Bad credentials
    resp_bad_login = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert resp_bad_login.status_code == 400, f"Expected 400, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=28  name='User Me' ---
def test_user_me():
    username, password, token = create_user_and_login()

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=29  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username, password, token = create_user_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    initial_balance = resp.json()["balance"]

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    new_balance = resp_topup.json()["balance"]
    assert new_balance > initial_balance

    resp_check = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert abs(resp_check.json()["balance"] - new_balance) < 1e-5

# --- id=30  name='Wallet Transfer' ---
def test_wallet_transfer():
    user_a, pass_a, token_a = create_user_and_login()
    user_b, pass_b, token_b = create_user_and_login()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json()["balance"]

    while balance_a < 1.0:
        resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
        assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
        balance_a = resp_topup.json()["balance"]

    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]
    balance_b = resp_b.json()["balance"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative: Missing required field
    payload_missing = {"amount": 1.0}
    resp_transfer_missing = requests.post(transfer_url, headers=headers_a, json=payload_missing, timeout=10)
    assert resp_transfer_missing.status_code == 400, f"Expected 400, got {resp_transfer_missing.status_code}: {resp_transfer_missing.text}"

    # Positive: Transfer funds
    transfer_amount = 1.0
    payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(transfer_url, headers=headers_a, json=payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify balances
    resp_a_check = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_check.status_code == 200, f"Expected 200, got {resp_a_check.status_code}: {resp_a_check.text}"
    assert abs(resp_a_check.json()["balance"] - (balance_a - transfer_amount)) < 1e-5

    resp_b_check = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b_check.status_code == 200, f"Expected 200, got {resp_b_check.status_code}: {resp_b_check.text}"
    assert abs(resp_b_check.json()["balance"] - (balance_b + transfer_amount)) < 1e-5

    # Negative: Transfer negative amount
    payload_neg = {"to": address_b, "amount": -1.0}
    resp_transfer_neg = requests.post(transfer_url, headers=headers_a, json=payload_neg, timeout=10)
    assert resp_transfer_neg.status_code == 400, f"Expected 400, got {resp_transfer_neg.status_code}: {resp_transfer_neg.text}"

    # Negative: Transfer more than balance
    payload_excess = {"to": address_b, "amount": balance_a + 1000.0}
    resp_transfer_excess = requests.post(transfer_url, headers=headers_a, json=payload_excess, timeout=10)
    assert resp_transfer_excess.status_code == 400, f"Expected 400, got {resp_transfer_excess.status_code}: {resp_transfer_excess.text}"
