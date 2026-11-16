# Tests generated in iteration 09
# Captured: 2026-07-01T20:38:17
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=357  name='Auth And User Profile' ---
def test_auth_and_user_profile():
    user, password = generate_user()

    # Signup
    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": user, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()

    # Login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": user, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]

    # Get User Profile
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    user_info = me_resp.json()
    assert user_info["user"] == user
    assert "enabled" in user_info

    # Get Wallet Balance
    bal_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(bal_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    wallet_info = bal_resp.json()
    assert wallet_info["balance"] == 0
    assert "address" in wallet_info

# --- id=358  name='Wallet Topup And Duplicate' ---
def test_wallet_topup_and_duplicate():
    _, _, token, _ = setup_user()

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    wallet_info = topup_resp.json()
    new_balance = wallet_info["balance"]
    assert new_balance > 0

    # Verify Balance
    bal_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(bal_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] == new_balance

    # Duplicate Topup
    dup_resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert dup_resp.status_code == 400, f"Expected 400, got {dup_resp.status_code}: {dup_resp.text}"

    # Balance unchanged
    bal_resp2 = requests.get(bal_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

# --- id=359  name='Wallet Transfer Positive' ---
def test_wallet_transfer_positive():
    # Setup User A and Topup
    _, _, token_a, addr_a = setup_user()
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a_initial = topup_resp.json()["balance"]

    # Setup User B
    _, _, token_b, addr_b = setup_user()

    # Transfer A -> B
    transfer_amount = balance_a_initial / 2.0
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(
        transfer_url, 
        headers={"Authorization": f"Bearer {token_a}"}, 
        json={"to": addr_b, "amount": transfer_amount},
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    wallet_a_updated = transfer_resp.json()
    assert wallet_a_updated["balance"] == balance_a_initial - transfer_amount

    # Verify User A Balance
    bal_url = get_url("gateway", "/wallet/balance")
    bal_a_resp = requests.get(bal_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert bal_a_resp.status_code == 200, f"Expected 200, got {bal_a_resp.status_code}: {bal_a_resp.text}"
    assert bal_a_resp.json()["balance"] == balance_a_initial - transfer_amount

    # Verify User B Balance
    bal_b_resp = requests.get(bal_url, headers={"Authorization": f"Bearer {token_b}"}, timeout=10)
    assert bal_b_resp.status_code == 200, f"Expected 200, got {bal_b_resp.status_code}: {bal_b_resp.text}"
    assert bal_b_resp.json()["balance"] == transfer_amount

    # Transfer 0 to self (no-op)
    transfer_self_resp = requests.post(
        transfer_url,
        headers={"Authorization": f"Bearer {token_a}"},
        json={"to": addr_a, "amount": 0},
        timeout=10
    )
    assert transfer_self_resp.status_code == 200, f"Expected 200, got {transfer_self_resp.status_code}: {transfer_self_resp.text}"
    assert transfer_self_resp.json()["balance"] == balance_a_initial - transfer_amount

# --- id=360  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a, addr_a = setup_user()
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    _, _, token_b, addr_b = setup_user()

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(
        transfer_url, 
        headers={"Authorization": f"Bearer {token_a}"}, 
        json={"to": addr_b, "amount": balance_a + 100},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

    bal_url = get_url("gateway", "/wallet/balance")
    bal_a_resp = requests.get(bal_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)
    assert bal_a_resp.status_code == 200, f"Expected 200, got {bal_a_resp.status_code}: {bal_a_resp.text}"
    assert bal_a_resp.json()["balance"] == balance_a

# --- id=361  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a, addr_a = setup_user()
    _, _, token_b, addr_b = setup_user()

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(
        transfer_url, 
        headers={"Authorization": f"Bearer {token_a}"}, 
        json={"to": addr_b, "amount": -10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=362  name='Wallet Transfer Missing Recipient' ---
def test_wallet_transfer_missing_recipient():
    _, _, token_a, addr_a = setup_user()
    topup_url = get_url("gateway", "/wallet/topup")
    requests.get(topup_url, headers={"Authorization": f"Bearer {token_a}"}, timeout=10)

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(
        transfer_url, 
        headers={"Authorization": f"Bearer {token_a}"}, 
        json={"to": f"non_existent_{uuid.uuid4().hex}", "amount": 10},
        timeout=10
    )
    assert transfer_resp.status_code == 400, f"Expected 400, got {transfer_resp.status_code}: {transfer_resp.text}"

# --- id=363  name='Unauthorized Access' ---
def test_unauthorized_access():
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, timeout=10)
    assert me_resp.status_code == 401, f"Expected 401, got {me_resp.status_code}: {me_resp.text}"

    bal_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(bal_url, headers={"Authorization": "Bearer invalid_token"}, timeout=10)
    assert bal_resp.status_code == 401, f"Expected 401, got {bal_resp.status_code}: {bal_resp.text}"
