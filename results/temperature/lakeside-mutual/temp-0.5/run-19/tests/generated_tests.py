# Tests generated in iteration 19
# Captured: 2026-07-09T05:56:23
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1059  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = generate_email()
    password = "Password123!"

    # 1. Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("email") == email

    # 2. Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None

    headers = {"X-Auth-Token": token}

    # 3. Register Customer
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
    resp = requests.post(reg_url, headers=headers, json=reg_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    # Follow-up GET Customer
    cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # 4. Get User to verify customerId is now present
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # 5. Change Address
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_data = {
        "streetAddress": "New St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    resp = requests.put(addr_url, headers=headers, json=addr_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("city") == "Zurich"

    # Follow-up GET Customer
    resp = requests.get(cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

# --- id=1060  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer in Customer Core
    core_cust_url = get_url("customer-core", "/customers")
    cust_data = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 5",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": generate_email(),
        "phoneNumber": "555-9876"
    }
    resp = requests.post(core_cust_url, headers=headers, json=cust_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    # Follow-up GET in Customer Core
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customers")[0].get("firstname") == "Jane"

    # 2. Create Policy in Policy Management
    pol_url = get_url("policy-management-backend", "/policies")
    pol_data = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(pol_url, headers=headers, json=pol_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json().get("policyId")
    assert policy_id is not None
    assert resp.json().get("policyType") == "Life"
    assert resp.json().get("customer") == customer_id

    # Follow-up GET Policy
    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyType") == "Life"
    assert resp.json().get("customer") == customer_id

    # 3. Update Policy
    update_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    pol_data["policyType"] = "Health"
    resp = requests.put(update_pol_url, headers=headers, json=pol_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET Policy to verify update
    resp = requests.get(get_pol_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyType") == "Health"

    # 4. Delete Policy
    del_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.delete(del_pol_url, headers=headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET Policies list to verify deletion
    list_pol_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_pol_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=1061  name='Customer Management Workflow' ---
def test_customer_management_workflow():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_cust_url = get_url("customer-core", "/customers")
    cust_data = {
        "firstname": "David",
        "lastname": "Bowie",
        "birthday": "1947-01-08T00:00:00Z",
        "streetAddress": "Space St 1",
        "postalCode": "1000",
        "city": "London",
        "email": generate_email(),
        "phoneNumber": "555-4321"
    }
    resp = requests.post(core_cust_url, headers=headers, json=cust_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    # Update Customer in Customer Management
    cm_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_data = {
        "firstname": "David",
        "lastname": "Jones",
        "birthday": "1947-01-08T00:00:00Z",
        "email": cust_data["email"],
        "phoneNumber": "555-4321",
        "moveHistory": []
    }
    resp = requests.put(cm_url, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # Follow-up GET in Customer Management
    resp = requests.get(cm_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

# --- id=1062  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    # Setup Self Service User
    email = generate_email()
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json().get("token")
    ss_headers = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Alice",
        "lastname": "Wonder",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Geneva",
        "streetAddress": "Lake St 1",
        "postalCode": "1200",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=ss_headers, json=reg_data, timeout=10)
    customer_id = resp.json().get("customerId")

    # 1. Create Quote Request in Self Service
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonder",
            "contactAddress": {"streetAddress": "Lake St 1", "postalCode": "1200", "city": "Geneva"},
            "billingAddress": {"streetAddress": "Lake St 1", "postalCode": "1200", "city": "Geneva"}
        },
        "insuranceOptions": {
            "startDate": get_future_date(),
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    resp = requests.post(qr_url, headers=ss_headers, json=qr_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json().get("id")
    assert quote_id is not None

    # Follow-up GET in Self Service
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("insuranceOptions").get("insuranceType") == "Auto"

    # 2. Poll in Policy Management
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(15):
        resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Timeout waiting for quote request in policy management"

    # 3. Draft Quote in Policy Management
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": get_future_date(),
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(pm_qr_url, headers=pm_headers, json=draft_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET in Policy Management
    resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s.get("status") for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in statuses

    # 4. Poll in Self Service for QUOTE_RECEIVED
    received = False
    for _ in range(15):
        resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            statuses = [s.get("status") for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in statuses:
                received = True
                break
        time.sleep(1)
    assert received, "Timeout waiting for QUOTE_RECEIVED in self service"

    # 5. Accept Quote in Self Service
    accept_data = {
        "status": "QUOTE_ACCEPTED"
    }
    resp = requests.patch(ss_qr_url, headers=ss_headers, json=accept_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET in Self Service
    resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s.get("status") for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=1063  name='Negative Self Accept Quote Before Received' ---
def test_negative_self_service_accept_quote_before_received():
    # Setup Self Service User
    email = generate_email()
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json().get("token")
    ss_headers = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Build St 1",
        "postalCode": "3000",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=ss_headers, json=reg_data, timeout=10)
    customer_id = resp.json().get("customerId")

    # Create Quote Request
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Build St 1", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Build St 1", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": get_future_date(),
            "insuranceType": "Home",
            "deductible": {"amount": 100, "currency": "CHF"}
        }
    }
    resp = requests.post(qr_url, headers=ss_headers, json=qr_data, timeout=10)
    quote_id = resp.json().get("id")

    # Immediately try to accept, should be 401 as it's still in REQUEST_SUBMITTED state
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_data = {"status": "QUOTE_ACCEPTED"}
    resp = requests.patch(ss_qr_url, headers=ss_headers, json=accept_data, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1064  name='Negative Customer Management Acknowledge Empty Id' ---
def test_negative_customer_management_acknowledge_empty_id():
    # Create Customer in Customer Core first to have a valid ID
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_cust_url = get_url("customer-core", "/customers")
    cust_data = {
        "firstname": "Empty",
        "lastname": "Id",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "St 1",
        "postalCode": "1000",
        "city": "City",
        "email": generate_email(),
        "phoneNumber": "555-0000"
    }
    resp = requests.post(core_cust_url, headers=headers, json=cust_data, timeout=10)
    customer_id = resp.json().get("customerId")

    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1065  name='Negative Customer Management Acknowledge No Log' ---
def test_negative_customer_management_acknowledge_no_log():
    # Create Customer in Customer Core
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_cust_url = get_url("customer-core", "/customers")
    cust_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Cinema St 1",
        "postalCode": "1000",
        "city": "London",
        "email": generate_email(),
        "phoneNumber": "555-0000"
    }
    resp = requests.post(core_cust_url, headers=headers, json=cust_data, timeout=10)
    customer_id = resp.json().get("customerId")

    # Try to acknowledge interactions for this new customer (who has no logs yet)
    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(url, json={"lastAcknowledgedInteractionId": customer_id}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1066  name='Negative Customer Core Create Missing Phone' ---
def test_negative_customer_core_create_missing_phone():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_cust_url = get_url("customer-core", "/customers")
    cust_data = {
        "firstname": "No",
        "lastname": "Phone",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Quiet St 1",
        "postalCode": "1000",
        "city": "Nowhere",
        "email": generate_email()
        # Missing phoneNumber
    }
    resp = requests.post(core_cust_url, headers=headers, json=cust_data, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"
