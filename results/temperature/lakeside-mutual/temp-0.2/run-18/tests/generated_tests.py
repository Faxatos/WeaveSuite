# Tests generated in iteration 18
# Captured: 2026-07-07T12:40:55
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=499  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["customers"][0]["customerId"] == customer_id

    update_payload = create_payload.copy()
    update_payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated = resp.json()
    assert updated["firstname"] == "Johnny"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_updated = resp.json()
    assert fetched_updated["customers"][0]["firstname"] == "Johnny"

# --- id=500  name='Customer Core Missing Phone Number Error' ---
def test_customer_core_missing_phone_number_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    create_payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=501  name='Policy Management Create Policy And' ---
def test_policy_management_create_policy_and_delete():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    create_customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"alice.smith.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_customer_payload, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}
    create_policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=create_policy_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    policy_id = policy["policyId"]
    assert policy["customer"] == customer_id

    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_policy = resp.json()
    assert fetched_policy["policyId"] == policy_id

    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_policy, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=502  name='Policy Management Create Policy Failed Dependency' ---
def test_policy_management_create_policy_failed_dependency():
    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}
    create_policy_payload = {
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
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=create_policy_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=503  name='Self Insurance Quote Workflow' ---
def test_self_service_insurance_quote_workflow():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    auth_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers_self = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Buildtown",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Build St", "postalCode": "12345", "city": "Buildtown"},
            "billingAddress": {"streetAddress": "123 Build St", "postalCode": "12345", "city": "Buildtown"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}
    max_retries = 10
    found = False
    for _ in range(max_retries):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers_policy, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), json=draft_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    found_status = False
    for _ in range(max_retries):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers_self, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in history):
                found_status = True
                break
        time.sleep(1)
    assert found_status, "QUOTE_RECEIVED status did not propagate to self-service"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in history)

# --- id=504  name='Self Accept Quote Illegal Transition' ---
def test_self_service_accept_quote_illegal_transition():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    auth_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers_self = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Filmcity",
        "streetAddress": "123 Film St",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Film St", "postalCode": "12345", "city": "Filmcity"},
            "billingAddress": {"streetAddress": "123 Film St", "postalCode": "12345", "city": "Filmcity"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=headers_self, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=505  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    create_customer_payload = {
        "firstname": "Dave",
        "lastname": "Davidson",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"dave.davidson.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_customer_payload, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    ack_payload = {"lastAcknowledgedInteractionId": "some-id"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=506  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    create_customer_payload = {
        "firstname": "Eve",
        "lastname": "Evans",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"eve.evans.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_customer_payload, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_payload = {
        "firstname": "Eve Updated",
        "lastname": "Evans",
        "birthday": "1985-05-05T00:00:00Z",
        "email": f"eve.evans.updated.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-management-backend", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["customerId"] == customer_id

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_core = resp.json()
    assert fetched_core["customers"][0]["firstname"] == "Eve Updated"
