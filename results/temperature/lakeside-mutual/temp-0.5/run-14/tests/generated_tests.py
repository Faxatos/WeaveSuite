# Tests generated in iteration 14
# Captured: 2026-07-09T03:18:38
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1020  name='Customer Core Crud And Negative' ---
def test_customer_core_crud_and_negative():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Negative: absent phoneNumber -> 500
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

    # Positive: create customer
    good_payload = bad_payload.copy()
    good_payload["phoneNumber"] = "555-1234"
    resp = requests.post(get_url("customer-core", "/customers"), json=good_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    cust_id = customer["customerId"]
    assert customer["firstname"] == "John"
    assert customer["lastname"] == "Doe"
    assert customer["streetAddress"] == "123 Main St"
    assert customer["postalCode"] == "12345"
    assert customer["city"] == "Anytown"
    assert customer["email"] == "john@example.com"
    assert "phoneNumber" in customer

    # Follow-up GET customer
    resp = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json()["customers"][0]
    assert cust_data["customerId"] == cust_id
    assert cust_data["firstname"] == "John"
    assert cust_data["lastname"] == "Doe"
    assert cust_data["streetAddress"] == "123 Main St"

    # PUT update customer
    update_payload = good_payload.copy()
    update_payload["firstname"] = "Johnny"
    update_payload["city"] = "Othertown"
    resp = requests.put(get_url("customer-core", f"/customers/{cust_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_cust = resp.json()
    assert updated_cust["firstname"] == "Johnny"
    assert updated_cust["city"] == "Othertown"

    # Follow-up GET customer to verify update
    resp = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json()["customers"][0]
    assert cust_data["firstname"] == "Johnny"
    assert cust_data["city"] == "Othertown"

    # PUT update address
    addr_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{cust_id}/address"), json=addr_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_resp = resp.json()
    assert addr_resp["streetAddress"] == "456 New St"
    assert addr_resp["postalCode"] == "54321"
    assert addr_resp["city"] == "Newtown"

    # Follow-up GET customer to verify address
    resp = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_data = resp.json()["customers"][0]
    assert cust_data["streetAddress"] == "456 New St"
    assert cust_data["postalCode"] == "54321"
    assert cust_data["city"] == "Newtown"

# --- id=1021  name='Policy Management Policy Lifecycle' ---
def test_policy_management_policy_lifecycle():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}

    # Negative: Create policy with fake customer -> 424
    policy_payload = {
        "customerId": str(uuid.uuid4()),
        "policyType": "AUTO",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

    # Create real customer in core
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    # Positive: Create policy with real customer
    policy_payload["customerId"] = cust_id
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    policy_id = policy["policyId"]
    assert policy["customer"] == cust_id
    assert policy["policyType"] == "AUTO"
    assert policy["deductible"]["amount"] == 500
    assert policy["policyLimit"]["amount"] == 100000
    assert policy["insurancePremium"]["amount"] == 1000

    # Follow-up GET policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_policy = resp.json()
    assert fetched_policy["policyId"] == policy_id
    assert fetched_policy["customer"] == cust_id
    assert fetched_policy["policyType"] == "AUTO"
    assert fetched_policy["deductible"]["amount"] == 500

    # DELETE policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_policy, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET on listing to verify deletion
    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = [p["policyId"] for p in resp.json().get("policies", [])]
    assert policy_id not in policies

# --- id=1022  name='Self And Policy Quote Workflow' ---
def test_self_service_and_policy_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    # 1. Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()

    # 2. Login
    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    assert token is not None
    headers_ss = {"X-Auth-Token": token}

    # Follow-up GET /user
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()

    # 3. Register Customer
    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Buildtown",
        "streetAddress": "1 Construction Way",
        "postalCode": "98765",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust = resp.json()
    cust_id = cust["customerId"]
    assert cust_id is not None

    # Follow-up GET /user to see customerId populated
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == cust_id

    # Follow-up GET /customers/{customerId}
    resp = requests.get(get_url("customer-self-service-backend", f"/customers/{cust_id}"), headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == cust_id

    # 4. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": cust_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "1 Construction Way", "postalCode": "98765", "city": "Buildtown"},
            "billingAddress": {"streetAddress": "1 Construction Way", "postalCode": "98765", "city": "Buildtown"}
        },
        "insuranceOptions": {
            "startDate": "2023-12-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req = resp.json()
    quote_req_id = quote_req["id"]
    assert quote_req["customerInfo"]["customerId"] == cust_id
    assert quote_req["insuranceOptions"]["insuranceType"] == "HOME"

    # Follow-up GET quote request
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_req_id

    # 5. Try to accept quote on self-service before drafted -> 401
    accept_payload = {"status": "QUOTE_ACCEPTED"}
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=accept_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 6. Poll Policy Management for the quote request
    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}")
    found = False
    for _ in range(15):
        resp = requests.get(policy_url, headers=headers_policy, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # 7. Draft quote on Policy Management
    future_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": future_date,
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    resp = requests.patch(policy_url, json=draft_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    patched_quote = resp.json()
    assert patched_quote["insuranceQuote"]["insurancePremium"]["amount"] == 500

    # Follow-up GET on policy management
    resp = requests.get(policy_url, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["insuranceQuote"]["policyLimit"]["amount"] == 500000

    # 8. Poll Self-Service until QUOTE_RECEIVED
    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}")
    received = False
    for _ in range(15):
        resp = requests.get(ss_url, headers=headers_ss, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        history = [s["status"] for s in resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in history:
            received = True
            break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to self-service-backend"

    # 9. Accept quote on Self-Service
    resp = requests.patch(ss_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify accepted
    resp = requests.get(ss_url, headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=1023  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create real customer in core
    cust_payload = {
        "firstname": "Dave",
        "lastname": "Log",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"dave_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers_core, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    url = get_url("customer-management-backend", f"/interaction-logs/{cust_id}")

    # 400 case: missing/empty lastAcknowledgedInteractionId
    bad_payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(url, json=bad_payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 404 case: valid payload, but no log exists for this new customer
    good_payload = {"lastAcknowledgedInteractionId": "123"}
    resp = requests.patch(url, json=good_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
