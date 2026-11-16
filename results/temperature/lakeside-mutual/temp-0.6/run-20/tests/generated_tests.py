# Tests generated in iteration 20
# Captured: 2026-07-09T16:58:52
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1198  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = generate_email()
    password = "Password123!"

    # 1. Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Test Street 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, headers=headers, json=reg_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET user
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 4. Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Test Street 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Test Street 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, headers=headers, json=quote_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Follow-up GET quote request
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert len(status_history) > 0
    assert status_history[-1]["status"] == "REQUEST_SUBMITTED"

    # 5. Policy Management: Poll for Quote Request
    policy_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    found = False
    for _ in range(15):
        resp = requests.get(policy_quote_url, headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, f"Quote request {quote_id} not found in policy-management-backend"

    # 6. Policy Management: Draft Quote
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(policy_quote_url, headers=policy_headers, json=draft_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET on policy-management
    resp = requests.get(policy_quote_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in statuses

    # 7. Self-Service: Poll for QUOTE_RECEIVED
    received = False
    for _ in range(15):
        resp = requests.get(get_quote_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in statuses:
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status not propagated to customer-self-service-backend"

    # 8. Self-Service: Accept Quote
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_quote_url, headers=headers, json=accept_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=1199  name='Customer Self Accept Quote Illegal Transition' ---
def test_customer_self_service_accept_quote_illegal_transition():
    email = generate_email()
    password = "Password123!"

    # Signup & Login
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register Customer
    reg_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Test 2",
        "postalCode": "3000",
        "phoneNumber": "555-4321"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=headers, json=reg_data, timeout=10)
    customer_id = resp.json()["customerId"]

    # Create Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "Test 2", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Test 2", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, headers=headers, json=quote_data, timeout=10)
    quote_id = resp.json()["id"]

    # Try to Accept Quote immediately (status is REQUEST_SUBMITTED) -> Expect 401
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    patch_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.patch(patch_url, headers=headers, json=accept_data, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1200  name='Customer Core Crud' ---
def test_customer_core_crud():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-05-05T00:00:00Z",
        "streetAddress": "Build St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": generate_email(),
        "phoneNumber": "555-9999"
    }
    resp = requests.post(create_url, headers=headers, json=create_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "Bob"

    # Follow-up GET
    get_url_customer = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_customer, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id

    # 2. Update Address
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_data = {
        "streetAddress": "New Build St 2",
        "postalCode": "1001",
        "city": "Lausanne"
    }
    resp = requests.put(addr_url, headers=headers, json=addr_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url_customer, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_customer = resp.json()["customers"][0]
    assert updated_customer["streetAddress"] == "New Build St 2"
    assert updated_customer["postalCode"] == "1001"

    # 3. Update Profile
    update_data = create_data.copy()
    update_data["firstname"] = "Robert"
    update_data["streetAddress"] = "New Build St 2"
    update_data["postalCode"] = "1001"
    update_profile_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.put(update_profile_url, headers=headers, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url_customer, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Robert"

# --- id=1201  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "No",
        "lastname": "Phone",
        "birthday": "1980-05-05T00:00:00Z",
        "streetAddress": "No St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": generate_email()
    }
    resp = requests.post(create_url, headers=headers, json=create_data, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1202  name='Policy Management Crud' ---
def test_policy_management_crud():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer in Core
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Policy",
        "lastname": "Holder",
        "birthday": "1970-01-01T00:00:00Z",
        "streetAddress": "Pol St 1",
        "postalCode": "2000",
        "city": "Geneva",
        "email": generate_email(),
        "phoneNumber": "555-1111"
    }
    resp = requests.post(create_url, headers=core_headers, json=create_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create Policy
    policy_url = get_url("policy-management-backend", "/policies")
    policy_data = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"},
        "insurancePremium": {"amount": 1200, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(policy_url, headers=policy_headers, json=policy_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Follow-up GET
    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    # Update Policy
    update_data = policy_data.copy()
    update_data["policyType"] = "Home"
    resp = requests.put(get_policy_url, headers=policy_headers, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Home"

    # Delete Policy
    resp = requests.delete(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=1203  name='Policy Management Invalid Customer' ---
def test_policy_management_invalid_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_url = get_url("policy-management-backend", "/policies")
    policy_data = {
        "customerId": "non-existent-id-12345",
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"},
        "insurancePremium": {"amount": 1200, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(policy_url, headers=policy_headers, json=policy_data, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1204  name='Customer Management Interaction Log Negative' ---
def test_customer_management_interaction_log_negative():
    # 1. Create a customer in Core to have a valid customer ID
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Log",
        "lastname": "Test",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Log St 1",
        "postalCode": "3000",
        "city": "Bern",
        "email": generate_email(),
        "phoneNumber": "555-2222"
    }
    resp = requests.post(create_url, headers=core_headers, json=create_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Patch with empty lastAcknowledgedInteractionId -> 400
    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    patch_data_400 = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(patch_url, json=patch_data_400, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. Patch with valid id but no log exists -> 404
    patch_data_404 = {"lastAcknowledgedInteractionId": "some-id"}
    resp = requests.patch(patch_url, json=patch_data_404, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1205  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    # Create Customer in Core
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_url = get_url("customer-core", "/customers")
    create_data = {
        "firstname": "Manage",
        "lastname": "Me",
        "birthday": "1985-01-01T00:00:00Z",
        "streetAddress": "Mgmt St 1",
        "postalCode": "4000",
        "city": "Basel",
        "email": generate_email(),
        "phoneNumber": "555-3333"
    }
    resp = requests.post(create_url, headers=core_headers, json=create_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # PUT Customer Profile in Management Backend
    mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_data = {
        "firstname": "Managed",
        "lastname": "Me",
        "birthday": "1985-01-01T00:00:00Z",
        "email": create_data["email"],
        "phoneNumber": "555-3333",
        "moveHistory": [
            {"streetAddress": "Mgmt St 1", "postalCode": "4000", "city": "Basel"}
        ]
    }
    resp = requests.put(mgmt_url, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(mgmt_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
