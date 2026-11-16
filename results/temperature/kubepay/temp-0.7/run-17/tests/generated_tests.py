# Tests generated in iteration 17
# Captured: 2026-07-01T23:42:28
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=427  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # GET balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    wallet_info = resp_bal.json()
    assert wallet_info.get("balance") == 0
    address = wallet_info.get("address")
    assert address is not None

    # Topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    assert topup_info.get("address") == address
    new_balance = topup_info.get("balance")
    assert new_balance > 0

    # Verify balance updated
    resp_bal2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance

    # Topup again -> 400 Bad Request
    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

    # Verify balance unchanged
    resp_bal3 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp_bal3.status_code == 200, f"Expected 200, got {resp_bal3.status_code}: {resp_bal3.text}"
    assert resp_bal3.json().get("balance") == new_balance

# --- id=428  name='Wallet Transfer Funds' ---
def test_wallet_transfer_funds():
    # Setup User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    headers_a = {"Authorization": f"Bearer {resp_a.json()['token']}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]
    address_a = resp_topup_a.json()["address"]

    # Setup User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    headers_b = {"Authorization": f"Bearer {resp_b.json()['token']}"}

    # Get User B address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]
    balance_b = resp_bal_b.json()["balance"]
    assert balance_b == 0

    transfer_amount = balance_a / 2.0
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
    updated_info_a = resp_transfer.json()
    assert updated_info_a["balance"] == balance_a - transfer_amount

    # Verify A balance via GET
    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    assert resp_bal_a2.json()["balance"] == balance_a - transfer_amount

    # Verify B balance via GET
    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    assert resp_bal_b2.json()["balance"] == transfer_amount

    # Transfer to B with amount 0 -> no-op
    resp_transfer_0 = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": 0},
        timeout=10
    )
    assert resp_transfer_0.status_code == 200, f"Expected 200, got {resp_transfer_0.status_code}: {resp_transfer_0.text}"
    assert resp_transfer_0.json()["balance"] == balance_a - transfer_amount

    # Transfer to self with amount > 0 -> no-op
    resp_transfer_self = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_a, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer_self.status_code == 200, f"Expected 200, got {resp_transfer_self.status_code}: {resp_transfer_self.text}"
    assert resp_transfer_self.json()["balance"] == balance_a - transfer_amount

# --- id=429  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    # Setup User A
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    resp_a = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_a, "password": "pwd"}, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    headers_a = {"Authorization": f"Bearer {resp_a.json()['token']}"}

    # Topup User A
    resp_topup_a = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup_a.status_code == 200, f"Expected 200, got {resp_topup_a.status_code}: {resp_topup_a.text}"
    balance_a = resp_topup_a.json()["balance"]

    # Setup User B
    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    resp_b = requests.post(get_url("gateway", "/auth/signup"), json={"user": user_b, "password": "pwd"}, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    headers_b = {"Authorization": f"Bearer {resp_b.json()['token']}"}

    # Get User B address
    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    address_b = resp_bal_b.json()["address"]

    # Missing 'to'
    resp_err_missing = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"amount": 10.0},
        timeout=10
    )
    assert resp_err_missing.status_code == 400, f"Expected 400, got {resp_err_missing.status_code}: {resp_err_missing.text}"

    # Negative amount
    resp_err_neg = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -10.0},
        timeout=10
    )
    assert resp_err_neg.status_code == 400, f"Expected 400, got {resp_err_neg.status_code}: {resp_err_neg.text}"

    # Insufficient funds
    resp_err_insuf = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": balance_a + 1000.0},
        timeout=10
    )
    assert resp_err_insuf.status_code == 400, f"Expected 400, got {resp_err_insuf.status_code}: {resp_err_insuf.text}"

    # Verify A balance unchanged
    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    assert resp_bal_a.json()["balance"] == balance_a

# --- id=430  name='Unauthorized Access' ---
def test_unauthorized_access():
    # GET /user/me
    resp_user = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_user.status_code == 401, f"Expected 401, got {resp_user.status_code}: {resp_user.text}"

    # GET /wallet/balance
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp_bal.status_code == 401, f"Expected 401, got {resp_bal.status_code}: {resp_bal.text}"

    # GET /wallet/topup
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    # POST /wallet/transfer
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        json={"to": "some_address", "amount": 10.0},
        timeout=10
    )
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"

# --- id=425  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": user, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Verify signup via GET /user/me
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json().get("user") == user

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": user, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    login_token = resp_login.json().get("token")
    assert login_token is not None

    # Verify login token works
    headers_login = {"Authorization": f"Bearer {login_token}"}
    resp_me2 = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me2.status_code == 200, f"Expected 200, got {resp_me2.status_code}: {resp_me2.text}"
    assert resp_me2.json().get("user") == user

    # Missing password -> 400 Bad Request
    resp_err = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": f"user_{uuid.uuid4().hex[:8]}"},
        timeout=10
    )
    assert resp_err.status_code == 400, f"Expected 400, got {resp_err.status_code}: {resp_err.text}"

# --- id=426  name='User Me Info' ---
def test_user_me_info():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    resp = requests.post(get_url("gateway", "/auth/signup"), json={"user": user, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}

    # GET /user/me
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    user_info = resp_me.json()
    assert user_info.get("user") == user
    assert "name" in user_info
    assert "enabled" in user_info
