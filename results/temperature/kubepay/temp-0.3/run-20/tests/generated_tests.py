# Tests generated in iteration 20
# Captured: 2026-07-02T09:10:02
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=635  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()
    token = signup_resp.json()["token"]

    # Verify signup via /user/me
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    # Negative: Signup with same username
    signup_resp_conflict = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp_conflict.status_code == 400, f"Expected 400, got {signup_resp_conflict.status_code}: {signup_resp_conflict.text}"

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()

    # Negative: Login with wrong password
    bad_login_resp = requests.post(login_url, json={"user": username, "password": "wrongpassword"}, timeout=10)
    assert bad_login_resp.status_code == 400, f"Expected 400, got {bad_login_resp.status_code}: {bad_login_resp.text}"

# --- id=636  name='User Me' ---
def test_user_me():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["user"] == username
    assert "name" in me_data
    assert "enabled" in me_data

    # Negative: Without token
    unauth_resp = requests.get(me_url, timeout=10)
    assert unauth_resp.status_code == 401, f"Expected 401, got {unauth_resp.status_code}: {unauth_resp.text}"

# --- id=637  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    balance_data = balance_resp.json()
    assert balance_data["balance"] == 0
    address = balance_data["address"]
    assert address is not None

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == address
    new_balance = topup_data["balance"]

    # Verify balance
    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json()["balance"] == new_balance

    # Negative: Topup again
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

    # Negative: Topup without token
    topup_unauth = requests.get(topup_url, timeout=10)
    assert topup_unauth.status_code == 401, f"Expected 401, got {topup_unauth.status_code}: {topup_unauth.text}"

# --- id=638  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # User A
    user_a = "usera_" + "".join(random.choices(string.ascii_lowercase, k=8))
    signup_resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert signup_resp_a.status_code == 200, f"Expected 200, got {signup_resp_a.status_code}: {signup_resp_a.text}"
    token_a = signup_resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = "userb_" + "".join(random.choices(string.ascii_lowercase, k=8))
    signup_resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert signup_resp_b.status_code == 200, f"Expected 200, got {signup_resp_b.status_code}: {signup_resp_b.text}"
    token_b = signup_resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    topup_resp_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a_initial = topup_resp_a.json()["balance"]

    # Get User B address
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]
    balance_b_initial = balance_resp_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    transfer_data = transfer_resp.json()
    assert transfer_data["balance"] == balance_a_initial - transfer_amount

    # Verify A balance
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json()["balance"] == balance_a_initial - transfer_amount

    # Verify B balance
    balance_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b2.status_code == 200, f"Expected 200, got {balance_resp_b2.status_code}: {balance_resp_b2.text}"
    assert balance_resp_b2.json()["balance"] == balance_b_initial + transfer_amount

    # Transfer 0 (no-op)
    transfer_resp_0 = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 0}, timeout=10)
    assert transfer_resp_0.status_code == 200, f"Expected 200, got {transfer_resp_0.status_code}: {transfer_resp_0.text}"
    assert transfer_resp_0.json()["balance"] == balance_a_initial - transfer_amount

# --- id=639  name='Wallet Transfer Negative' ---
def test_wallet_transfer_negative():
    # User A
    user_a = "usera_" + "".join(random.choices(string.ascii_lowercase, k=8))
    signup_resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert signup_resp_a.status_code == 200, f"Expected 200, got {signup_resp_a.status_code}: {signup_resp_a.text}"
    token_a = signup_resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b = "userb_" + "".join(random.choices(string.ascii_lowercase, k=8))
    signup_resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert signup_resp_b.status_code == 200, f"Expected 200, got {signup_resp_b.status_code}: {signup_resp_b.text}"
    token_b = signup_resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    topup_resp_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a_initial = topup_resp_a.json()["balance"]

    # Get User B address
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # Negative amount
    resp_neg = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    # Insufficient funds
    resp_insufficient = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": balance_a_initial + 100}, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Recipient not found
    resp_not_found = requests.post(transfer_url, headers=headers_a, json={"to": "non_existent_address", "amount": 10}, timeout=10)
    assert resp_not_found.status_code == 400, f"Expected 400, got {resp_not_found.status_code}: {resp_not_found.text}"

    # Missing required field 'to'
    resp_missing_to = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp_missing_to.status_code == 400, f"Expected 400, got {resp_missing_to.status_code}: {resp_missing_to.text}"

    # Missing required field 'amount'
    resp_missing_amount = requests.post(transfer_url, headers=headers_a, json={"to": address_b}, timeout=10)
    assert resp_missing_amount.status_code == 400, f"Expected 400, got {resp_missing_amount.status_code}: {resp_missing_amount.text}"

    # Unauthorized
    resp_unauth = requests.post(transfer_url, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"
