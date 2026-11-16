# Tests generated in iteration 08
# Captured: 2026-07-02T04:27:17
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=531  name='Auth Login' ---
def test_auth_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Setup: create user
    register_and_get_token(username, password)

    # Action: login
    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    login_token = login_resp.json()["token"]

    # Follow-up GET
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

# --- id=532  name='Wallet Topup And Repetition' ---
def test_wallet_topup_and_repetition():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    token = register_and_get_token(username, password)
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    bal_url = get_url("gateway", "/wallet/balance")
    bal_resp = requests.get(bal_url, headers=headers, timeout=10)
    assert bal_resp.status_code == 200, f"Expected 200, got {bal_resp.status_code}: {bal_resp.text}"
    assert bal_resp.json()["balance"] == 0
    address = bal_resp.json()["address"]

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    new_balance = topup_resp.json()["balance"]
    assert new_balance > 0
    assert topup_resp.json()["address"] == address

    # Follow-up GET
    bal_resp2 = requests.get(bal_url, headers=headers, timeout=10)
    assert bal_resp2.status_code == 200, f"Expected 200, got {bal_resp2.status_code}: {bal_resp2.text}"
    assert bal_resp2.json()["balance"] == new_balance

    # Repetition (documented constraint)
    topup_resp2 = requests.get(topup_url, headers=headers, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=533  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    token_a = register_and_get_token(user_a, "pass")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    token_b = register_and_get_token(user_b, "pass")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]
    address_a = topup_resp.json()["address"]

    # Get B address
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]
    balance_b = bal_resp_b.json()["balance"]
    assert balance_b == 0

    # Transfer A -> B
    transfer_amount = 10
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_resp = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"to": address_b, "amount": transfer_amount}, 
        timeout=10
    )
    assert transfer_resp.status_code == 200, f"Expected 200, got {transfer_resp.status_code}: {transfer_resp.text}"
    assert transfer_resp.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET A
    bal_resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a2.status_code == 200, f"Expected 200, got {bal_resp_a2.status_code}: {bal_resp_a2.text}"
    assert bal_resp_a2.json()["balance"] == balance_a - transfer_amount

    # Follow-up GET B
    bal_resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b2.status_code == 200, f"Expected 200, got {bal_resp_b2.status_code}: {bal_resp_b2.text}"
    assert bal_resp_b2.json()["balance"] == balance_b + transfer_amount

    # Transfer 0 (no-op)
    transfer_resp_0 = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"to": address_b, "amount": 0}, 
        timeout=10
    )
    assert transfer_resp_0.status_code == 200, f"Expected 200, got {transfer_resp_0.status_code}: {transfer_resp_0.text}"
    assert transfer_resp_0.json()["balance"] == balance_a - transfer_amount

    # Transfer to self (no-op)
    transfer_resp_self = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"to": address_a, "amount": 10}, 
        timeout=10
    )
    assert transfer_resp_self.status_code == 200, f"Expected 200, got {transfer_resp_self.status_code}: {transfer_resp_self.text}"
    assert transfer_resp_self.json()["balance"] == balance_a - transfer_amount

# --- id=534  name='Wallet Transfer Negative Cases' ---
def test_wallet_transfer_negative_cases():
    user_a = f"usera_{uuid.uuid4().hex[:8]}"
    token_a = register_and_get_token(user_a, "pass")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = f"userb_{uuid.uuid4().hex[:8]}"
    token_b = register_and_get_token(user_b, "pass")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup A
    topup_resp = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"
    balance_a = topup_resp.json()["balance"]

    # Get B address
    bal_resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert bal_resp_b.status_code == 200, f"Expected 200, got {bal_resp_b.status_code}: {bal_resp_b.text}"
    address_b = bal_resp_b.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")

    # 1. Insufficient funds
    resp = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"to": address_b, "amount": balance_a + 100}, 
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 2. Negative amount
    resp = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"to": address_b, "amount": -10}, 
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. Recipient not found (using username instead of wallet address)
    resp = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"to": user_b, "amount": 10}, 
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 4. Missing 'to'
    resp = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"amount": 10}, 
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 5. Missing 'amount'
    resp = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"to": address_b}, 
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Final follow-up GET A to ensure balance unchanged after all failed attempts
    bal_resp_a_final = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert bal_resp_a_final.status_code == 200, f"Expected 200, got {bal_resp_a_final.status_code}: {bal_resp_a_final.text}"
    assert bal_resp_a_final.json()["balance"] == balance_a

# --- id=535  name='Auth Negative Cases' ---
def test_auth_negative_cases():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Missing password on signup
    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Missing password on login
    login_url = get_url("gateway", "/auth/login")
    resp = requests.post(login_url, json={"user": username}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=536  name='Unauthorized Access' ---
def test_unauthorized_access():
    user = f"user_{uuid.uuid4().hex[:8]}"
    token = register_and_get_token(user, "pass")

    # Get valid address
    bal_resp = requests.get(get_url("gateway", "/wallet/balance"), headers={"Authorization": f"Bearer {token}"}, timeout=10)
    address = bal_resp.json()["address"]

    # /user/me
    resp = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/balance
    resp = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/topup
    resp = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # /wallet/transfer
    resp = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address, "amount": 10}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
