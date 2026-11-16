# Tests generated in iteration 19
# Captured: 2026-07-07T13:12:29
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=507  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    # Get customer
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_customer = resp.json()["customers"][0]
    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["firstname"] == "John"

    # Update customer
    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Johnny"

    # Update address
    address_payload = {
        "streetAddress": "789 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify address update
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_customer = resp.json()["customers"][0]
    assert fetched_customer["streetAddress"] == "789 New St"
    assert fetched_customer["postalCode"] == "54321"
    assert fetched_customer["city"] == "Newtown"

    # Negative test: Create without phoneNumber
    bad_payload = payload.copy()
    del bad_payload["phoneNumber"]
    resp = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=508  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core
    customer_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": "jane.smith@example.com",
        "phoneNumber": "555-5678"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create policy
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    policy_id = policy["policyId"]
    assert policy["customer"] == customer_id

    # Get policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id

    # Delete policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Negative test: Create policy with non-existent customer
    bad_policy_payload = policy_payload.copy()
    bad_policy_payload["customerId"] = "non-existent-id-123"
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=bad_policy_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=509  name='Insurance Quote Workflow' ---
def test_insurance_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    # Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]

    self_service_headers = {"X-Auth-Token": token}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Register customer profile
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1992-02-02T00:00:00Z",
        "city": "Wonder City",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "11111",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Create quote request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonderland",
            "contactAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "11111", "city": "Wonder City"},
            "billingAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "11111", "city": "Wonder City"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # Negative test: Try to accept quote before it's drafted (in REQUEST_SUBMITTED state)
    accept_payload = {"status": "QUOTE_ACCEPTED"}
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Poll policy-management until request is available
    max_retries = 10
    for _ in range(max_retries):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management-backend")

    # Draft quote on policy-management
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 1500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), json=draft_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Poll self-service until QUOTE_RECEIVED
    for _ in range(max_retries):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=self_service_headers, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in status_history:
            break
        time.sleep(1)
    else:
        pytest.fail("QUOTE_RECEIVED status did not propagate to customer-self-service-backend")

    # Accept quote on self-service
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify final state
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=self_service_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in status_history

# --- id=510  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    # Get interaction log for a non-existent customer
    fake_customer_id = f"fake-{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{fake_customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Try to acknowledge interactions for a customer with no log
    ack_payload = {"lastAcknowledgedInteractionId": "123"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{fake_customer_id}"), json=ack_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=511  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in core first
    customer_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildtown",
        "email": "bob@example.com",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Get customer in management backend
    resp = requests.get(get_url("customer-management-backend", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Update customer in management backend
    update_payload = {
        "firstname": "Bobby",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "email": "bobby@example.com",
        "phoneNumber": "555-9999",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("customer-management-backend", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
