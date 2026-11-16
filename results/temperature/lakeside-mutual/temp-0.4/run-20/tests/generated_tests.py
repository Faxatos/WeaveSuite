# Tests generated in iteration 20
# Captured: 2026-07-08T19:48:23
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=907  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = get_core_headers()

    # Negative test: missing phoneNumber -> 500
    bad_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

    # Positive test: create customer
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    # Verify creation
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_customer = resp.json()["customers"][0]
    assert fetched_customer["firstname"] == "John"

    # Update customer
    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_customer = resp.json()["customers"][0]
    assert fetched_customer["firstname"] == "Johnny"

# --- id=908  name='Self Signup And Register Customer' ---
def test_self_service_signup_and_register_customer():
    email = f"user_{random_string()}@example.com"
    password = "password123"

    # Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()

    # Verify user details before registration
    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()

    # Register customer
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verify user details after registration
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Verify customer details
    resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=909  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    # 1. Setup user and customer in self-service
    email = f"quote_{random_string()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Builderland",
        "streetAddress": "123 Brick Ln",
        "postalCode": "54321",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # 2. Create quote request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Brick Ln", "postalCode": "54321", "city": "Builderland"},
            "billingAddress": {"streetAddress": "123 Brick Ln", "postalCode": "54321", "city": "Builderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Verify creation in self-service
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Negative: Try to accept quote before it's drafted -> 401
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json={"status": "QUOTE_ACCEPTED"}, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 3. Policy management drafts quote
    pm_headers = get_policy_headers()

    # Poll until available in policy management
    max_retries = 15
    found = False
    for _ in range(max_retries):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Self-service accepts quote
    # Poll until QUOTE_RECEIVED in self-service
    found = False
    for _ in range(max_retries):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                found = True
                break
        time.sleep(1)
    assert found, "QUOTE_RECEIVED status did not propagate to self-service-backend"

    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json={"status": "QUOTE_ACCEPTED"}, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify accepted
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=910  name='Policy Management Create Policy' ---
def test_policy_management_create_policy():
    core_headers = get_core_headers()
    pm_headers = get_policy_headers()

    # Negative: Create policy for non-existent customer -> 424
    fake_customer_id = str(uuid.uuid4())
    policy_payload = {
        "customerId": fake_customer_id,
        "policyType": "AUTO",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

    # Create real customer in core
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "streetAddress": "123 Cinema St",
        "postalCode": "98765",
        "city": "Hollywood",
        "email": "charlie@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Positive: Create policy
    policy_payload["customerId"] = customer_id
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Verify policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    assert policy["customer"] == customer_id
    assert policy["policyType"] == "AUTO"

# --- id=911  name='Customer Management Interaction Logs Errors' ---
def test_customer_management_interaction_logs_errors():
    core_headers = get_core_headers()

    # Create customer in core
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "streetAddress": "123 Rock St",
        "postalCode": "11111",
        "city": "Seattle",
        "email": "dave@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Negative: empty lastAcknowledgedInteractionId -> 400
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Negative: valid lastAcknowledgedInteractionId but no log exists -> 404
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": "some-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=912  name='Policy Management Quote Request Not Found' ---
def test_policy_management_quote_request_not_found():
    pm_headers = get_policy_headers()
    fake_id = 999999999

    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=913  name='Self Change Address' ---
def test_self_service_change_address():
    # Setup user and customer
    email = f"addr_{random_string()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1975-01-01T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Punisher St",
        "postalCode": "10001",
        "phoneNumber": "555-6666"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # Change address
    addr_payload = {
        "streetAddress": "456 Safehouse Ave",
        "postalCode": "10002",
        "city": "New York"
    }
    resp = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), json=addr_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "456 Safehouse Ave"

    # Verify address change in customer-core
    core_headers = get_core_headers()
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_customer = resp.json()["customers"][0]
    assert fetched_customer["streetAddress"] == "456 Safehouse Ave"
    assert fetched_customer["postalCode"] == "10002"
    assert fetched_customer["city"] == "New York"

# --- id=914  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    core_headers = get_core_headers()
    pm_headers = get_policy_headers()

    # Create customer
    cust_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "streetAddress": "123 Navy St",
        "postalCode": "33333",
        "city": "Arlington",
        "email": "grace@example.com",
        "phoneNumber": "555-7777"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # Create policy
    policy_payload = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 200000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Delete policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Verify deletion by checking list
    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies)

# --- id=915  name='Self Quote Request Wrong Customer Id' ---
def test_self_service_quote_request_wrong_customer_id():
    # Setup user and customer
    email = f"wrong_{random_string()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Laura",
        "lastname": "Croft",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Manor St",
        "postalCode": "99999",
        "phoneNumber": "555-1313"
    }
    requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)

    # Create quote request with wrong customerId
    wrong_customer_id = str(uuid.uuid4())
    quote_req_payload = {
        "customerInfo": {
            "customerId": wrong_customer_id,
            "firstname": "Laura",
            "lastname": "Croft",
            "contactAddress": {"streetAddress": "123 Manor St", "postalCode": "99999", "city": "London"},
            "billingAddress": {"streetAddress": "123 Manor St", "postalCode": "99999", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=916  name='Customer Management Interaction Log Empty' ---
def test_customer_management_get_interaction_log_empty():
    core_headers = get_core_headers()

    # Create customer
    cust_payload = {
        "firstname": "Mike",
        "lastname": "Wazowski",
        "streetAddress": "123 Scare St",
        "postalCode": "12345",
        "city": "Monstropolis",
        "email": "mike@example.com",
        "phoneNumber": "555-1010"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    customer_id = resp.json()["customerId"]

    # GET interaction log
    resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    log = resp.json()
    assert log.get("customerId") == customer_id or not log.get("interactions")
