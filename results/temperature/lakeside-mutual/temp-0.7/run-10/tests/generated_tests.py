# Tests generated in iteration 10
# Captured: 2026-07-09T23:14:27
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1271  name='Self Registration Workflow' ---
def test_self_service_registration_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
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

    # 3. GET /user before registration
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()

    # 4. Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 5. Verify Customer via GET
    get_cust_url = get_resource_url(resp.json(), "customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 6. Verify User after registration
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=1272  name='Core Customer Update Workflow' ---
def test_core_customer_update_workflow():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create
    create_url = get_url("customer-core", "/customers")
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-15T00:00:00Z",
        "streetAddress": "Oak Ave 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(create_url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Verify Create
    get_url_1 = get_resource_url(resp.json(), "customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_1, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json()["customers"][0]
    assert cust_data["firstname"] == "Alice"
    assert cust_data["lastname"] == "Smith"
    assert cust_data["streetAddress"] == "Oak Ave 2"
    assert cust_data["email"] == payload["email"]
    assert "phoneNumber" in cust_data

    # 3. Update
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    payload["firstname"] = "Alicia"
    resp = requests.put(update_url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Verify Update
    resp = requests.get(get_url_1, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json()["customers"][0]
    assert cust_data["firstname"] == "Alicia"

# --- id=1273  name='Core Customer Update Missing Phone Error' ---
def test_core_customer_update_missing_phone_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Pine St 3",
        "postalCode": "2000",
        "city": "Geneva",
        "email": f"bob_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(create_url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update missing phoneNumber -> 500
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    del payload["phoneNumber"]
    resp = requests.put(update_url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1274  name='Policy Deletion' ---
def test_policy_deletion():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer
    create_cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "streetAddress": "Code St 1",
        "postalCode": "5000",
        "city": "Aarau",
        "email": f"grace_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-4444"
    }
    resp = requests.post(create_cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Create Policy
    create_pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Basic coverage"}
            ]
        }
    }
    resp = requests.post(create_pol_url, json=pol_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # 3. Verify Policy
    get_pol_url = get_resource_url(resp.json(), "policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id
    assert resp.json()["policyType"] == "Home"
    assert resp.json()["deductible"]["amount"] == 500
    assert resp.json()["policyLimit"]["amount"] == 100000
    assert resp.json()["insurancePremium"]["amount"] == 1000
    assert "startDate" in resp.json()["policyPeriod"]
    assert "endDate" in resp.json()["policyPeriod"]

    # 4. Delete Policy
    delete_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.delete(delete_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # 5. Verify Deletion via listing
    list_pol_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_pol_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = [p["policyId"] for p in resp.json().get("policies", [])]
    assert policy_id not in policies

# --- id=1275  name='Insurance Quote Workflow' ---
def test_insurance_quote_workflow():
    # 1. Setup Self-Service Customer
    email = f"quote_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Black",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # 2. Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Black",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Verify Quote in Self-Service
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Poll Policy Management until it appears
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(15):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy management"

    # 4. Draft Quote Response in Policy Management
    pm_patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(pm_quote_url, json=pm_patch_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify in Policy Management
    resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in status_history

    # 5. Poll Self-Service until QUOTE_RECEIVED appears
    received = False
    for _ in range(15):
        resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in status_history:
                received = True
                break
        time.sleep(1)
    assert received, "Quote response did not propagate to self-service"

    # 6. Accept Quote in Self-Service
    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(ss_quote_url, json=ss_patch_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 7. Verify Acceptance in Self-Service
    resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in status_history
    assert "insuranceQuote" in resp.json()
    assert resp.json()["insuranceQuote"]["insurancePremium"]["amount"] == 1000
    assert resp.json()["insuranceQuote"]["policyLimit"]["amount"] == 100000

# --- id=1276  name='Insurance Quote Illegal Transition Error' ---
def test_insurance_quote_illegal_transition_error():
    email = f"illegal_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Eve",
        "lastname": "White",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "White",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Verify Quote Request created
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Attempt to accept immediately (while in REQUEST_SUBMITTED) -> 401
    ss_patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(ss_quote_url, json=ss_patch_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1277  name='Self Address Change' ---
def test_self_service_address_change():
    email = f"addr_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Frank",
        "lastname": "Wright",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Old St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # Change Address
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    new_addr = {
        "streetAddress": "New St 2",
        "postalCode": "9000",
        "city": "St. Gallen"
    }
    resp = requests.put(addr_url, json=new_addr, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "New St 2"
    assert resp.json()["postalCode"] == "9000"
    assert resp.json()["city"] == "St. Gallen"

    # Follow-up GET
    get_cust_url = get_resource_url(resp.json(), "customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=1278  name='Customer Management Update Workflow' ---
def test_customer_management_update_workflow():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core
    create_cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Henry",
        "lastname": "Ford",
        "birthday": "1900-01-01T00:00:00Z",
        "streetAddress": "Car St 1",
        "postalCode": "6000",
        "city": "Lucerne",
        "email": f"henry_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-5555"
    }
    resp = requests.post(create_cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update in customer-management
    update_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_payload = {
        "firstname": "Henry",
        "lastname": "Ford II",
        "birthday": "1900-01-01T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-5555",
        "moveHistory": []
    }
    resp = requests.put(update_url, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Verify in customer-management
    resp = requests.get(update_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=1279  name='Customer Management Interactions Errors' ---
def test_customer_management_interactions_errors():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    create_cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Frank",
        "lastname": "Green",
        "birthday": "1988-08-08T00:00:00Z",
        "streetAddress": "Maple St 5",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"frank_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(create_cust_url, json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Ensure customer exists in management backend
    get_cust_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    int_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    # 400 Empty interaction ID
    resp = requests.patch(int_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
