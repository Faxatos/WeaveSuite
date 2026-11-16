# Tests generated in iteration 19
# Captured: 2026-07-09T16:28:44
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1192  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_service = "customer-core"

    # 1. Create customer
    create_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-15T00:00:00Z",
        "streetAddress": "100 Original St",
        "postalCode": "10001",
        "city": "New York",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0001"
    }
    create_url = get_url(core_service, "/customers")
    resp = requests.post(create_url, json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "Alice"
    assert customer["streetAddress"] == "100 Original St"

    # 2. Get customer to verify creation
    get_url_ = get_url(core_service, f"/customers/{customer_id}")
    resp = requests.get(get_url_, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert "customers" in fetched
    assert len(fetched["customers"]) == 1
    assert fetched["customers"][0]["customerId"] == customer_id
    assert fetched["customers"][0]["firstname"] == "Alice"
    assert fetched["customers"][0]["lastname"] == "Smith"
    assert fetched["customers"][0]["streetAddress"] == "100 Original St"
    assert fetched["customers"][0]["postalCode"] == "10001"
    assert fetched["customers"][0]["city"] == "New York"

    # 3. Update address
    update_payload = {
        "streetAddress": "200 Updated Ave",
        "postalCode": "20002",
        "city": "Washington"
    }
    update_url = get_url(core_service, f"/customers/{customer_id}/address")
    resp = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "200 Updated Ave"
    assert resp.json()["postalCode"] == "20002"
    assert resp.json()["city"] == "Washington"

    # 4. Get customer to verify update
    resp = requests.get(get_url_, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["customers"][0]["streetAddress"] == "200 Updated Ave"
    assert fetched["customers"][0]["postalCode"] == "20002"
    assert fetched["customers"][0]["city"] == "Washington"

# --- id=1193  name='Self Insurance Quote Workflow' ---
def test_self_service_insurance_quote_workflow():
    self_service = "customer-self-service-backend"
    policy_service = "policy-management-backend"
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Signup
    signup_url = get_url(self_service, "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_url = get_url(self_service, "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    self_headers = {"X-Auth-Token": token}

    # Verify login via GET /user
    resp = requests.get(get_url(self_service, "/user"), headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # 3. Register Customer
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Builderland",
        "streetAddress": "1 Build St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    reg_url = get_url(self_service, "/customers")
    resp = requests.post(reg_url, json=reg_payload, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verify customer registration via GET
    get_cust_url = get_url(self_service, f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 4. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "1 Build St", "postalCode": "12345", "city": "Builderland"},
            "billingAddress": {"streetAddress": "1 Build St", "postalCode": "12345", "city": "Builderland"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    quote_req_url = get_url(self_service, "/insurance-quote-requests")
    resp = requests.post(quote_req_url, json=quote_req_payload, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # Verify quote request via GET
    ss_quote_url = f"{quote_req_url}/{quote_req_id}"
    resp = requests.get(ss_quote_url, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_req_id
    assert resp.json()["insuranceOptions"]["insuranceType"] == "LIFE"

    # 5. Policy-Management: poll GET until 200 (async arrival)
    pm_quote_url = get_url(policy_service, f"/insurance-quote-requests/{quote_req_id}")
    found = False
    for _ in range(15):
        resp = requests.get(pm_quote_url, headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, f"Quote request {quote_req_id} did not arrive in policy-management"

    # 6. Policy-Management: Draft Quote (QUOTE_RECEIVED)
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(pm_quote_url, json=draft_payload, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["insuranceQuote"]["insurancePremium"]["amount"] == 500
    assert resp.json()["insuranceQuote"]["policyLimit"]["amount"] == 100000

    # 7. Self-Service: Poll GET until QUOTE_RECEIVED
    quote_received = False
    for _ in range(15):
        resp = requests.get(ss_quote_url, headers=self_headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            statuses = [s.get("status") for s in data.get("statusHistory", [])]
            if "QUOTE_RECEIVED" in statuses:
                quote_received = True
                break
        time.sleep(1)
    assert quote_received, "Quote status QUOTE_RECEIVED did not propagate to self-service"

    # 8. Self-Service: Accept Quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify accepted via GET
    resp = requests.get(ss_quote_url, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    statuses = [s.get("status") for s in data.get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses
    assert data["insuranceQuote"]["insurancePremium"]["amount"] == 500
    assert data["insuranceQuote"]["insurancePremium"]["currency"] == "USD"
    assert data["insuranceQuote"]["policyLimit"]["amount"] == 100000
    assert data["insuranceQuote"]["policyLimit"]["currency"] == "USD"

# --- id=1194  name='Policy Management Create Policy And' ---
def test_policy_management_create_policy_and_delete():
    core_service = "customer-core"
    policy_service = "policy-management-backend"
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer
    create_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": f"charlie.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0002"
    }
    resp = requests.post(get_url(core_service, "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET for customer
    get_url_ = get_url(core_service, f"/customers/{customer_id}")
    resp = requests.get(get_url_, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Create Policy
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "policyType": "HOME",
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 1500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Fire Coverage", "description": "Covers fire damage"}
            ]
        }
    }
    policy_url = get_url(policy_service, "/policies")
    resp = requests.post(policy_url, json=policy_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]
    assert resp.json()["customer"] == customer_id

    # 3. Get Policy
    get_policy_url = get_url(policy_service, f"/policies/{policy_id}")
    resp = requests.get(get_policy_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["policyType"] == "HOME"
    assert resp.json()["deductible"]["amount"] == 1000
    assert resp.json()["policyLimit"]["amount"] == 500000
    assert resp.json()["insurancePremium"]["amount"] == 1500

    # 4. Delete Policy
    resp = requests.delete(get_policy_url, headers=headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # 5. Follow-up GET to verify deletion
    resp = requests.get(get_url(policy_service, "/policies"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_ids = [p["policyId"] for p in resp.json().get("policies", [])]
    assert policy_id not in policy_ids

# --- id=1195  name='Customer Management Interaction Log Negative Paths' ---
def test_customer_management_interaction_log_negative_paths():
    core_service = "customer-core"
    mgmt_service = "customer-management-backend"
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer
    create_payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1980-03-22T00:00:00Z",
        "streetAddress": "1 Themyscira Ave",
        "postalCode": "00001",
        "city": "Island",
        "email": f"diana.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0003"
    }
    resp = requests.post(get_url(core_service, "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET for creation
    get_url_ = get_url(core_service, f"/customers/{customer_id}")
    resp = requests.get(get_url_, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. PATCH empty lastAcknowledgedInteractionId -> 400
    patch_url = get_url(mgmt_service, f"/interaction-logs/{customer_id}")
    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1196  name='Self Accept Quote Too Early 401' ---
def test_self_service_accept_quote_too_early_401():
    self_service = "customer-self-service-backend"

    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Signup & Login
    resp = requests.post(get_url(self_service, "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url(self_service, "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    self_headers = {"X-Auth-Token": token}

    # Follow-up GET /user
    resp = requests.get(get_url(self_service, "/user"), headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Register Customer
    reg_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1995-05-05T00:00:00Z",
        "city": "Eden",
        "streetAddress": "1 Apple Way",
        "postalCode": "12345",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url(self_service, "/customers"), json=reg_payload, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET /customers/{customerId}
    resp = requests.get(get_url(self_service, f"/customers/{customer_id}"), headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "Adams",
            "contactAddress": {"streetAddress": "1 Apple Way", "postalCode": "12345", "city": "Eden"},
            "billingAddress": {"streetAddress": "1 Apple Way", "postalCode": "12345", "city": "Eden"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp = requests.post(get_url(self_service, "/insurance-quote-requests"), json=quote_req_payload, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # Follow-up GET /insurance-quote-requests/{id}
    ss_quote_url = get_url(self_service, f"/insurance-quote-requests/{quote_req_id}")
    resp = requests.get(ss_quote_url, headers=self_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Attempt to accept quote in REQUEST_SUBMITTED state -> 401
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(ss_quote_url, json=accept_payload, headers=self_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1197  name='Customer Core Create Missing Phone 500' ---
def test_customer_core_create_missing_phone_500():
    core_service = "customer-core"
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    create_payload = {
        "firstname": "Error",
        "lastname": "User",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Error St",
        "postalCode": "12345",
        "city": "Error City",
        "email": f"error.{uuid.uuid4()}@example.com"
        # phoneNumber is deliberately omitted to trigger 500
    }
    resp = requests.post(get_url(core_service, "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"
