# Tests generated in iteration 01
# Captured: 2026-07-08T09:07:31
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=743  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET for Register Customer
    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Get User
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Change Address
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    new_addr = {
        "streetAddress": "New St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    resp = requests.put(addr_url, json=new_addr, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET for Change Address
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=744  name='Customer Core Workflow' ---
def test_customer_core_workflow():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer
    url = get_url("customer-core", "/customers")
    data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Core St 1",
        "postalCode": "1000",
        "city": "City",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(url, json=data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET
    get_url_path = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_path, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json()["customers"][0]
    assert cust_data["customerId"] == customer_id
    assert cust_data["firstname"] == "Alice"

    # Update Customer
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    data["firstname"] = "Alicia"
    resp = requests.put(update_url, json=data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url_path, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Alicia"

    # Negative: Create without phoneNumber
    bad_data = data.copy()
    del bad_data["phoneNumber"]
    resp = requests.post(url, json=bad_data, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=745  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core
    core_url = get_url("customer-core", "/customers")
    cust_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Build St 1",
        "postalCode": "2000",
        "city": "Town",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(core_url, json=cust_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET for customer
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Create Policy
    pol_url = get_url("policy-management-backend", "/policies")
    pol_data = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "policyType": "Life",
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(pol_url, json=pol_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Follow-up GET
    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id
    assert resp.json()["policyType"] == "Life"

    # Update Policy
    pol_data["policyType"] = "Health"
    resp = requests.put(get_pol_url, json=pol_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Health"

    # Delete Policy
    resp = requests.delete(get_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET on listing
    list_pol_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

    # Negative: Create Policy with non-existent customer
    bad_pol_data = pol_data.copy()
    bad_pol_data["customerId"] = "non-existent-id"
    resp = requests.post(pol_url, json=bad_pol_data, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=746  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    # 1. Self-Service: Signup, Login, Register Customer
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "password123"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    requests.post(signup_url, json={"email": email, "password": password}, timeout=10)

    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "Street 1",
        "postalCode": "1234",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(reg_url, json=reg_data, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # Follow-up GET for customer
    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Self-Service: Create Quote Request
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "Street 1", "postalCode": "1234", "city": "London"},
            "billingAddress": {"streetAddress": "Street 1", "postalCode": "1234", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(qr_url, json=qr_data, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    qr_id = resp.json()["id"]

    # Follow-up GET
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == qr_id

    # Negative: Self-Service accept quote while in REQUEST_SUBMITTED -> 401
    resp = requests.patch(ss_qr_url, json={"status": "QUOTE_ACCEPTED"}, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 3. Policy Management: Poll GET Quote Request until 200
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    success = False
    for _ in range(10):
        resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            success = True
            break
        time.sleep(1)
    assert success, "Quote request did not propagate to policy-management"

    # 4. Policy Management: Draft Quote Response
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp = requests.patch(pm_qr_url, json=draft_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_RECEIVED" for h in history)

    # 5. Self-Service: Poll GET Quote Request until QUOTE_RECEIVED
    success = False
    for _ in range(10):
        resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                success = True
                break
        time.sleep(1)
    assert success, "QUOTE_RECEIVED status did not propagate to self-service"

    # 6. Self-Service: Accept Quote
    resp = requests.patch(ss_qr_url, json={"status": "QUOTE_ACCEPTED"}, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=747  name='Customer Management Interaction Logs Negative' ---
def test_customer_management_interaction_logs_negative():
    # Create customer in core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_url = get_url("customer-core", "/customers")
    cust_data = {
        "firstname": "Dave",
        "lastname": "Defect",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Defect St 1",
        "postalCode": "3000",
        "city": "City",
        "email": f"dave_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(core_url, json=cust_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Customer Management: PATCH with empty lastAcknowledgedInteractionId -> 400
    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(cm_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Customer Management: PATCH with valid lastAcknowledgedInteractionId -> 404 (no log exists)
    resp = requests.patch(cm_url, json={"lastAcknowledgedInteractionId": "some-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
