# Tests generated in iteration 03
# Captured: 2026-07-10T22:26:55
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=10  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Signup
    resp = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Login
    resp_login = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Signup again (Conflict)
    resp_conflict = requests.post(
        get_url("gateway", "/auth/signup"),
        json={"user": username, "password": password},
        timeout=10
    )
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=11  name='Auth Login Missing Password' ---
def test_auth_login_missing_password():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(
        get_url("gateway", "/auth/login"),
        json={"user": username},
        timeout=10
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=12  name='User Me' ---
def test_user_me():
    username, _, token = signup_user()

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        get_url("gateway", "/user/me"),
        headers=headers,
        timeout=10
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["user"] == username
    assert "name" in data
    assert "enabled" in data

# --- id=13  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    _, _, token = signup_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial balance
    resp_bal = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    initial_data = resp_bal.json()
    assert "address" in initial_data
    assert "balance" in initial_data

    # Topup
    resp_topup = requests.get(
        get_url("gateway", "/wallet/topup"),
        headers=headers,
        timeout=10
    )
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_data = resp_topup.json()
    assert topup_data["address"] == initial_data["address"]

    # Verify balance updated
    resp_bal2 = requests.get(
        get_url("gateway", "/wallet/balance"),
        headers=headers,
        timeout=10
    )
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json()["balance"] == topup_data["balance"]

# --- id=14  name='Wallet Transfer' ---
def test_wallet_transfer():
    # User A
    _, _, token_a = signup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    _, _, token_b = signup_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Topup User A
    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    # Get User A balance
    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    balance_a = resp_a.json()["balance"]

    # Get User B address and balance
    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]
    balance_b = resp_b.json()["balance"]

    # Transfer A -> B
    transfer_amount = 10.0
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": transfer_amount},
        timeout=10
    )
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    # Verify A's balance
    resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json()["balance"] < balance_a

    # Verify B's balance
    resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b2.status_code == 200, f"Expected 200, got {resp_b2.status_code}: {resp_b2.text}"
    assert resp_b2.json()["balance"] > balance_b

# --- id=15  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = signup_user()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    _, _, token_b = signup_user()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json()["address"]

    # Transfer A -> B with negative amount
    resp_transfer = requests.post(
        get_url("gateway", "/wallet/transfer"),
        headers=headers_a,
        json={"to": address_b, "amount": -5.0},
        timeout=10
    )
    assert resp_transfer.status_code == 400, f"Expected 400, got {resp_transfer.status_code}: {resp_transfer.text}"
