# Tests generated in iteration 06
# Captured: 2026-06-14T20:21:06
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=963  name='Wallet Transfer Recipient Not Found Bad Request' ---
def test_wallet_transfer_recipient_not_found_bad_request():
    token_a, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    # Transfer to non-existent wallet
    transfer_payload = {"to": "non_existent_address_12345", "amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=964  name='Wallet Transfer Unauthorized' ---
def test_wallet_transfer_unauthorized():
    transfer_payload = {"to": "some_address", "amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=965  name='Wallet Balance Unauthorized' ---
def test_wallet_balance_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=966  name='Wallet Topup Unauthorized' ---
def test_wallet_topup_unauthorized():
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=953  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json={"user": username, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # Verify signup
    token = resp_signup.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == username

    # Login
    resp_login = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Verify login token works
    login_token = resp_login.json()["token"]
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == username

# --- id=954  name='Auth Signup Bad Request' ---
def test_auth_signup_bad_request():
    username = f"user_{uuid.uuid4().hex[:8]}"
    # Missing password
    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=955  name='Auth Login Bad Request' ---
def test_auth_login_bad_request():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "wrongpassword"
    resp = requests.post(get_url("gateway", "/auth/login"), json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=956  name='User Me Unauthorized' ---
def test_user_me_unauthorized():
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=957  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    token, _ = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json()["balance"] == 0
    address = resp_bal.json()["address"]

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    new_balance = resp_topup.json()["balance"]
    assert new_balance > 0
    assert resp_topup.json()["address"] == address

    # Verify topup
    resp_bal_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal_after.status_code == 200, f"Expected 200, got {resp_bal_after.status_code}: {resp_bal_after.text}"
    assert resp_bal_after.json()["balance"] == new_balance

# --- id=958  name='Wallet Topup Twice Bad Request' ---
def test_wallet_topup_twice_bad_request():
    token, _ = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First topup
    resp_topup1 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup1.status_code == 200, f"Expected 200, got {resp_topup1.status_code}: {resp_topup1.text}"

    # Second topup
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=959  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    token_a, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, _ = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a_initial = resp_topup_a.json()["balance"]

    # Get B's address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b_initial = resp_bal_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = 10
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's balance in response
    assert resp_transfer.json()["balance"] == balance_a_initial - transfer_amount

    # Verify A's balance with GET
    resp_bal_a_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a_after.status_code == 200, f"Expected 200, got {resp_bal_a_after.status_code}: {resp_bal_a_after.text}"
    assert resp_bal_a_after.json()["balance"] == balance_a_initial - transfer_amount

    # Verify B's balance with GET
    resp_bal_b_after = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b_after.status_code == 200, f"Expected 200, got {resp_bal_b_after.status_code}: {resp_bal_b_after.text}"
    assert resp_bal_b_after.json()["balance"] == balance_b_initial + transfer_amount

# --- id=960  name='Wallet Transfer Missing Fields Bad Request' ---
def test_wallet_transfer_missing_fields_bad_request():
    token_a, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Missing 'to'
    transfer_payload = {"amount": 10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=961  name='Wallet Transfer Negative Amount Bad Request' ---
def test_wallet_transfer_negative_amount_bad_request():
    token_a, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, _ = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    # Negative amount
    transfer_payload = {"to": address_b, "amount": -10}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=962  name='Wallet Transfer Insufficient Funds Bad Request' ---
def test_wallet_transfer_insufficient_funds_bad_request():
    token_a, _ = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b, _ = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_bal_b.json()["address"]

    # Insufficient funds (balance is 0)
    transfer_payload = {"to": address_b, "amount": 100}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
