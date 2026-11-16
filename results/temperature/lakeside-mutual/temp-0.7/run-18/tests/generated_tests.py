# Tests generated in iteration 18
# Captured: 2026-07-10T03:14:36
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1326  name='Customer Core Crud And Errors' ---
def test_customer_core_crud_and_errors():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": random_email(),
        "phoneNumber": "555-1234"
    }
    create_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=payload,
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer = create_resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert "customers" in get_data
    assert len(get_data["customers"]) == 1
    assert get_data["customers"][0]["customerId"] == customer_id
    assert get_data["customers"][0]["firstname"] == "John"

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    update_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        json=update_payload,
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    get_resp2 = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json()["customers"][0]["firstname"] == "Johnny"

    address_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    addr_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}/address"),
        json=address_payload,
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    get_resp3 = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert get_resp3.status_code == 200, f"Expected 200, got {get_resp3.status_code}: {get_resp3.text}"
    cust_data = get_resp3.json()["customers"][0]
    assert cust_data["streetAddress"] == "456 New St"
    assert cust_data["city"] == "Newtown"
    assert cust_data["postalCode"] == "54321"

    bad_payload = payload.copy()
    del bad_payload["phoneNumber"]
    bad_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=bad_payload,
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert bad_resp.status_code == 500, f"Expected 500, got {bad_resp.status_code}: {bad_resp.text}"

# --- id=1327  name='Customer Self Auth And Registration' ---
def test_customer_self_service_auth_and_registration():
    email = random_email()
    password = "Password123!"

    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email
    assert "customerId" not in signup_resp.json()

    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "11111",
        "phoneNumber": "555-9999"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json=reg_payload,
        headers=headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    addr_payload = {
        "streetAddress": "Looking Glass 2",
        "postalCode": "22222",
        "city": "Wonderland"
    }
    addr_resp = requests.put(
        get_url("customer-self-service-backend", f"/customers/{customer_id}/address"),
        json=addr_payload,
        headers=headers,
        timeout=10
    )
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

# --- id=1328  name='Policy Management Policy Lifecycle' ---
def test_policy_management_policy_lifecycle():
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "Construction Site 1",
        "postalCode": "12345",
        "city": "Builder Town",
        "email": random_email(),
        "phoneNumber": "555-2222"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    pol_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_payload,
        headers=POLICY_AUTH_HEADERS,
        timeout=10
    )
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    get_pol_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=POLICY_AUTH_HEADERS,
        timeout=10
    )
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id
    assert get_pol_resp.json()["customer"] == customer_id

    del_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=POLICY_AUTH_HEADERS,
        timeout=10
    )
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    bad_policy = policy_payload.copy()
    bad_policy["customerId"] = "fake-customer-id-999"
    bad_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=bad_policy,
        headers=POLICY_AUTH_HEADERS,
        timeout=10
    )
    assert bad_resp.status_code == 424, f"Expected 424, got {bad_resp.status_code}: {bad_resp.text}"

# --- id=1329  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Hollywood Blvd",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": random_email(),
        "phoneNumber": "555-3333"
    }
    cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=cust_payload,
        headers=CORE_AUTH_HEADERS,
        timeout=10
    )
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    patch_empty = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert patch_empty.status_code == 400, f"Expected 400, got {patch_empty.status_code}: {patch_empty.text}"

    patch_not_found = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": "interaction-123"},
        timeout=10
    )
    assert patch_not_found.status_code == 404, f"Expected 404, got {patch_not_found.status_code}: {patch_not_found.text}"

# --- id=1330  name='Cross Insurance Quote Workflow' ---
def test_cross_service_insurance_quote_workflow():
    email = random_email()
    password = "Password123!"
    requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json={
            "firstname": "Eve",
            "lastname": "Hacker",
            "birthday": "1995-05-05T00:00:00Z",
            "city": "Tech City",
            "streetAddress": "Server Rack 4",
            "postalCode": "10101",
            "phoneNumber": "555-0000"
        },
        headers=ss_headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "Hacker",
            "contactAddress": {"streetAddress": "Server Rack 4", "postalCode": "10101", "city": "Tech City"},
            "billingAddress": {"streetAddress": "Server Rack 4", "postalCode": "10101", "city": "Tech City"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    create_quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_payload,
        headers=ss_headers,
        timeout=10
    )
    assert create_quote_resp.status_code == 200, f"Expected 200, got {create_quote_resp.status_code}: {create_quote_resp.text}"
    quote_id = create_quote_resp.json()["id"]

    bad_accept_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        json={"status": "QUOTE_ACCEPTED"},
        headers=ss_headers,
        timeout=10
    )
    assert bad_accept_resp.status_code == 401, f"Expected 401, got {bad_accept_resp.status_code}: {bad_accept_resp.text}"

    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    found = False
    for _ in range(15):
        get_pm = requests.get(pm_quote_url, headers=POLICY_AUTH_HEADERS, timeout=10)
        if get_pm.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management"

    future_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": future_date,
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    draft_resp = requests.patch(
        pm_quote_url,
        json=draft_payload,
        headers=POLICY_AUTH_HEADERS,
        timeout=10
    )
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(15):
        get_ss = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if get_ss.status_code == 200:
            history = get_ss.json().get("statusHistory", [])
            statuses = [h.get("status") for h in history]
            if "QUOTE_RECEIVED" in statuses:
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to self-service"

    accept_resp = requests.patch(
        ss_quote_url,
        json={"status": "QUOTE_ACCEPTED"},
        headers=ss_headers,
        timeout=10
    )
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"
