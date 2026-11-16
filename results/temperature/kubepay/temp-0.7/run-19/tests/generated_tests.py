# Tests generated in iteration 19
# Captured: 2026-07-02T00:32:13
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=444  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    # Signup
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token, "Token missing in signup response"

    # Login
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_token = resp.json().get("token")
    assert login_token, "Token missing in login response"

    # Verify user state via User Service
    headers = {"Authorization": f"Bearer {login_token}"}
    resp = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_info = resp.json()
    assert user_info.get("user") == username
    assert "name" in user_info
    assert "enabled" in user_info

# --- id=445  name='Auth Signup Duplicate' ---
def test_auth_signup_duplicate():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=446  name='Auth Login Invalid' ---
def test_auth_login_invalid():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=447  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=448  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance check
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    wallet_info = resp.json()
    assert "address" in wallet_info
    assert wallet_info.get("balance") == 0
    address = wallet_info["address"]

    # Perform topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    topup_info = resp.json()
    assert topup_info.get("address") == address
    new_balance = topup_info.get("balance")
    assert new_balance > 0

    # Verify state via follow-up GET
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == new_balance

# --- id=449  name='Wallet Topup Repetition' ---
def test_wallet_topup_repetition():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Password123!"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=450  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    # Setup User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    token_a = resp.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    token_b = resp.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    addr_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10).json()["address"]
    addr_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()["address"]

    # Topup User A
    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a_initial = resp.json()["balance"]
    assert balance_a_initial > 0, "Topup should result in positive balance"

    transfer_amount = round(balance_a_initial / 2.0, 2)

    # Transfer funds
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": addr_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    transfer_info = resp.json()
    assert transfer_info["address"] == addr_a

    expected_balance_a = round(balance_a_initial - transfer_amount, 2)
    assert round(transfer_info["balance"], 2) == expected_balance_a

    # Verify User A balance via GET
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert round(resp.json()["balance"], 2) == expected_balance_a

    # Verify User B balance via GET
    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert round(resp.json()["balance"], 2) == transfer_amount

# --- id=451  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    headers_a = {"Authorization": f"Bearer {resp.json()['token']}"}

    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    headers_b = {"Authorization": f"Bearer {resp.json()['token']}"}

    addr_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()["address"]

    # User A has 0 balance
    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": addr_b, "amount": 10.0},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=452  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    headers_a = {"Authorization": f"Bearer {resp.json()['token']}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_12345", "amount": 1.0},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=453  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    headers_a = {"Authorization": f"Bearer {resp.json()['token']}"}

    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    headers_b = {"Authorization": f"Bearer {resp.json()['token']}"}

    addr_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10).json()["address"]

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": addr_b, "amount": -5.0},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=454  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    headers_a = {"Authorization": f"Bearer {resp.json()['token']}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 1.0},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    addr_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10).json()["address"]

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": addr_a},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=455  name='Wallet Transfer Noop' ---
def test_wallet_transfer_noop():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    headers_a = {"Authorization": f"Bearer {resp.json()['token']}"}

    addr_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10).json()["address"]

    resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    balance_a = resp.json()["balance"]

    resp = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": addr_a, "amount": 0.0},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp.json()["balance"] == balance_a

# --- id=456  name='Wallet Unauthorized Access' ---
def test_wallet_unauthorized_access():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 1.0}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
