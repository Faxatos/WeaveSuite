# Tests generated in iteration 01
# Captured: 2026-06-15T15:51:50
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1241  name='Auth Signup Login And User Info' ---
def test_auth_signup_login_and_user_info():
    username, password, token_signup, headers_signup = create_user_and_verify()

    payload = {"user": username, "password": password}
    resp_login = requests.post(get_url("gateway", "/auth/login"), json=payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token_login = resp_login.json().get("token")
    assert token_login is not None

    headers_login = {"Authorization": f"Bearer {token_login}"}
    resp_me = requests.get(get_url("gateway", "/user/me"), headers=headers_login, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    user_info = resp_me.json()
    assert user_info.get("user") == username
    assert "name" in user_info
    assert "enabled" in user_info

# --- id=1242  name='Auth Negative' ---
def test_auth_negative():
    payload = {"user": f"user_{uuid.uuid4().hex[:8]}"}
    resp_signup = requests.post(get_url("gateway", "/auth/signup"), json=payload, timeout=10)
    assert resp_signup.status_code == 400, f"Expected 400, got {resp_signup.status_code}: {resp_signup.text}"

    username, password, _, _ = create_user_and_verify()
    payload_login = {"user": username, "password": password + "wrong"}
    resp_login = requests.post(get_url("gateway", "/auth/login"), json=payload_login, timeout=10)
    assert resp_login.status_code == 400, f"Expected 400, got {resp_login.status_code}: {resp_login.text}"

# --- id=1243  name='Wallet Topup And Transfer' ---
def test_wallet_topup_and_transfer():
    _, _, _, headers_a = create_user_and_verify()
    _, _, _, headers_b = create_user_and_verify()

    resp_bal_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a.status_code == 200, f"Expected 200, got {resp_bal_a.status_code}: {resp_bal_a.text}"
    info_a = resp_bal_a.json()
    assert info_a.get("balance") == 0
    address_a = info_a.get("address")

    resp_bal_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b.status_code == 200, f"Expected 200, got {resp_bal_b.status_code}: {resp_bal_b.text}"
    info_b = resp_bal_b.json()
    assert info_b.get("balance") == 0
    address_b = info_b.get("address")

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    topup_info = resp_topup.json()
    topup_balance = topup_info.get("balance")
    assert topup_balance > 0
    assert topup_info.get("address") == address_a

    resp_bal_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a2.status_code == 200, f"Expected 200, got {resp_bal_a2.status_code}: {resp_bal_a2.text}"
    bal_a2_info = resp_bal_a2.json()
    assert bal_a2_info.get("balance") == topup_balance
    assert bal_a2_info.get("address") == address_a

    transfer_amount = topup_balance / 2
    transfer_payload = {"to": address_b, "amount": transfer_amount}
    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json=transfer_payload, headers=headers_a, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    transfer_info = resp_transfer.json()
    expected_balance_a = topup_balance - transfer_amount
    assert transfer_info.get("balance") == expected_balance_a
    assert transfer_info.get("address") == address_a

    resp_bal_a3 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a3.status_code == 200, f"Expected 200, got {resp_bal_a3.status_code}: {resp_bal_a3.text}"
    bal_a3_info = resp_bal_a3.json()
    assert bal_a3_info.get("balance") == expected_balance_a
    assert bal_a3_info.get("address") == address_a

    resp_bal_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_bal_b2.status_code == 200, f"Expected 200, got {resp_bal_b2.status_code}: {resp_bal_b2.text}"
    bal_b2_info = resp_bal_b2.json()
    assert bal_b2_info.get("balance") == transfer_amount
    assert bal_b2_info.get("address") == address_b

    resp_transfer_noop = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address_a, "amount": 0}, headers=headers_a, timeout=10)
    assert resp_transfer_noop.status_code == 200, f"Expected 200, got {resp_transfer_noop.status_code}: {resp_transfer_noop.text}"
    assert resp_transfer_noop.json().get("balance") == expected_balance_a

    resp_bal_a4 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_bal_a4.status_code == 200, f"Expected 200, got {resp_bal_a4.status_code}: {resp_bal_a4.text}"
    assert resp_bal_a4.json().get("balance") == expected_balance_a

# --- id=1244  name='Wallet Negative' ---
def test_wallet_negative():
    _, _, _, headers_c = create_user_and_verify()
    _, _, _, headers_d = create_user_and_verify()

    resp_bal_d = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_d, timeout=10)
    assert resp_bal_d.status_code == 200, f"Expected 200, got {resp_bal_d.status_code}: {resp_bal_d.text}"
    address_d = resp_bal_d.json().get("address")

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    balance_c = resp_topup.json().get("balance")

    resp_topup2 = requests.get(get_url("gateway", "/wallet/topup"), headers=headers_c, timeout=10)
    assert resp_topup2.status_code == 400, f"Expected 400, got {resp_topup2.status_code}: {resp_topup2.text}"

    resp_transfer_missing = requests.post(get_url("gateway", "/wallet/transfer"), json={"amount": 10}, headers=headers_c, timeout=10)
    assert resp_transfer_missing.status_code == 400, f"Expected 400, got {resp_transfer_missing.status_code}: {resp_transfer_missing.text}"

    resp_transfer_neg = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address_d, "amount": -10}, headers=headers_c, timeout=10)
    assert resp_transfer_neg.status_code == 400, f"Expected 400, got {resp_transfer_neg.status_code}: {resp_transfer_neg.text}"

    resp_transfer_insufficient = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address_d, "amount": balance_c + 100}, headers=headers_c, timeout=10)
    assert resp_transfer_insufficient.status_code == 400, f"Expected 400, got {resp_transfer_insufficient.status_code}: {resp_transfer_insufficient.text}"

# --- id=1245  name='Unauthorized Access' ---
def test_unauthorized_access():
    _, _, _, headers = create_user_and_verify()
    resp_bal = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    address = resp_bal.json().get("address")

    resp_me = requests.get(get_url("gateway", "/user/me"), timeout=10)
    assert resp_me.status_code == 401, f"Expected 401, got {resp_me.status_code}: {resp_me.text}"

    resp_bal_unauth = requests.get(get_url("gateway", "/wallet/balance"), timeout=10)
    assert resp_bal_unauth.status_code == 401, f"Expected 401, got {resp_bal_unauth.status_code}: {resp_bal_unauth.text}"

    resp_topup = requests.get(get_url("gateway", "/wallet/topup"), timeout=10)
    assert resp_topup.status_code == 401, f"Expected 401, got {resp_topup.status_code}: {resp_topup.text}"

    resp_transfer = requests.post(get_url("gateway", "/wallet/transfer"), json={"to": address, "amount": 10}, timeout=10)
    assert resp_transfer.status_code == 401, f"Expected 401, got {resp_transfer.status_code}: {resp_transfer.text}"
