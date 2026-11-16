# Tests generated in iteration 02
# Captured: 2026-07-09T07:37:27
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1071  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) > 0
    assert customers[0]["customerId"] == customer_id
    assert customers[0]["firstname"] == "John"
    assert customers[0]["lastname"] == "Doe"
    assert customers[0]["streetAddress"] == "123 Main St"
    assert customers[0]["postalCode"] == "12345"
    assert customers[0]["city"] == "Anytown"
    assert "phoneNumber" in customers[0]

    payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert customers[0]["firstname"] == "Johnny"

    address_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "456 New St"
    assert resp.json()["postalCode"] == "54321"
    assert resp.json()["city"] == "Newtown"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert customers[0]["streetAddress"] == "456 New St"
    assert customers[0]["postalCode"] == "54321"
    assert customers[0]["city"] == "Newtown"

# --- id=1072  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "No",
        "lastname": "Phone",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"nophone.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1073  name='Customer Management Update' ---
def test_customer_management_update():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Management",
        "lastname": "Test",
        "streetAddress": "123 Mgmt St",
        "postalCode": "12345",
        "city": "Mgmt City",
        "email": f"mgmt.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_payload = {
        "firstname": "ManagementUpdated",
        "lastname": "TestUpdated",
        "birthday": "1990-01-01T00:00:00Z",
        "email": f"mgmt.updated.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0001",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert customers[0]["firstname"] == "ManagementUpdated"
    assert customers[0]["lastname"] == "TestUpdated"

# --- id=1074  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()

    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Metropolis",
        "streetAddress": "456 High St",
        "postalCode": "54321",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "456 High St", "postalCode": "54321", "city": "Metropolis"},
            "billingAddress": {"streetAddress": "456 High St", "postalCode": "54321", "city": "Metropolis"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    for _ in range(15):
        resp = requests.get(pm_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(pm_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(15):
        resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in statuses

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=1075  name='Customer Self Early Quote Acceptance' ---
def test_customer_self_service_early_quote_acceptance():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Construction City",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Build St", "postalCode": "12345", "city": "Construction City"},
            "billingAddress": {"streetAddress": "123 Build St", "postalCode": "12345", "city": "Construction City"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10)
    quote_id = resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1076  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cc_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "streetAddress": "123 Rabbit Hole",
        "postalCode": "12345",
        "city": "Wonderland",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Health",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Full coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id
    assert resp.json()["policyType"] == "Health"

    policy_payload["policyType"] = "Life"
    resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Life"

    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=1077  name='Policy Management Create Dependency Failure' ---
def test_policy_management_create_dependency_failure():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": "non-existent-id-" + str(uuid.uuid4()),
        "policyType": "Health",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Full coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1078  name='Customer Management Interaction Log Failures' ---
def test_customer_management_interaction_log_failures():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Eve",
        "lastname": "Hacker",
        "streetAddress": "123 Null St",
        "postalCode": "00000",
        "city": "Void",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": "some-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
