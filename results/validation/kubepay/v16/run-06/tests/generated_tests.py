# Tests generated in iteration 06
# Captured: 2026-06-14T13:37:51
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=792  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    signup_url = get_url("gateway", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"user": username, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "token" in signup_resp.json()
    token = signup_resp.json()["token"]

    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json()["user"] == username

    login_url = get_url("gateway", "/auth/login")
    login_resp = requests.post(login_url, json={"user": username, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    assert "token" in login_resp.json()
    login_token = login_resp.json()["token"]

    me_resp2 = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"}, timeout=10)
    assert me_resp2.status_code == 200, f"Expected 200, got {me_resp2.status_code}: {me_resp2.text}"
    assert me_resp2.json()["user"] == username

# --- id=793  name='Wallet Transfer Multiple Times' ---
def test_wallet_transfer_multiple_times():
    token1, _ = create_user_and_get_token()
    token2, _ = create_user_and_get_token()

    balance_url = get_url("gateway", "/wallet/balance")
    resp2 = requests.get(balance_url, headers={"Authorization": f"Bearer {token2}"}, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    address2 = resp2.json()["address"]
    initial_balance2 = resp2.json()["balance"]

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token1}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    resp1 = requests.get(balance_url, headers={"Authorization": f"Bearer {token1}"}, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"
    balance1 = resp1.json()["balance"]
    assert balance1 > 0

    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 1
    t1_resp = requests.post(transfer_url, json={"to": address2, "amount": transfer_amount}, headers={"Authorization": f"Bearer {token1}"}, timeout=10)
    assert t1_resp.status_code == 200, f"Expected 200, got {t1_resp.status_code}: {t1_resp.text}"

    resp1_after_t1 = requests.get(balance_url, headers={"Authorization": f"Bearer {token1}"}, timeout=10)
    assert resp1_after_t1.status_code == 200, f"Expected 200, got {resp1_after_t1.status_code}: {resp1_after_t1.text}"
    assert resp1_after_t1.json()["balance"] == balance1 - transfer_amount

    t2_resp = requests.post(transfer_url, json={"to": address2, "amount": transfer_amount}, headers={"Authorization": f"Bearer {token1}"}, timeout=10)
    assert t2_resp.status_code == 200, f"Expected 200, got {t2_resp.status_code}: {t2_resp.text}"

    resp1_after_t2 = requests.get(balance_url, headers={"Authorization": f"Bearer {token1}"}, timeout=10)
    assert resp1_after_t2.status_code == 200, f"Expected 200, got {resp1_after_t2.status_code}: {resp1_after_t2.text}"
    assert resp1_after_t2.json()["balance"] == balance1 - 2 * transfer_amount

    resp2_after = requests.get(balance_url, headers={"Authorization": f"Bearer {token2}"}, timeout=10)
    assert resp2_after.status_code == 200, f"Expected 200, got {resp2_after.status_code}: {resp2_after.text}"
    assert resp2_after.json()["balance"] == initial_balance2 + 2 * transfer_amount

# --- id=794  name='Wallet Topup Twice Negative' ---
def test_wallet_topup_twice_negative():
    token, _ = create_user_and_get_token()

    topup_url = get_url("gateway", "/wallet/topup")
    topup_resp = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert topup_resp.status_code == 200, f"Expected 200, got {topup_resp.status_code}: {topup_resp.text}"

    topup_resp2 = requests.get(topup_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert topup_resp2.status_code == 400, f"Expected 400, got {topup_resp2.status_code}: {topup_resp2.text}"

# --- id=795  name='Wallet Transfer Insufficient Funds Negative' ---
def test_wallet_transfer_insufficient_funds_negative():
    token1, _ = create_user_and_get_token()
    token2, _ = create_user_and_get_token()

    balance_url = get_url("gateway", "/wallet/balance")
    resp2 = requests.get(balance_url, headers={"Authorization": f"Bearer {token2}"}, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    address2 = resp2.json()["address"]

    transfer_url = get_url("gateway", "/wallet/transfer")
    t_resp = requests.post(transfer_url, json={"to": address2, "amount": 10}, headers={"Authorization": f"Bearer {token1}"}, timeout=10)
    assert t_resp.status_code == 400, f"Expected 400, got {t_resp.status_code}: {t_resp.text}"

# --- id=796  name='Wallet Transfer Missing Fields Negative' ---
def test_wallet_transfer_missing_fields_negative():
    token1, _ = create_user_and_get_token()

    transfer_url = get_url("gateway", "/wallet/transfer")
    t_resp = requests.post(transfer_url, json={"amount": 10}, headers={"Authorization": f"Bearer {token1}"}, timeout=10)
    assert t_resp.status_code == 400, f"Expected 400, got {t_resp.status_code}: {t_resp.text}"

# --- id=797  name='Auth Unauthorized Negative' ---
def test_auth_unauthorized_negative():
    me_url = get_url("gateway", "/user/me")
    resp = requests.get(me_url, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
