# Tests generated in iteration 05
# Captured: 2026-07-10T23:05:13
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=20  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = generate_random_string()
    password = generate_random_string()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    signup_data = signup_resp.json()
    assert "token" in signup_data

    # Verify signup with /user/me
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {signup_data['token']}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_data = login_resp.json()
    assert "token" in login_data

    # Verify login token works
    headers_login = {"Authorization": f"Bearer {login_data['token']}"}
    me_resp2 = requests.get(me_url, headers=headers_login, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json().get("user") == username

# --- id=21  name='Auth Signup Missing Password' ---
def test_auth_signup_missing_password():
    username = generate_random_string()
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert signup_resp.status_code == 400, f"Expected 400, got {signup_resp.status_code}: {signup_resp.text}"

# --- id=22  name='User Me' ---
def test_user_get_me():
    username = generate_random_string()
    password = generate_random_string()

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]

    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data.get("user") == username
    assert "name" in me_data
    assert "enabled" in me_data

# --- id=23  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    username = generate_random_string()
    password = generate_random_string()

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    token = signup_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    balance_resp = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp.status_code == 200, f"Expected 200, got {balance_resp.status_code}: {balance_resp.text}"
    initial_balance = balance_resp.json().get("balance", 0)

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    topup_data = topup_resp.json()
    assert "balance" in topup_data
    assert topup_data["balance"] > initial_balance

    balance_resp2 = requests.get(balance_url, headers=headers, timeout=10)
    assert balance_resp2.status_code == 200, f"Expected 200, got {balance_resp2.status_code}: {balance_resp2.text}"
    assert balance_resp2.json()["balance"] == topup_data["balance"]

# --- id=24  name='Wallet Transfer' ---
def test_wallet_transfer():
    # User A
    user_a = generate_random_string()
    pass_a = generate_random_string()
    signup_resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    assert signup_resp_a.status_code == 200, f"Expected 200, got {signup_resp_a.status_code}: {signup_resp_a.text}"
    token_a = signup_resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Verify User A creation
    me_resp_a = requests.get(get_url("gateway", "/user/me"), headers=headers_a, timeout=10)
    assert me_resp_a.status_code == 200, f"Expected 200, got {me_resp_a.status_code}: {me_resp_a.text}"

    # User B
    user_b = generate_random_string()
    pass_b = generate_random_string()
    signup_resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pass_b}, timeout=10)
    assert signup_resp_b.status_code == 200, f"Expected 200, got {signup_resp_b.status_code}: {signup_resp_b.text}"
    token_b = signup_resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Verify User B creation
    me_resp_b = requests.get(get_url("gateway", "/user/me"), headers=headers_b, timeout=10)
    assert me_resp_b.status_code == 200, f"Expected 200, got {me_resp_b.status_code}: {me_resp_b.text}"

    # Get User B address
    balance_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b.status_code == 200, f"Expected 200, got {balance_resp_b.status_code}: {balance_resp_b.text}"
    address_b = balance_resp_b.json().get("address")
    initial_balance_b = balance_resp_b.json().get("balance", 0)

    # Topup User A
    topup_resp_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp_a.status_code == 200, f"Expected 200, got {topup_resp_a.status_code}: {topup_resp_a.text}"
    balance_a_before = topup_resp_a.json().get("balance", 0)

    # Transfer A -> B
    transfer_amount = 1
    transfer_url = get_url("gateway", "/wallet/transfer")
    target = address_b if address_b else user_b
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": target, "amount": transfer_amount}, timeout=10)
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"

    # Check A balance
    balance_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert balance_resp_a2.status_code == 200, f"Expected 200, got {balance_resp_a2.status_code}: {balance_resp_a2.text}"
    assert balance_resp_a2.json()["balance"] == balance_a_before - transfer_amount

    # Check B balance
    balance_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert balance_resp_b2.status_code == 200, f"Expected 200, got {balance_resp_b2.status_code}: {balance_resp_b2.text}"
    assert balance_resp_b2.json()["balance"] == initial_balance_b + transfer_amount

# --- id=25  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = generate_random_string()
    pass_a = generate_random_string()
    signup_resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    assert signup_resp_a.status_code == 200, f"Expected 200, got {signup_resp_a.status_code}: {signup_resp_a.text}"
    token_a = signup_resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Verify User A creation
    me_resp_a = requests.get(get_url("gateway", "/user/me"), headers=headers_a, timeout=10)
    assert me_resp_a.status_code == 200, f"Expected 200, got {me_resp_a.status_code}: {me_resp_a.text}"

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"to": "someone", "amount": -10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=26  name='Wallet Transfer Missing To' ---
def test_wallet_transfer_missing_to():
    user_a = generate_random_string()
    pass_a = generate_random_string()
    signup_resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pass_a}, timeout=10)
    assert signup_resp_a.status_code == 200, f"Expected 200, got {signup_resp_a.status_code}: {signup_resp_a.text}"
    token_a = signup_resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(transfer_url, headers=headers_a, json={"amount": 10}, timeout=10)
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"
