# Tests generated in iteration 04
# Captured: 2026-07-10T22:47:16
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=19  name='Wallet Transfer' ---
def test_wallet_transfer():
    # User A
    user_a, _, token_a = create_user_and_get_token()
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b, _, token_b = create_user_and_get_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User B address
    balance_url = get_url("gateway", "/wallet/balance")
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json().get("address")
    balance_b_initial = resp_b.json().get("balance", 0)

    # Topup User A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_a_after_topup = resp_topup.json().get("balance", 0)

    transfer_amount = 1
    if balance_a_after_topup < transfer_amount:
        transfer_amount = balance_a_after_topup

    if transfer_amount > 0:
        transfer_url = get_url("gateway", "/wallet/transfer")
        resp_transfer = requests.post(
            transfer_url, 
            headers=headers_a, 
            json={"to": address_b, "amount": transfer_amount}, 
            timeout=10
        )
        assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
        balance_a_after_transfer = resp_transfer.json().get("balance", 0)

        # Verify A balance
        resp_a_check = requests.get(balance_url, headers=headers_a, timeout=10)
        assert resp_a_check.status_code == 200, f"Expected 200, got {resp_a_check.status_code}: {resp_a_check.text}"
        assert resp_a_check.json().get("balance", 0) == balance_a_after_transfer

        # Verify B balance
        resp_b_check = requests.get(balance_url, headers=headers_b, timeout=10)
        assert resp_b_check.status_code == 200, f"Expected 200, got {resp_b_check.status_code}: {resp_b_check.text}"
        assert resp_b_check.json().get("balance", 0) == balance_b_initial + transfer_amount

        # Negative: Transfer more than balance
        resp_over = requests.post(
            transfer_url, 
            headers=headers_a, 
            json={"to": address_b, "amount": balance_a_after_transfer + 1000}, 
            timeout=10
        )
        assert resp_over.status_code == 400, f"Expected 400, got {resp_over.status_code}: {resp_over.text}"

    # Negative: Transfer negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp_neg = requests.post(
        transfer_url, 
        headers=headers_a, 
        json={"to": address_b, "amount": -5}, 
        timeout=10
    )
    assert resp_neg.status_code == 400, f"Expected 400, got {resp_neg.status_code}: {resp_neg.text}"

# --- id=16  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = "Password123!"

    signup_url = get_url("gateway", "/auth/signup")
    resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "token" in resp.json()

    # Negative: Duplicate signup
    resp_dup = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert resp_dup.status_code == 400, f"Expected 400, got {resp_dup.status_code}: {resp_dup.text}"

    # Login
    login_url = get_url("gateway", "/auth/login")
    resp_login = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    # Negative: Login wrong password
    resp_bad_login = requests.post(login_url, json={"user": username, "password": "WrongPassword!"}, timeout=10)
    assert resp_bad_login.status_code == 400, f"Expected 400, got {resp_bad_login.status_code}: {resp_bad_login.text}"

    # Negative: Missing required field
    resp_bad_req = requests.post(login_url, json={"user": username}, timeout=10)
    assert resp_bad_req.status_code == 400, f"Expected 400, got {resp_bad_req.status_code}: {resp_bad_req.text}"

# --- id=17  name='User Me' ---
def test_user_me():
    username, password, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "name" in data
    assert "enabled" in data

# --- id=18  name='Wallet Balance And Topup' ---
def test_wallet_balance_and_topup():
    username, password, token = create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    balance_url = get_url("gateway", "/wallet/balance")
    resp_bal = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal.status_code == 200, f"Expected 200, got {resp_bal.status_code}: {resp_bal.text}"
    initial_balance = resp_bal.json().get("balance", 0)
    address = resp_bal.json().get("address")
    assert address is not None

    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    new_balance = resp_topup.json().get("balance", 0)
    assert new_balance > initial_balance

    # Verify with balance endpoint
    resp_bal2 = requests.get(balance_url, headers=headers, timeout=10)
    assert resp_bal2.status_code == 200, f"Expected 200, got {resp_bal2.status_code}: {resp_bal2.text}"
    assert resp_bal2.json().get("balance") == new_balance
