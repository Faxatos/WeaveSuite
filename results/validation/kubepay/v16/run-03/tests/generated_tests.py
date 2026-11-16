# Tests generated in iteration 03
# Captured: 2026-06-14T12:27:50
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=768  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{generate_random_string()}"
    password = generate_random_string(12)

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token, "Token missing from signup response"

    # Verify user creation
    me_url = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(me_url, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == username

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token, "Token missing from login response"

    # Verify login token works
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me_login = requests.get(me_url, headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json().get("user") == username

# --- id=769  name='Wallet Topup And Balance' ---
def test_wallet_topup_and_balance():
    _, _, token = create_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Check initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == 0

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    new_balance = resp_topup.json().get("balance")
    assert new_balance > 0, "Balance should be greater than 0 after topup"

    # Verify balance updated
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance

    # Negative test: Topup again should fail
    resp_topup2 = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=770  name='Wallet Transfer Cumulative' ---
def test_wallet_transfer_cumulative():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")
    assert address_b, "Address missing for user B"

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup_a = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    initial_balance_a = resp_topup_a.json().get("balance")

    # Verify topup A
    resp_bal_a_initial = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a_initial.status_code == 200, f"Expected 200, got {resp_bal_a_initial.status_code}: {resp_bal_a_initial.text}"

    # Transfer 1: A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount_1 = 10
    resp_trans1 = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount_1}, timeout=10)
    assert resp_trans1.status_code == 200, f"Expected 200, got {resp_trans1.status_code}: {resp_trans1.text}"

    # Verify A's balance after transfer 1
    resp_bal_a_mid = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a_mid.status_code == 200, f"Expected 200, got {resp_bal_a_mid.status_code}: {resp_bal_a_mid.text}"

    # Transfer 2: A -> B
    transfer_amount_2 = 5
    resp_trans2 = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount_2}, timeout=10)
    assert resp_trans2.status_code == 200, f"Expected 200, got {resp_trans2.status_code}: {resp_trans2.text}"

    # Verify A's balance after transfer 2
    resp_bal_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    expected_balance_a = initial_balance_a - transfer_amount_1 - transfer_amount_2
    assert resp_bal_a.json().get("balance") == expected_balance_a

    # Verify B's balance
    resp_bal_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    expected_balance_b = transfer_amount_1 + transfer_amount_2
    assert resp_bal_b2.json().get("balance") == expected_balance_b

# --- id=771  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Transfer A -> B without topup
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_trans = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 100}, timeout=10)
    assert resp_trans.status_code == 400, f"Expected 400, got {resp_trans.status_code}: {resp_trans.text}"

# --- id=772  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get B's address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json().get("address")

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    # Verify topup
    resp_bal_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"

    # Transfer A -> B with negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_trans = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -10}, timeout=10)
    assert resp_trans.status_code == 400, f"Expected 400, got {resp_trans.status_code}: {resp_trans.text}"

# --- id=773  name='Wallet Transfer Self Noop' ---
def test_wallet_transfer_self_noop():
    _, _, token_a = create_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    address_a = resp_topup.json().get("address")
    balance_a = resp_topup.json().get("balance")

    # Verify topup
    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"

    # Transfer A -> A
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_trans = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 10}, timeout=10)
    assert resp_trans.status_code == 200, f"Expected 200, got {resp_trans.status_code}: {resp_trans.text}"

    # Verify balance unchanged
    resp_bal = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    assert resp_bal.json().get("balance") == balance_a
