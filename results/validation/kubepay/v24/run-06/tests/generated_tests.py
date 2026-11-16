# Tests generated in iteration 06
# Captured: 2026-06-16T22:43:55
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1662  name='Wallet Transfer Errors' ---
def test_wallet_transfer_errors():
    userA, passA = generate_user()
    tokenA = signup(userA, passA)
    headersA = {"Authorization": f"Bearer {tokenA}"}

    # Topup A
    resp_topupA = requests.get(get_url("gateway", "/wallet/topup"), headers=headersA, timeout=10)
    assert resp_topupA.status_code == 200, f"Expected 200, got {resp_topupA.status_code}: {resp_topupA.text}"
    balanceA = resp_topupA.json()["balance"]
    addressA = resp_topupA.json()["address"]

    url_transfer = get_url("gateway", "/wallet/transfer")

    # Missing 'to'
    resp_err1 = requests.post(url_transfer, headers=headersA, json={"amount": 10}, timeout=10)
    assert resp_err1.status_code == 400, f"Expected 400, got {resp_err1.status_code}: {resp_err1.text}"

    # Missing 'amount'
    resp_err2 = requests.post(url_transfer, headers=headersA, json={"to": addressA}, timeout=10)
    assert resp_err2.status_code == 400, f"Expected 400, got {resp_err2.status_code}: {resp_err2.text}"

    # Negative amount
    resp_err3 = requests.post(url_transfer, headers=headersA, json={"to": addressA, "amount": -5}, timeout=10)
    assert resp_err3.status_code == 400, f"Expected 400, got {resp_err3.status_code}: {resp_err3.text}"

    # Insufficient funds
    resp_err4 = requests.post(url_transfer, headers=headersA, json={"to": addressA, "amount": balanceA + 100}, timeout=10)
    assert resp_err4.status_code == 400, f"Expected 400, got {resp_err4.status_code}: {resp_err4.text}"

    # Recipient not found
    resp_err5 = requests.post(url_transfer, headers=headersA, json={"to": "non_existent_address_123", "amount": 10}, timeout=10)
    assert resp_err5.status_code == 400, f"Expected 400, got {resp_err5.status_code}: {resp_err5.text}"

    # Transfer 0 (no-op)
    resp_noop1 = requests.post(url_transfer, headers=headersA, json={"to": addressA, "amount": 0}, timeout=10)
    assert resp_noop1.status_code == 200, f"Expected 200, got {resp_noop1.status_code}: {resp_noop1.text}"
    assert resp_noop1.json()["balance"] == balanceA

    # Transfer to own address (no-op)
    resp_noop2 = requests.post(url_transfer, headers=headersA, json={"to": addressA, "amount": 5}, timeout=10)
    assert resp_noop2.status_code == 200, f"Expected 200, got {resp_noop2.status_code}: {resp_noop2.text}"
    assert resp_noop2.json()["balance"] == balanceA

# --- id=1658  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user, password = generate_user()

    # Signup
    url_signup = get_url("gateway", "/auth/signup")
    resp_signup = requests.post(url_signup, json={"user": user, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    # Duplicate signup (Conflict)
    resp_dup = requests.post(url_signup, json={"user": user, "password": password}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"

    # Login
    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json={"user": user, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Login wrong password
    resp_wrong = requests.post(url_login, json={"user": user, "password": "wrongpassword"}, timeout=10)
    assert resp_wrong.status_code == 400, f"Expected 400, got {resp_wrong.status_code}: {resp_wrong.text}"

# --- id=1659  name='User Me' ---
def test_user_me():
    user, password = generate_user()
    token = signup(user, password)

    url_me = get_url("gateway", "/user/me")
    headers = {"Authorization": f"Bearer {token}"}

    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    data = resp_me.json()
    assert data["user"] == user
    assert "name" in data
    assert "enabled" in data

    # Unauthorized
    resp_unauth = requests.get(url_me, timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=1660  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    user, password = generate_user()
    token = signup(user, password)
    headers = {"Authorization": f"Bearer {token}"}

    # Initial balance
    url_balance = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    bal_data = resp_bal.json()
    assert bal_data["balance"] == 0
    assert "address" in bal_data

    # Topup
    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["balance"] > 0
    assert topup_data["address"] == bal_data["address"]

    # Follow-up balance
    resp_bal2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == topup_data["balance"]

    # Topup again (conflict)
    resp_topup2 = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

# --- id=1661  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    userA, passA = generate_user()
    tokenA = signup(userA, passA)
    headersA = {"Authorization": f"Bearer {tokenA}"}

    userB, passB = generate_user()
    tokenB = signup(userB, passB)
    headersB = {"Authorization": f"Bearer {tokenB}"}

    # Topup A
    resp_topupA = requests.get(get_url("gateway", "/wallet/topup"), headers=headersA, timeout=10)
    assert resp_topupA.status_code == 200, f"Expected 200, got {resp_topupA.status_code}: {resp_topupA.text}"
    balanceA = resp_topupA.json()["balance"]

    # Get B address
    resp_balB = requests.get(get_url("gateway", "/wallet/balance"), headers=headersB, timeout=10)
    assert resp_balB.status_code == 200, f"Expected 200, got {resp_balB.status_code}: {resp_balB.text}"
    addressB = resp_balB.json()["address"]
    balanceB = resp_balB.json()["balance"]

    # Transfer A -> B
    transfer_amount = 10
    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headersA, json={"to": addressB, "amount": transfer_amount}, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balanceA - transfer_amount

    # Follow-up A
    resp_balA2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headersA, timeout=10)
    assert resp_balA2.status_code == 200, f"Expected 200, got {resp_balA2.status_code}: {resp_balA2.text}"
    assert resp_balA2.json()["balance"] == balanceA - transfer_amount

    # Follow-up B
    resp_balB2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headersB, timeout=10)
    assert resp_balB2.status_code == 200, f"Expected 200, got {resp_balB2.status_code}: {resp_balB2.text}"
    assert resp_balB2.json()["balance"] == balanceB + transfer_amount
