# Tests generated in iteration 17
# Captured: 2026-07-08T02:39:39
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=706  name='Customer Self Backend Registration And Core Update' ---
def test_customer_self_service_backend_registration_and_core_update():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers_self = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    customer_id = resp_json["customerId"]

    links = resp_json.get("_links", {})
    if "self" in links:
        self_href = links["self"]["href"]
        customer_url_self = self_href if self_href.startswith("http") else get_url("customer-self-service-backend", self_href)
    else:
        customer_url_self = get_url("customer-self-service-backend", f"/customers/{customer_id}")

    resp = requests.get(customer_url_self, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_url_core = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(customer_url_core, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) == 1
    assert customers[0]["customerId"] == customer_id
    assert customers[0]["firstname"] == "John"

    update_data = {
        "firstname": "John",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 2",
        "postalCode": "8000",
        "email": email,
        "phoneNumber": "555-1234"
    }
    resp = requests.put(customer_url_core, json=update_data, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(customer_url_core, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert customers[0]["lastname"] == "Smith"
    assert customers[0]["streetAddress"] == "Main St 2"

# --- id=707  name='Customer Self Backend Insurance Quote Workflow' ---
def test_customer_self_service_backend_insurance_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_self = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_self, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    quote_url_self = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.get(quote_url_self, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_req_id

    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}
    quote_url_policy = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}")

    success = False
    for _ in range(15):
        resp = requests.get(quote_url_policy, headers=headers_policy, timeout=10)
        if resp.status_code == 200:
            success = True
            break
        time.sleep(1)
    assert success, f"Expected 200 from policy-management GET, got {resp.status_code}"

    patch_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(quote_url_policy, json=patch_data, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(quote_url_policy, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "insuranceQuote" in resp.json()
    assert resp.json()["insuranceQuote"]["insurancePremium"]["amount"] == 100

    success = False
    for _ in range(15):
        resp = requests.get(quote_url_self, headers=headers_self, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in status_history:
            success = True
            break
        time.sleep(1)
    assert success, "Expected QUOTE_RECEIVED in statusHistory"

    resp = requests.patch(quote_url_self, json={"status": "QUOTE_ACCEPTED"}, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(quote_url_self, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in status_history

# --- id=708  name='Customer Self Backend Quote Illegal Transition 401' ---
def test_customer_self_service_backend_quote_illegal_transition_401():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_self = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_self, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    quote_url_self = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.patch(quote_url_self, json={"status": "QUOTE_ACCEPTED"}, headers=headers_self, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=709  name='Policy Management Backend Creation And Deletion' ---
def test_policy_management_backend_creation_and_deletion():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_data = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "1234",
        "city": "Wonderland",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    policy_data = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 1200, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Liability"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    policy_id = resp_json["policyId"]

    links = resp_json.get("_links", {})
    if "self" in links:
        self_href = links["self"]["href"]
        policy_url = self_href if self_href.startswith("http") else get_url("policy-management-backend", self_href)
    else:
        policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")

    resp = requests.get(policy_url, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    resp = requests.delete(policy_url, headers=headers_policy, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=710  name='Customer Core Missing Phone Number 500' ---
def test_customer_core_missing_phone_number_500():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_data = {
        "firstname": "Error",
        "lastname": "Prone",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Bug St 1",
        "postalCode": "1234",
        "city": "BugCity",
        "email": f"error_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_data = customer_data.copy()
    del update_data["phoneNumber"]

    customer_url_core = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.put(customer_url_core, json=update_data, headers=headers_core, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=711  name='Customer Management Backend Interaction Log Empty Ack 400' ---
def test_customer_management_backend_interaction_log_empty_ack_400():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_data = {
        "firstname": "Ack",
        "lastname": "Test",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Ack St 1",
        "postalCode": "1234",
        "city": "AckCity",
        "email": f"ack_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(log_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=712  name='Customer Self Backend Change Address' ---
def test_customer_self_service_backend_change_address():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_self = {"X-Auth-Token": token}

    reg_data = {
        "firstname": "Address",
        "lastname": "Changer",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "OldCity",
        "streetAddress": "Old St 1",
        "postalCode": "1000",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    new_address = {
        "streetAddress": "New St 2",
        "postalCode": "2000",
        "city": "NewCity"
    }
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    resp = requests.put(addr_url, json=new_address, headers=headers_self, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    core_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_url, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) == 1
    assert customers[0]["streetAddress"] == "New St 2"
    assert customers[0]["postalCode"] == "2000"
    assert customers[0]["city"] == "NewCity"
