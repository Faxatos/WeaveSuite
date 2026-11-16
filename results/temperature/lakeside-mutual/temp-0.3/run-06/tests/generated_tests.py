# Tests generated in iteration 06
# Captured: 2026-07-07T20:23:47
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=606  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    # Create customer
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_random_email(),
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    # GET customer
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_customer = resp.json()
    assert "customers" in get_customer
    assert len(get_customer["customers"]) == 1
    assert get_customer["customers"][0]["customerId"] == customer_id
    assert get_customer["customers"][0]["firstname"] == "John"

    # Update customer
    update_payload = payload.copy()
    update_payload["firstname"] = "Jane"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_customer = resp.json()
    assert updated_customer["firstname"] == "Jane"

    # GET customer again
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_customer = resp.json()
    assert get_customer["customers"][0]["firstname"] == "Jane"

# --- id=607  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    # Create customer
    payload = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "100 Old St",
        "postalCode": "10000",
        "city": "Old City",
        "email": generate_random_email(),
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Change address
    address_payload = {
        "streetAddress": "200 New St",
        "postalCode": "20000",
        "city": "New City"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # GET customer to verify
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_customer = resp.json()
    assert get_customer["customers"][0]["streetAddress"] == "200 New St"
    assert get_customer["customers"][0]["postalCode"] == "20000"
    assert get_customer["customers"][0]["city"] == "New City"

# --- id=608  name='Customer Core Create Customer Missing Phone Number 500' ---
def test_customer_core_create_customer_missing_phone_number_500():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": generate_random_email()
        # phoneNumber is missing
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=609  name='Policy Management Create Policy For Existing Customer' ---
def test_policy_management_create_policy_for_existing_customer():
    # Create customer in core
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": generate_random_email(),
        "phoneNumber": "555-5678"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create policy
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    policy_id = policy["policyId"]
    assert policy["customer"] == customer_id
    assert policy["policyType"] == "Life"

    # GET policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_policy = resp.json()
    assert get_policy["policyId"] == policy_id
    assert get_policy["customer"] == customer_id

    # DELETE policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=610  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=611  name='Customer Management Interaction Log Empty Id 400' ---
def test_customer_management_patch_interaction_log_empty_id_400():
    # Create customer in core
    payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Eve St",
        "postalCode": "12345",
        "city": "Evetown",
        "email": generate_random_email(),
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    patch_payload = {
        "lastAcknowledgedInteractionId": ""
    }
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=612  name='Customer Management Interaction Log Not Found 404' ---
def test_customer_management_patch_interaction_log_not_found_404():
    # Create customer in core
    payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildtown",
        "email": generate_random_email(),
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # PATCH interaction log with valid id but no log exists
    patch_payload = {
        "lastAcknowledgedInteractionId": "interaction-123"
    }
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=613  name='End To End Insurance Quote Workflow' ---
def test_end_to_end_insurance_quote_workflow():
    # 1. Signup
    email = generate_random_email()
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    self_service_headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "NW1",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 4. Create Insurance Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "1 Cinema Rd", "postalCode": "NW1", "city": "London"},
            "billingAddress": {"streetAddress": "1 Cinema Rd", "postalCode": "NW1", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_request = resp.json()
    quote_request_id = quote_request["id"]

    # 5. Policy Management: Poll GET until 200
    max_retries = 10
    found = False
    for _ in range(max_retries):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_request_id}"), headers=POLICY_HEADERS, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Insurance quote request did not propagate to policy-management-backend"

    # 6. Policy Management: Draft Quote (PATCH)
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_request_id}"), json=draft_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 7. Self-Service: Poll GET until QUOTE_RECEIVED
    found_status = False
    for _ in range(max_retries):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_request_id}"), headers=self_service_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in history):
                found_status = True
                break
        time.sleep(1)
    assert found_status, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    # 8. Self-Service: Accept Quote (PATCH)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_request_id}"), json=accept_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 9. Self-Service: Verify QUOTE_ACCEPTED
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_request_id}"), headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in history), "QUOTE_ACCEPTED not found in status history"

# --- id=614  name='Self Quote Request Submitted 401' ---
def test_self_service_patch_quote_request_submitted_401():
    # 1. Signup
    email = generate_random_email()
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    self_service_headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Themyscira",
        "streetAddress": "1 Palace Rd",
        "postalCode": "00001",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 4. Create Insurance Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Diana",
            "lastname": "Prince",
            "contactAddress": {"streetAddress": "1 Palace Rd", "postalCode": "00001", "city": "Themyscira"},
            "billingAddress": {"streetAddress": "1 Palace Rd", "postalCode": "00001", "city": "Themyscira"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_request_id = resp.json()["id"]

    # 5. Self-Service: Accept Quote immediately (in REQUEST_SUBMITTED state) -> expect 401
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_request_id}"), json=accept_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
