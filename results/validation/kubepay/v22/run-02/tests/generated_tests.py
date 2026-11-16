# Tests generated in iteration 02
# Captured: 2026-06-16T09:24:09
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1500  name='Wallet Transfer Workflow' ---
def test_wallet_transfer_workflow():
    # 1. Signup User A
    user_a = f"userA_{uuid.uuid4().hex[:8]}"
    pwd_a = "passA123"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": pwd_a}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    token_a = resp_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Verify User A creation via /user/me
    resp_me_a = requests.get(get_url("gateway", "/user/me"), headers=headers_a, timeout=10)
    assert resp_me_a.status_code == 200, f"Expected 200, got {resp_me_a.status_code}: {resp_me_a.text}"
    assert resp_me_a.json()["user"] == user_a
    assert "name" in resp_me_a.json()
    assert "enabled" in resp_me_a.json()

    # 2. Signup User B
    user_b = f"userB_{uuid.uuid4().hex[:8]}"
    pwd_b = "passB123"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": pwd_b}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    token_b = resp_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Verify User B creation via /user/me
    resp_me_b = requests.get(get_url("gateway", "/user/me"), headers=headers_b, timeout=10)
    assert resp_me_b.status_code == 200, f"Expected 200, got {resp_me_b.status_code}: {resp_me_b.text}"
    assert resp_me_b.json()["user"] == user_b

    # 3. User A gets initial balance
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    bal_a_data = resp_bal_a.json()
    assert bal_a_data["balance"] == 0
    address_a = bal_a_data["address"]

    # 4. User B gets initial balance
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    bal_b_data = resp_bal_b.json()
    assert bal_b_data["balance"] == 0
    address_b = bal_b_data["address"]

    # 5. User A tops up
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == address_a
    topup_amount = topup_data["balance"]
    assert topup_amount > 0

    # Verify User A topup via /wallet/balance
    resp_bal_a_after_topup = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a_after_topup.status_code == 200, f"Expected 200, got {resp_bal_a_after_topup.status_code}: {resp_bal_a_after_topup.text}"
    assert resp_bal_a_after_topup.json()["balance"] == topup_amount
    assert resp_bal_a_after_topup.json()["address"] == address_a

    # 6. User A transfers to User B
    transfer_amount = topup_amount / 2
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_data = resp_transfer.json()
    assert transfer_data["address"] == address_a
    assert transfer_data["balance"] == topup_amount - transfer_amount

    # Verify User A balance via GET
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == topup_amount - transfer_amount

    # Verify User B balance via GET
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == transfer_amount

# --- id=1501  name='Wallet Transfer Failures' ---
def test_wallet_transfer_failures():
    # 1. Signup User C
    user_c = f"userC_{uuid.uuid4().hex[:8]}"
    pwd_c = "passC123"
    resp_c = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_c, "password": pwd_c}, timeout=10)
    assert resp_c.status_code == 200, f"Expected 200, got {resp_c.status_code}: {resp_c.text}"
    token_c = resp_c.json()["token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    # Verify User C creation via /user/me
    resp_me_c = requests.get(get_url("gateway", "/user/me"), headers=headers_c, timeout=10)
    assert resp_me_c.status_code == 200, f"Expected 200, got {resp_me_c.status_code}: {resp_me_c.text}"

    # 2. Get initial balance and address
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_c, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    address_c = resp_bal.json()["address"]

    # 3. Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_c = resp_topup.json()["balance"]

    # Verify topup via GET
    resp_bal_after_topup = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_c, timeout=10)
    assert resp_bal_after_topup.status_code == 200, f"Expected 200, got {resp_bal_after_topup.status_code}: {resp_bal_after_topup.text}"
    assert resp_bal_after_topup.json()["balance"] == balance_c

    # 4. Topup again -> 400
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"
    assert "message" in resp_topup2.json()

    # 5. Transfer negative amount -> 400
    resp_neg = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"to": address_c, "amount": -10}, timeout=10)
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

    # Verify balance unchanged
    resp_bal_check1 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_c, timeout=10)
    assert resp_bal_check1.status_code == 200, f"Expected 200, got {resp_bal_check1.status_code}: {resp_bal_check1.text}"
    assert resp_bal_check1.json()["balance"] == balance_c

    # 6. Transfer more than balance -> 400
    user_d = f"userD_{uuid.uuid4().hex[:8]}"
    resp_d = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_d, "password": "pwd"}, timeout=10)
    assert resp_d.status_code == 200, f"Expected 200, got {resp_d.status_code}: {resp_d.text}"
    token_d = resp_d.json()["token"]

    # Verify User D creation
    resp_me_d = requests.get(get_url("gateway", "/user/me"), headers={"Authorization": f"Bearer {token_d}"}, timeout=10)
    assert resp_me_d.status_code == 200, f"Expected 200, got {resp_me_d.status_code}: {resp_me_d.text}"

    resp_bal_d = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token_d}"}, timeout=10)
    assert resp_bal_d.status_code == 200, f"Expected 200, got {resp_bal_d.status_code}: {resp_bal_d.text}"
    address_d = resp_bal_d.json()["address"]

    resp_insufficient = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"to": address_d, "amount": balance_c + 100}, timeout=10)
    assert resp_insufficient.status_code == 400, f"Expected 400, got {resp_insufficient.status_code}: {resp_insufficient.text}"

    # Verify balance unchanged
    resp_bal_check2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_c, timeout=10)
    assert resp_bal_check2.status_code == 200, f"Expected 200, got {resp_bal_check2.status_code}: {resp_bal_check2.text}"
    assert resp_bal_check2.json()["balance"] == balance_c

    # 7. Transfer to invalid address -> 400
    resp_invalid_addr = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"to": "invalid_address_123", "amount": 1}, timeout=10)
    assert resp_invalid_addr.status_code == 400, f"Expected 400, got {resp_invalid_addr.status_code}: {resp_invalid_addr.text}"

    # Verify balance unchanged
    resp_bal_check3 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_c, timeout=10)
    assert resp_bal_check3.status_code == 200, f"Expected 200, got {resp_bal_check3.status_code}: {resp_bal_check3.text}"
    assert resp_bal_check3.json()["balance"] == balance_c

    # 8. Transfer 0 to self -> 200 (no-op)
    resp_noop = requests.post(get_url("gateway", "/wallet/transfer"), headers=headers_c, json={"to": address_c, "amount": 0}, timeout=10)
    assert resp_noop.status_code == 200, f"Expected 200, got {resp_noop.status_code}: {resp_noop.text}"
    assert resp_noop.json()["balance"] == balance_c

    # Verify balance unchanged
    resp_bal_after_noop = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_c, timeout=10)
    assert resp_bal_after_noop.status_code == 200, f"Expected 200, got {resp_bal_after_noop.status_code}: {resp_bal_after_noop.text}"
    assert resp_bal_after_noop.json()["balance"] == balance_c

# --- id=1502  name='Auth Login Workflow' ---
def test_auth_login_workflow():
    # 1. Signup User E
    user_e = f"userE_{uuid.uuid4().hex[:8]}"
    pwd_e = "passE123"
    resp_e = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_e, "password": pwd_e}, timeout=10)
    assert resp_e.status_code == 200, f"Expected 200, got {resp_e.status_code}: {resp_e.text}"

    # Verify User E creation via /user/me
    token_e = resp_e.json()["token"]
    headers_e = {"Authorization": f"Bearer {token_e}"}
    resp_me_e = requests.get(get_url("gateway", "/user/me"), headers=headers_e, timeout=10)
    assert resp_me_e.status_code == 200, f"Expected 200, got {resp_me_e.status_code}: {resp_me_e.text}"

    # 2. Login User E
    resp_login = requests.post(get_url("gateway", "/auth/login"), json={"user": user_e, "password": pwd_e}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token_login = resp_login.json()["token"]
    assert token_login != ""

    # Verify login token works
    headers_login = {"Authorization": f"Bearer {token_login}"}
    resp_me_login = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me_login.status_code == 200, f"Expected 200, got {resp_me_login.status_code}: {resp_me_login.text}"
    assert resp_me_login.json()["user"] == user_e

# --- id=1503  name='Auth Unauthorized Access' ---
def test_auth_unauthorized_access():
    # 1. Login with non-existent user -> 400
    resp_login_fail = requests.post(get_url("gateway", "/auth/login"), json={"user": "nonexistent_user", "password": "pwd"}, timeout=10)
    assert resp_login_fail.status_code == 400, f"Expected 400, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    # 2. Access /user/me without token -> 401
    resp_me_unauth = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_me_unauth.status_code == 401, f"Expected 401, got {resp_me_unauth.status_code}: {resp_me_unauth.text}"

    # 3. Access /wallet/balance without token -> 401
    resp_bal_unauth = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp_bal_unauth.status_code == 401, f"Expected 401, got {resp_bal_unauth.status_code}: {resp_bal_unauth.text}"

    # 4. Access /wallet/topup without token -> 401
    resp_topup_unauth = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp_topup_unauth.status_code == 401, f"Expected 401, got {resp_topup_unauth.status_code}: {resp_topup_unauth.text}"

    # 5. Access /wallet/transfer without token -> 401
    resp_transfer_unauth = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": "addr", "amount": 10}, timeout=10)
    assert resp_transfer_unauth.status_code == 401, f"Expected 401, got {resp_transfer_unauth.status_code}: {resp_transfer_unauth.text}"
