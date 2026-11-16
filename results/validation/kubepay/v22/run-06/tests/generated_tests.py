# Tests generated in iteration 06
# Captured: 2026-06-16T10:35:54
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1512  name='Wallet Transfer Workflow' ---
def test_wallet_transfer_workflow():
    # 1. Create User A
    user_a = f"userA_{uuid.uuid4().hex[:8]}"
    pwd_a = "passA"
    resp_signup_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pwd_a}, timeout=10)
    assert resp_signup_a.status_code == 200, f"Expected 200, got {resp_signup_a.status_code}: {resp_signup_a.text}"
    token_a = resp_signup_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Create User B
    user_b = f"userB_{uuid.uuid4().hex[:8]}"
    pwd_b = "passB"
    resp_signup_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pwd_b}, timeout=10)
    assert resp_signup_b.status_code == 200, f"Expected 200, got {resp_signup_b.status_code}: {resp_signup_b.text}"
    token_b = resp_signup_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User A checks balance
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    info_a = resp_bal_a.json()
    assert info_a["balance"] == 0
    address_a = info_a["address"]

    # 4. User B checks balance
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    info_b = resp_bal_b.json()
    assert info_b["balance"] == 0
    address_b = info_b["address"]

    # 5. User A tops up
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    topup_info_a = resp_topup_a.json()
    assert topup_info_a["balance"] > 0
    assert topup_info_a["address"] == address_a
    balance_a_after_topup = topup_info_a["balance"]

    # 6. User A transfers to User B
    transfer_amount = balance_a_after_topup / 2.0
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_info_a = resp_transfer.json()
    assert transfer_info_a["balance"] == balance_a_after_topup - transfer_amount

    # 7. Verify User A balance via GET
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a_after_topup - transfer_amount

    # 8. Verify User B balance via GET
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == transfer_amount

    # 9. Transfer 0 amount (no-op)
    resp_transfer_zero = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer_zero.status_code == 200, f"Expected 200, got {resp_transfer_zero.status_code}: {resp_transfer_zero.text}"
    assert resp_transfer_zero.json()["balance"] == balance_a_after_topup - transfer_amount

    # 10. Transfer to own address (no-op)
    resp_transfer_own = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": 10},
        timeout=10
    )
    assert resp_transfer_own.status_code == 200, f"Expected 200, got {resp_transfer_own.status_code}: {resp_transfer_own.text}"
    assert resp_transfer_own.json()["balance"] == balance_a_after_topup - transfer_amount

# --- id=1513  name='User Info Workflow' ---
def test_user_info_workflow():
    user_name = f"user_{uuid.uuid4().hex[:8]}"
    password = "secure_password"

    # 1. Signup
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_name, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # 2. Login
    resp_login = requests.post(get_url("gateway", "/auth/login"), json={"user": user_name, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Get User Info
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    user_info = resp_me.json()
    assert user_info["user"] == user_name
    assert "name" in user_info
    assert "enabled" in user_info

    # 4. Unauthorized access
    resp_unauth = requests.get(get_url("gateway", "/user/me"), headers={"Authorization": "Bearer invalid_token"}, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=1514  name='Wallet Negative Scenarios' ---
def test_wallet_negative_scenarios():
    user_a = f"userA_{uuid.uuid4().hex[:8]}"
    pwd_a = "passA"
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pwd_a}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    token_a = resp_signup.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Topup once
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance = resp_topup.json()["balance"]

    # Topup twice -> 400
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json()

    # Transfer negative amount -> 400
    resp_transfer_neg = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "some_address", "amount": -10},
        timeout=10
    )
    assert resp_transfer_neg.status_code == 400, f"Expected 400, got {resp_transfer_neg.status_code}: {resp_transfer_neg.text}"
    assert "message" in resp_transfer_neg.json()

    # Create user B to get a valid address
    user_b = f"userB_{uuid.uuid4().hex[:8]}"
    resp_signup_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp_signup_b.status_code == 200, f"Expected 200, got {resp_signup_b.status_code}: {resp_signup_b.text}"
    token_b = resp_signup_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    # Transfer more than balance -> 400
    resp_transfer_insufficient = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance + 100},
        timeout=10
    )
    assert resp_transfer_insufficient.status_code == 400, f"Expected 400, got {resp_transfer_insufficient.status_code}: {resp_transfer_insufficient.text}"
    assert "message" in resp_transfer_insufficient.json()

    # Transfer to invalid address -> 400
    resp_transfer_invalid_addr = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": "invalid_address_123", "amount": 1},
        timeout=10
    )
    assert resp_transfer_invalid_addr.status_code == 400, f"Expected 400, got {resp_transfer_invalid_addr.status_code}: {resp_transfer_invalid_addr.text}"
    assert "message" in resp_transfer_invalid_addr.json()

    # Missing auth token -> 401
    resp_transfer_unauth = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": address_b, "amount": 1},
        timeout=10
    )
    assert resp_transfer_unauth.status_code == 401, f"Expected 401, got {resp_transfer_unauth.status_code}: {resp_transfer_unauth.text}"

# --- id=1515  name='Auth Negative Scenarios' ---
def test_auth_negative_scenarios():
    user_name = f"user_{uuid.uuid4().hex[:8]}"
    password = "secure_password"

    # Signup with missing password
    resp_signup_bad = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_name}, timeout=10)
    assert resp_signup_bad.status_code == 400, f"Expected 400, got {resp_signup_bad.status_code}: {resp_signup_bad.text}"
    assert "message" in resp_signup_bad.json()

    # Successful signup
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_name, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    # Login with wrong password
    resp_login_bad = requests.post(get_url("gateway", "/auth/login"), json={"user": user_name, "password": "wrong_password"}, timeout=10)
    assert resp_login_bad.status_code == 400, f"Expected 400, got {resp_login_bad.status_code}: {resp_login_bad.text}"
    assert "message" in resp_login_bad.json()
