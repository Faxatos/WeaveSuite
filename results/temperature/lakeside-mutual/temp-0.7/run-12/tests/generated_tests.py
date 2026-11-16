# Tests generated in iteration 12
# Captured: 2026-07-10T00:16:51
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1286  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "Password123!"

    # Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Register customer
    cust_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Main St",
        "postalCode": "10001",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(cust_url, headers=headers, json=reg_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Verify customer GET
    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Create quote request
    quote_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "10001", "city": "New York"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "10001", "city": "New York"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(quote_url, headers=headers, json=quote_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Poll Service 4 for quote request
    svc4_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    svc4_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    for _ in range(15):
        resp = requests.get(svc4_quote_url, headers=svc4_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Draft quote on Service 4
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(svc4_quote_url, headers=svc4_headers, json=draft_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Poll Service 3 for QUOTE_RECEIVED
    svc3_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(15):
        resp = requests.get(svc3_quote_url, headers=headers, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        statuses = [s.get("status") for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            received = True
            break
        time.sleep(1)
    assert received, "Quote request did not reach QUOTE_RECEIVED state on customer-self-service-backend"

    # Accept quote on Service 3
    accept_payload = {
        "status": "QUOTE_ACCEPTED"
    }
    resp = requests.patch(svc3_quote_url, headers=headers, json=accept_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify QUOTE_ACCEPTED
    resp = requests.get(svc3_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    statuses = [s.get("status") for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses, f"Expected QUOTE_ACCEPTED in statusHistory, got {statuses}"

# --- id=1287  name='Customer Core Policy Workflow' ---
def test_customer_core_policy_workflow():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer on Service 1
    cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "20002",
        "city": "Washington",
        "email": f"alice_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(cust_url, headers=headers, json=cust_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # GET customer to verify
    get_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id

    # Create policy on Service 4
    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 250, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Liability"}]}
    }
    resp = requests.post(pol_url, headers=headers, json=pol_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # GET policy to verify
    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}?expand=customer")
    resp = requests.get(get_pol_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert "customer" in resp.json()

# --- id=1288  name='Customer Self Illegal Status Transition' ---
def test_customer_self_service_illegal_status_transition():
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "Password123!"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers = {"X-Auth-Token": resp.json()["token"]}

    reg_payload = {
        "firstname": "Bob", "lastname": "Builder", "birthday": "1980-01-01T00:00:00Z",
        "city": "Town", "streetAddress": "1 Rd", "postalCode": "12345", "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=headers, json=reg_payload, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob", "lastname": "Builder",
            "contactAddress": {"streetAddress": "1 Rd", "postalCode": "12345", "city": "Town"},
            "billingAddress": {"streetAddress": "1 Rd", "postalCode": "12345", "city": "Town"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z", "insuranceType": "Home", "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), headers=headers, json=quote_payload, timeout=10)
    quote_id = resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED"
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, json=accept_payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1289  name='Policy Management Missing Customer' ---
def test_policy_management_missing_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": f"nonexistent-{uuid.uuid4().hex}",
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 250, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Liability"}]}
    }
    resp = requests.post(pol_url, headers=headers, json=pol_payload, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1290  name='Customer Core Missing Phone Number Internal Error' ---
def test_customer_core_missing_phone_number_internal_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "20002",
        "city": "Washington",
        "email": f"alice_{uuid.uuid4().hex}@example.com"
    }
    resp = requests.post(cust_url, headers=headers, json=cust_payload, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1291  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    cust_id = f"cust-{uuid.uuid4().hex}"
    log_url = get_url("customer-management-backend", f"/interaction-logs/{cust_id}")

    resp = requests.patch(log_url, json={}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.patch(log_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.patch(log_url, json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1292  name='Customer Core Update Customer' ---
def test_customer_core_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1990-10-10T00:00:00Z",
        "streetAddress": "789 Pine St",
        "postalCode": "30003",
        "city": "Atlanta",
        "email": f"charlie_{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(cust_url, headers=headers, json=cust_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_url = get_url("customer-core", f"/customers/{customer_id}")
    update_payload = cust_payload.copy()
    update_payload["firstname"] = "Charles"

    resp = requests.put(update_url, headers=headers, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["firstname"] == "Charles"

    get_url_ids = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_ids, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Charles"

# --- id=1293  name='Policy Management Quote Request Not Found' ---
def test_policy_management_quote_request_not_found():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_id = 999999999
    url = get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
