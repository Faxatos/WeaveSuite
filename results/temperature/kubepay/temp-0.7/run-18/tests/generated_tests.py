# Tests generated in iteration 18
# Captured: 2026-07-02T00:04:02
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=431  name='Auth Signup And Login' ---
def test_auth_signup_and_login():
    user_data = generate_user()
    url_signup = get_url("gateway", "/auth/signup")

    resp_signup = requests.post(url_signup, json=user_data, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert "token" in resp_signup.json()

    url_login = get_url("gateway", "/auth/login")
    resp_login = requests.post(url_login, json=user_data, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    assert "token" in resp_login.json()

    token = resp_login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == user_data["user"]

# --- id=432  name='Auth Signup Conflict' ---
def test_auth_signup_conflict():
    user_data = generate_user()
    url = get_url("gateway", "/auth/signup")
    resp = requests.post(url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp2 = requests.post(url, json=user_data, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=433  name='Auth Login Invalid Credentials' ---
def test_auth_login_invalid_credentials():
    user_data = generate_user()
    url = get_url("gateway", "/auth/login")
    resp = requests.post(url, json=user_data, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=434  name='Auth Missing Fields' ---
def test_auth_missing_fields():
    url_signup = get_url("gateway", "/auth/signup")
    resp = requests.post(url_signup, json={"user": "test"}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    url_login = get_url("gateway", "/auth/login")
    resp2 = requests.post(url_login, json={"user": "test"}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=435  name='User Me And Wallet Initial Balance' ---
def test_user_me_and_wallet_initial_balance():
    user_data = generate_user()
    token = signup(user_data)
    headers = {"Authorization": f"Bearer {token}"}

    url_me = get_url("gateway", "/user/me")
    resp_me = requests.get(url_me, headers=headers, timeout=10)
    assert resp_me.status_code == 200, f"Expected 200, got {resp_me.status_code}: {resp_me.text}"
    assert resp_me.json()["user"] == user_data["user"]
    assert "name" in resp_me.json()

    url_balance = get_url("gateway", "/wallet/balance")
    resp_balance = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance.status_code == 200, f"Expected 200, got {resp_balance.status_code}: {resp_balance.text}"
    assert resp_balance.json()["balance"] == 0
    assert isinstance(resp_balance.json()["address"], str)

# --- id=436  name='Wallet Topup And Conflict' ---
def test_wallet_topup_and_conflict():
    user_data = generate_user()
    token = signup(user_data)
    headers = {"Authorization": f"Bearer {token}"}

    url_balance = get_url("gateway", "/wallet/balance")
    resp = requests.get(url_balance, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["balance"] == 0

    url_topup = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"
    new_balance = resp_topup.json()["balance"]
    assert new_balance > 0

    resp_balance2 = requests.get(url_balance, headers=headers, timeout=10)
    assert resp_balance2.status_code == 200, f"Expected 200, got {resp_balance2.status_code}: {resp_balance2.text}"
    assert resp_balance2.json()["balance"] == new_balance

    resp_conflict = requests.get(url_topup, headers=headers, timeout=10)
    assert resp_conflict.status_code == 400, f"Expected 400, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=437  name='Wallet Transfer Success' ---
def test_wallet_transfer_success():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_a.json()["balance"]

    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    balance_b = resp_b.json()["balance"]
    address_b = resp_b.json()["address"]

    transfer_amount = 1.0 if balance_a >= 1.0 else balance_a / 2.0
    if transfer_amount == 0:
        pytest.skip("Topup amount is 0, cannot test transfer")

    transfer_payload = {
        "to": address_b,
        "amount": transfer_amount
    }

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"
    assert resp_transfer.json()["balance"] == balance_a - transfer_amount

    resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json()["balance"] == balance_a - transfer_amount

    resp_b2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    assert resp_b2.status_code == 200, f"Expected 200, got {resp_b2.status_code}: {resp_b2.text}"
    assert resp_b2.json()["balance"] == balance_b + transfer_amount

# --- id=438  name='Wallet Transfer To Self' ---
def test_wallet_transfer_to_self():
    user_data = generate_user()
    token = signup(user_data)
    headers = {"Authorization": f"Bearer {token}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers, timeout=10)

    resp = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    balance = resp.json()["balance"]
    address = resp.json()["address"]

    transfer_payload = {
        "to": address,
        "amount": balance
    }

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp_transfer = requests.post(url_transfer, headers=headers, json=transfer_payload, timeout=10)
    assert resp_transfer.status_code == 200, f"Expected 200, got {resp_transfer.status_code}: {resp_transfer.text}"

    resp2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers, timeout=10)
    assert resp2.json()["balance"] == balance

# --- id=439  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)

    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_a.json()["balance"]

    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_b.json()["address"]

    transfer_payload = {
        "to": address_b,
        "amount": balance_a + 100
    }

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a2.json()["balance"] == balance_a

# --- id=440  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    user_b = generate_user()
    token_b = signup(user_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp_b = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_b, timeout=10)
    address_b = resp_b.json()["address"]

    transfer_payload = {
        "to": address_b,
        "amount": -10
    }

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=441  name='Wallet Transfer Invalid Recipient' ---
def test_wallet_transfer_invalid_recipient():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.get(get_url("gateway", "/wallet/topup"), headers=headers_a, timeout=10)
    resp_a = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    balance_a = resp_a.json()["balance"]

    transfer_payload = {
        "to": "invalid_address_that_does_not_exist",
        "amount": 1
    }

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp = requests.post(url_transfer, headers=headers_a, json=transfer_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp_a2 = requests.get(get_url("gateway", "/wallet/balance"), headers=headers_a, timeout=10)
    assert resp_a2.json()["balance"] == balance_a

# --- id=442  name='Wallet Transfer Missing Fields' ---
def test_wallet_transfer_missing_fields():
    user_a = generate_user()
    token_a = signup(user_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    url_transfer = get_url("gateway", "/wallet/transfer")

    resp1 = requests.post(url_transfer, headers=headers_a, json={"amount": 10}, timeout=10)
    assert resp1.status_code == 400, f"Expected 400, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(url_transfer, headers=headers_a, json={"to": "some_address"}, timeout=10)
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"

# --- id=443  name='Unauthorized Access' ---
def test_unauthorized_access():
    url_me = get_url("gateway", "/user/me")
    resp = requests.get(url_me, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    url_balance = get_url("gateway", "/wallet/balance")
    resp2 = requests.get(url_balance, headers={"Authorization": "Bearer invalid_token"}, timeout=10)
    assert resp2.status_code == 401, f"Expected 401, got {resp2.status_code}: {resp2.text}"

    url_transfer = get_url("gateway", "/wallet/transfer")
    resp3 = requests.post(url_transfer, json={"to": "addr", "amount": 10}, timeout=10)
    assert resp3.status_code == 401, f"Expected 401, got {resp3.status_code}: {resp3.text}"
