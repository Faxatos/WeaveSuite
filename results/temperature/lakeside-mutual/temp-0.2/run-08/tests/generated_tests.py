# Tests generated in iteration 08
# Captured: 2026-07-07T07:25:30
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=416  name='Customer Core And Policy Management Workflow' ---
def test_customer_core_and_policy_management_workflow():
    # 1. Create customer in customer-core
    core_url = get_url("customer-core", "/customers")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": "alice.smith@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(core_url, json=customer_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_data = resp.json()
    customer_id = customer_data["customerId"]

    # Verify customer creation
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_wrapper = resp.json()
    assert "customers" in cust_wrapper
    assert len(cust_wrapper["customers"]) > 0
    fetched_cust = cust_wrapper["customers"][0]
    assert fetched_cust["firstname"] == "Alice"
    assert fetched_cust["email"] == "alice.smith@example.com"

    # 2. Create policy in policy-management-backend
    pol_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Fire", "description": "Fire coverage"}]
        }
    }
    resp = requests.post(pol_url, json=policy_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_data = resp.json()
    policy_id = policy_data["policyId"]

    # Verify policy creation
    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_pol = resp.json()
    assert fetched_pol["customer"] == customer_id
    assert fetched_pol["policyType"] == "Home"
    assert fetched_pol["deductible"]["amount"] == 1000

# --- id=417  name='Self Quote Workflow' ---
def test_self_service_quote_workflow():
    # 1. Signup
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    ss_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(ss_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 3. Register customer profile
    cust_url = get_url("customer-self-service-backend", "/customers")
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "city": "Buildtown",
        "streetAddress": "1 Brick Rd",
        "postalCode": "10001",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(cust_url, json=cust_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verify user
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 4. Create quote request
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {
                "streetAddress": "1 Brick Rd",
                "postalCode": "10001",
                "city": "Buildtown"
            },
            "billingAddress": {
                "streetAddress": "1 Brick Rd",
                "postalCode": "10001",
                "city": "Buildtown"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(qr_url, json=qr_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_data = resp.json()
    quote_id = quote_data["id"]
    assert quote_data["customerInfo"]["customerId"] == customer_id

    # Verify quote request
    get_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_quote = resp.json()
    assert fetched_quote["id"] == quote_id
    assert fetched_quote["customerInfo"]["customerId"] == customer_id

    # 5. Negative: Try to accept while REQUEST_SUBMITTED
    resp = requests.patch(get_qr_url, json={"status": "QUOTE_ACCEPTED"}, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 6. Poll policy-management for async arrival
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(15):
        resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management-backend")

    # 7. Draft quote response in back-office
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 20000, "currency": "USD"}
    }
    resp = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    draft_resp_data = resp.json()
    assert draft_resp_data["insuranceQuote"]["insurancePremium"]["amount"] == 150

    # Verify draft in policy-management
    resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["insuranceQuote"]["insurancePremium"]["amount"] == 150

    # 8. Poll self-service for QUOTE_RECEIVED async propagation
    for _ in range(15):
        resp = requests.get(get_qr_url, headers=ss_headers, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        statuses = [s.get("status") for s in data.get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request status QUOTE_RECEIVED did not propagate to customer-self-service-backend")

    # 9. Accept quote in self-service
    resp = requests.patch(get_qr_url, json={"status": "QUOTE_ACCEPTED"}, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify final status
    resp = requests.get(get_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    statuses = [s.get("status") for s in data.get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=418  name='Policy Management Invalid Customer' ---
def test_policy_management_invalid_customer():
    url = get_url("policy-management-backend", "/policies")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "customerId": "non-existent-customer-id",
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Item 1", "description": "Desc 1"}]
        }
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=419  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    url = get_url("customer-core", "/customers")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "No",
        "lastname": "Phone",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "no.phone@example.com"
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=420  name='Customer Management Interaction Log Not Found' ---
def test_customer_management_interaction_log_not_found():
    core_url = get_url("customer-core", "/customers")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Log",
        "lastname": "Less",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "log.less@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(core_url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    ack_payload = {"lastAcknowledgedInteractionId": "int-123"}
    resp = requests.patch(cm_url, json=ack_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=421  name='Policy Management Quote Request Not Found' ---
def test_policy_management_quote_request_not_found():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", "/insurance-quote-requests/999999999")
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 20000, "currency": "USD"}
    }
    resp = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=422  name='Customer Core Update Customer' ---
def test_customer_core_update_customer():
    core_url = get_url("customer-core", "/customers")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "123 Rock St",
        "postalCode": "98101",
        "city": "Seattle",
        "email": "dave@example.com",
        "phoneNumber": "555-4444"
    }
    resp = requests.post(core_url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_url = get_url("customer-core", f"/customers/{customer_id}")
    update_payload = {
        "firstname": "David",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "456 Grunge Ave",
        "postalCode": "98102",
        "city": "Seattle",
        "email": "david.grohl@example.com",
        "phoneNumber": "555-5555"
    }
    resp = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_data = resp.json()
    assert updated_data["firstname"] == "David"
    assert updated_data["streetAddress"] == "456 Grunge Ave"

    get_url_core = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_core, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()["customers"][0]
    assert fetched["firstname"] == "David"
    assert fetched["streetAddress"] == "456 Grunge Ave"
    assert fetched["email"] == "david.grohl@example.com"

# --- id=423  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    core_url = get_url("customer-core", "/customers")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Eve",
        "lastname": "Polastri",
        "birthday": "1980-05-05T00:00:00Z",
        "streetAddress": "123 Spy Way",
        "postalCode": "W1",
        "city": "London",
        "email": "eve@example.com",
        "phoneNumber": "555-6666"
    }
    resp = requests.post(core_url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "456 MI6 Blvd",
        "postalCode": "SW1",
        "city": "London"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_data = resp.json()
    assert addr_data["streetAddress"] == "456 MI6 Blvd"

    get_url_core = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_core, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()["customers"][0]
    assert fetched["streetAddress"] == "456 MI6 Blvd"
    assert fetched["postalCode"] == "SW1"

# --- id=424  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    core_url = get_url("customer-core", "/customers")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1975-11-11T00:00:00Z",
        "streetAddress": "123 Punisher Ln",
        "postalCode": "10012",
        "city": "New York",
        "email": "frank@example.com",
        "phoneNumber": "555-7777"
    }
    resp = requests.post(core_url, json=customer_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    pol_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 600, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Collision", "description": "Collision coverage"}]
        }
    }
    resp = requests.post(pol_url, json=policy_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    del_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.delete(del_url, headers=headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    list_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=425  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    url = get_url("policy-management-backend", "/riskfactor/compute")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "riskFactor" in data
    assert isinstance(data["riskFactor"], int)

# --- id=426  name='Customer Core Cities' ---
def test_customer_core_get_cities():
    url = get_url("customer-core", "/cities/12345")
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "cities" in data
    assert isinstance(data["cities"], list)

# --- id=427  name='Self Change Address' ---
def test_self_service_change_address():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    cust_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Navy Pier",
        "postalCode": "10001",
        "phoneNumber": "555-8888"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "456 Pentagon",
        "postalCode": "20310",
        "city": "Arlington"
    }
    resp = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_data = resp.json()
    assert addr_data["streetAddress"] == "456 Pentagon"

    get_url_cust = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_url_cust, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
