# Tests generated in iteration 04
# Captured: 2026-06-15T09:49:44
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1191  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "pwd_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

    # Signup
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()
    token = resp.json()["token"]

    # Follow-up GET
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Negative: Wrong password
    resp_bad = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password + "bad"},
        timeout=10
    )
    assert resp_bad.status_code == 400, f"Expected 400, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=1192  name='User Me' ---
def test_user_me():
    username, password, token = register_user()

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

    # Negative: No token
    resp_unauth = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=1193  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username, password, token = register_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["balance"] == 0
    address = data["address"]
    assert address is not None

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address
    assert topup_data["balance"] > 0
    new_balance = topup_data["balance"]

    # Verify balance
    resp_check = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_check.status_code == 200, f"Expected 200, got {resp_check.status_code}: {resp_check.text}"
    assert resp_check.json()["balance"] == new_balance

    # Negative: Topup again
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1194  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    _, _, token_a = register_user()
    _, _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    # Get B address
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]
    balance_b = resp_b.json()["balance"]

    transfer_amount = balance_a / 2.0 if balance_a > 0 else 0
    if transfer_amount == 0:
        transfer_amount = 10.0

    # Transfer A -> B
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_data = resp_transfer.json()
    assert transfer_data["balance"] == balance_a - transfer_amount

    # Follow-up GET A balance
    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET B balance
    resp_check_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_check_b.status_code == 200, f"Expected 200, got {resp_check_b.status_code}: {resp_check_b.text}"
    assert resp_check_b.json()["balance"] == balance_b + transfer_amount

# --- id=1195  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = register_user()
    _, _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B address
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    # Transfer A -> B (A has 0 balance)
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 100.0},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up GET A balance to ensure it didn't change
    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == 0

# --- id=1196  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json()["balance"]

    # Transfer A -> invalid
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 1.0},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up GET A balance to ensure it didn't change
    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == balance_a

# --- id=1197  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = register_user()
    _, _, token_b = register_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json()["balance"]

    # Get B address
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    # Transfer A -> B negative amount
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -50.0},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Follow-up GET A balance to ensure it didn't change
    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == balance_a

# --- id=1198  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    _, _, token_a = register_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a = resp_topup.json()["balance"]
    address_a = resp_topup.json()["address"]

    # Transfer A -> A
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10.0},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a

    # Follow-up GET A balance
    resp_check_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a.status_code == 200, f"Expected 200, got {resp_check_a.status_code}: {resp_check_a.text}"
    assert resp_check_a.json()["balance"] == balance_a

    # Transfer amount 0
    _, _, token_b = register_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_b.json()["address"]

    resp_transfer_0 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0.0},
        timeout=10
    )
    assert resp_transfer_0.status_code == 200, f"Expected 200, got {resp_transfer_0.status_code}: {resp_transfer_0.text}"
    assert resp_transfer_0.json()["balance"] == balance_a

    # Follow-up GET A balance
    resp_check_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_check_a2.status_code == 200, f"Expected 200, got {resp_check_a2.status_code}: {resp_check_a2.text}"
    assert resp_check_a2.json()["balance"] == balance_a
