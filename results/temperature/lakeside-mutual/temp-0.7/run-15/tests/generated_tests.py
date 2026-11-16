# Tests generated in iteration 15
# Captured: 2026-07-10T01:43:16
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1305  name='Customer Self Backend Insurance Quote Workflow' ---
def test_customer_self_service_backend_insurance_quote_workflow():
    email = f"user_{random_string()}@example.com"
    password = "password123"

    # 1. Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # 2. Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "City",
        "streetAddress": "Street",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    assert customer_id is not None

    # Follow-up GET for Register Customer
    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 4. Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Street", "postalCode": "12345", "city": "City"},
            "billingAddress": {"streetAddress": "Street", "postalCode": "12345", "city": "City"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # Follow-up GET for Quote Request
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_req_id

    # 5. Poll Back-office for Quote Request
    pm_headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}")

    success = False
    for _ in range(10):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            success = True
            break
        time.sleep(1)
    assert success, f"Quote request did not propagate to policy-management-backend"

    # 6. Draft Quote Response (Back-office)
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(pm_quote_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET on Back-office
    resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in history

    # 7. Poll Self-service for QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    success = False
    for _ in range(10):
        resp = requests.get(ss_quote_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in status_history:
                success = True
                break
        time.sleep(1)
    assert success, "Quote status QUOTE_RECEIVED did not propagate to self-service"

    # 8. Accept Quote (Self-service)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET on Self-service
    resp = requests.get(ss_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=1306  name='Customer Core Policy Management Workflow' ---
def test_customer_core_policy_management_workflow():
    headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}

    # 1. Create Customer
    customer_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Avenue",
        "postalCode": "67890",
        "city": "Town",
        "email": f"jane_{random_string()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(customer_url, json=cust_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id
    assert resp.json()["customers"][0]["firstname"] == "Jane"

    # 2. Update Customer
    cust_payload["firstname"] = "Janet"
    resp = requests.put(get_cust_url, json=cust_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["firstname"] == "Janet"

    # Follow-up GET
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Janet"

    # 3. Create Policy
    policy_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Item 1", "description": "Desc 1"}]
        }
    }
    resp = requests.post(policy_url, json=policy_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]
    assert resp.json()["customer"] == customer_id

    # Follow-up GET
    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_policy_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["policyType"] == "Auto"

    # 4. Update Policy
    policy_payload["policyType"] = "Home"
    resp = requests.put(get_policy_url, json=policy_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Home"

    # Follow-up GET
    resp = requests.get(get_policy_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Home"

    # 5. Delete Policy
    resp = requests.delete(get_policy_url, headers=headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET (Listing)
    list_policies_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_policies_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_ids = [p["policyId"] for p in resp.json().get("policies", [])]
    assert policy_id not in policy_ids

# --- id=1307  name='Customer Self Backend Quote Illegal Transition' ---
def test_customer_self_service_backend_quote_illegal_transition():
    email = f"user_{random_string()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "City",
        "streetAddress": "Street",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    customer_id = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10).json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Street", "postalCode": "12345", "city": "City"},
            "billingAddress": {"streetAddress": "Street", "postalCode": "12345", "city": "City"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_req_id = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10).json()["id"]

    # Attempt illegal transition immediately (while in REQUEST_SUBMITTED state)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401 for illegal transition, got {resp.status_code}: {resp.text}"

# --- id=1308  name='Policy Management Backend Creation Failed Dependency' ---
def test_policy_management_backend_creation_failed_dependency():
    headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    policy_url = get_url("policy-management-backend", "/policies")
    policy_payload = {
        "customerId": str(uuid.uuid4()),
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Item 1", "description": "Desc 1"}]
        }
    }
    resp = requests.post(policy_url, json=policy_payload, headers=headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424 for non-existent customer, got {resp.status_code}: {resp.text}"

# --- id=1309  name='Customer Management Backend Interaction Log Errors' ---
def test_customer_management_backend_interaction_log_errors():
    headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}

    # Create Customer via core to ensure customer exists but has no logs yet
    customer_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Lane",
        "postalCode": "11111",
        "city": "Town",
        "email": f"bob_{random_string()}@example.com",
        "phoneNumber": "555-0000"
    }
    customer_id = requests.post(customer_url, json=cust_payload, headers=headers, timeout=10).json()["customerId"]

    # Test 400 Empty ID
    log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(log_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400 for empty lastAcknowledgedInteractionId, got {resp.status_code}: {resp.text}"

    # Test 404 No Log Exists
    resp = requests.patch(log_url, json={"lastAcknowledgedInteractionId": "some-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404 for non-existent log, got {resp.status_code}: {resp.text}"

# --- id=1310  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    customer_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Hole",
        "postalCode": "22222",
        "city": "Wonderland",
        "email": f"alice_{random_string()}@example.com"
        # phoneNumber is missing
    }
    resp = requests.post(customer_url, json=cust_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500 for missing phoneNumber, got {resp.status_code}: {resp.text}"
