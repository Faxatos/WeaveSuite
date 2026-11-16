# Tests generated in iteration 02
# Captured: 2026-07-09T19:15:26
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1221  name='Customer Core Workflow' ---
def test_customer_core_workflow():
    # 1. Create a customer
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_email(),
        "phoneNumber": "+41791234567"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer_id is not None

    # 2. Get customer
    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    fetched = get_resp.json()["customers"][0]
    assert fetched["customerId"] == customer_id
    assert fetched["firstname"] == "John"

    # 3. Update customer
    payload["firstname"] = "Johnny"
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    # 4. Get customer to verify update
    get_resp2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    fetched2 = get_resp2.json()["customers"][0]
    assert fetched2["firstname"] == "Johnny"
    assert fetched2["lastname"] == "Doe"

# --- id=1222  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = generate_email()
    password = "password123"

    # 1. Signup
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # 2. Login
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "98765",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # 4. Verify user details
    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    # 5. Change address
    addr_payload = {
        "streetAddress": "789 New Way",
        "postalCode": "11111",
        "city": "New City"
    }
    addr_resp = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), json=addr_payload, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    assert addr_resp.json()["streetAddress"] == "789 New Way"

    # 6. Create Insurance Quote Request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": addr_payload,
            "billingAddress": addr_payload
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    # Verify quote request
    get_quote = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert get_quote.status_code == 200, f"Expected 200, got {get_quote.status_code}: {get_quote.text}"
    assert get_quote.json()["id"] == quote_id
    assert get_quote.json()["customerInfo"]["customerId"] == customer_id

# --- id=1223  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    # 1. Create a customer in core
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildtown",
        "email": generate_email(),
        "phoneNumber": "+41791234567"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=CORE_HEADERS, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    # 2. Create policy
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    # 3. Get policy
    get_pol = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert get_pol.status_code == 200, f"Expected 200, got {get_pol.status_code}: {get_pol.text}"
    assert get_pol.json()["policyId"] == policy_id
    assert get_pol.json()["customer"] == customer_id

    # 4. Compute risk factor
    risk_payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    risk_resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_payload, headers=POLICY_HEADERS, timeout=10)
    assert risk_resp.status_code == 200, f"Expected 200, got {risk_resp.status_code}: {risk_resp.text}"
    assert "riskFactor" in risk_resp.json()

    # 5. Delete policy
    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    # Verify deletion
    get_del = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert get_del.status_code in [404, 500], f"Expected 404 or 500, got {get_del.status_code}: {get_del.text}"

# --- id=1224  name='Insurance Quote Request Processing Workflow' ---
def test_insurance_quote_request_processing_workflow():
    # Set up user and customer in self-service
    email = generate_email()
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Cinema St",
        "postalCode": "00000",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    addr_payload = {"streetAddress": "123 Cinema St", "postalCode": "00000", "city": "London"}

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": addr_payload,
            "billingAddress": addr_payload
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    quote_id = quote_resp.json()["id"]

    # Poll policy-management for the request
    found = False
    for _ in range(15):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=POLICY_HEADERS, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management"

    # Draft quote in policy-management
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    patch_pol = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=POLICY_HEADERS, timeout=10)
    assert patch_pol.status_code == 200, f"Expected 200, got {patch_pol.status_code}: {patch_pol.text}"

    # Poll self-service for QUOTE_RECEIVED status
    received = False
    for _ in range(15):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
        if resp.status_code == 200:
            status_history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to self-service"

    # Accept quote in self-service
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    patch_self = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=headers, timeout=10)
    assert patch_self.status_code == 200, f"Expected 200, got {patch_self.status_code}: {patch_self.text}"

    # Verify update
    get_quote2 = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert get_quote2.status_code == 200, f"Expected 200, got {get_quote2.status_code}: {get_quote2.text}"
    status_history2 = get_quote2.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history2)

# --- id=1225  name='Negative Customer Core Missing Phone' ---
def test_negative_customer_core_missing_phone():
    payload = {
        "firstname": "No",
        "lastname": "Phone",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_email()
        # Missing phoneNumber
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1226  name='Negative Policy Management Missing Customer' ---
def test_negative_policy_management_missing_customer():
    policy_payload = {
        "customerId": "nonexistent-customer-id",
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1227  name='Negative Customer Management Acknowledge Interactions' ---
def test_negative_customer_management_acknowledge_interactions():
    # 1. 400 Bad Request for empty lastAcknowledgedInteractionId
    customer_id = "some-id"
    resp_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp_400.status_code == 400, f"Expected 400, got {resp_400.status_code}: {resp_400.text}"

    # 2. 404 Not Found for valid ID but no log exists
    cust_payload = {
        "firstname": "Log",
        "lastname": "Less",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_email(),
        "phoneNumber": "+41791234567"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=CORE_HEADERS, timeout=10)
    real_customer_id = cust_resp.json()["customerId"]

    resp_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{real_customer_id}"), json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=1228  name='Negative Self Illegal Quote Transition' ---
def test_negative_self_service_illegal_quote_transition():
    # Set up user and customer in self-service
    email = generate_email()
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Danger",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Danger City",
        "streetAddress": "123 Danger St",
        "postalCode": "11111",
        "phoneNumber": "555-1111"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    addr_payload = {"streetAddress": "123 Danger St", "postalCode": "11111", "city": "Danger City"}

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Danger",
            "contactAddress": addr_payload,
            "billingAddress": addr_payload
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    quote_id = quote_resp.json()["id"]

    # Attempt to accept immediately (illegal transition from REQUEST_SUBMITTED)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    patch_self = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=headers, timeout=10)
    assert patch_self.status_code == 401, f"Expected 401, got {patch_self.status_code}: {patch_self.text}"
