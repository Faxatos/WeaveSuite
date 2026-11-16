# Tests generated in iteration 05
# Captured: 2026-06-14T13:14:29
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=784  name='Auth Login' ---
def test_auth_login():
    username, password, _ = create_user()
    url = get_url("gateway", "/auth/login")
    resp = requests.post(url, json={"user": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    # Verify token works
    me_url = get_url("gateway", "/user/me")
    me_resp = requests.get(me_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
    assert me_resp.json().get("user") == username

# --- id=785  name='User Me' ---
def test_user_me():
    username, _, token = create_user()
    url = get_url("gateway", "/user/me")
    resp = requests.get(url, headers=get_auth_headers(token), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("user") == username
    assert "enabled" in data

# --- id=786  name='Wallet Topup Workflow' ---
def test_wallet_topup_workflow():
    _, _, token = create_user()
    headers = get_auth_headers(token)

    # Check initial balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("balance") == 0

    # Topup
    topup_url = get_url("gateway", "/wallet/topup")
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify balance updated
    resp = requests.get(balance_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    new_balance = resp.json().get("balance")
    assert new_balance > 0

    # Topup again should fail
    resp = requests.get(topup_url, headers=headers, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=787  name='Wallet Transfer Workflow' ---
def test_wallet_transfer_workflow():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    # Get A's balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    balance_a = resp_a.json().get("balance")

    # Get B's address and balance
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json().get("address")
    balance_b = resp_b.json().get("balance")
    assert balance_b == 0

    # Transfer A -> B
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 10
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify A's balance
    resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json().get("balance") == balance_a - transfer_amount

    # Verify B's balance
    resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b2.status_code == 200, f"Expected 200, got {resp_b2.status_code}: {resp_b2.text}"
    assert resp_b2.json().get("balance") == balance_b + transfer_amount

# --- id=788  name='Wallet Transfer Multiple' ---
def test_wallet_transfer_multiple():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    # Get A's balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    balance_a = resp_a.json().get("balance")

    # Get B's address and balance
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json().get("address")
    balance_b = resp_b.json().get("balance")

    # Transfer A -> B twice
    transfer_url = get_url("gateway", "/wallet/transfer")
    transfer_amount = 5

    resp1 = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp_a_mid = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a_mid.status_code == 200, f"Expected 200, got {resp_a_mid.status_code}: {resp_a_mid.text}"
    assert resp_a_mid.json().get("balance") == balance_a - transfer_amount

    resp2 = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": transfer_amount}, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"

    # Verify cumulative state
    resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json().get("balance") == balance_a - (transfer_amount * 2)

    resp_b2 = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b2.status_code == 200, f"Expected 200, got {resp_b2.status_code}: {resp_b2.text}"
    assert resp_b2.json().get("balance") == balance_b + (transfer_amount * 2)

# --- id=789  name='Wallet Transfer Negative Amount' ---
def test_wallet_transfer_negative_amount():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    # Get A's balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    balance_a = resp_a.json().get("balance")

    # Get B's address
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json().get("address")

    # Transfer A -> B with negative amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": -5}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify balance unchanged
    resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json().get("balance") == balance_a

# --- id=790  name='Wallet Transfer Insufficient Funds' ---
def test_wallet_transfer_insufficient_funds():
    _, _, token_a = create_user()
    _, _, token_b = create_user()
    headers_a = get_auth_headers(token_a)
    headers_b = get_auth_headers(token_b)

    # Get A's balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    balance_a = resp_a.json().get("balance")

    # Get B's address
    resp_b = requests.get(balance_url, headers=headers_b, timeout=10)
    assert resp_b.status_code == 200, f"Expected 200, got {resp_b.status_code}: {resp_b.text}"
    address_b = resp_b.json().get("address")

    # Transfer A -> B with insufficient funds (A has 0)
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_b, "amount": 10}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Verify balance unchanged
    resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json().get("balance") == balance_a

# --- id=791  name='Wallet Transfer Self Noop' ---
def test_wallet_transfer_self_noop():
    _, _, token_a = create_user()
    headers_a = get_auth_headers(token_a)

    # Topup A
    topup_url = get_url("gateway", "/wallet/topup")
    resp_topup = requests.get(topup_url, headers=headers_a, timeout=10)
    assert resp_topup.status_code == 200, f"Expected 200, got {resp_topup.status_code}: {resp_topup.text}"

    # Get A's address and balance
    balance_url = get_url("gateway", "/wallet/balance")
    resp_a = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a.status_code == 200, f"Expected 200, got {resp_a.status_code}: {resp_a.text}"
    address_a = resp_a.json().get("address")
    balance_a = resp_a.json().get("balance")

    # Transfer A -> A with 0 amount
    transfer_url = get_url("gateway", "/wallet/transfer")
    resp = requests.post(transfer_url, headers=headers_a, json={"to": address_a, "amount": 0}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify A's balance is unchanged
    resp_a2 = requests.get(balance_url, headers=headers_a, timeout=10)
    assert resp_a2.status_code == 200, f"Expected 200, got {resp_a2.status_code}: {resp_a2.text}"
    assert resp_a2.json().get("balance") == balance_a
