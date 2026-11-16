# Tests generated in iteration 01
# Captured: 2026-07-09T18:44:03
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1213  name='Customer Core Create And Update' ---
def test_customer_core_create_and_update():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer
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
    customer_id = resp.json()["customerId"]

    # Follow-up GET
    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customers"][0]["firstname"] == "John"

    # 2. Update address
    addr_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    resp_addr = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=addr_payload, headers=headers, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    # Follow-up GET
    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["streetAddress"] == "456 New St"

    # 3. Update full profile
    put_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown",
        "email": "john.doe_updated@example.com",
        "phoneNumber": "555-1234"
    }
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=put_payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    # Follow-up GET
    resp_get3 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert resp_get3.json()["customers"][0]["email"] == "john.doe_updated@example.com"

# --- id=1214  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    # Negative Test: Missing phoneNumber raises 500
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "jane.doe@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1215  name='Self End To End Registration' ---
def test_self_service_end_to_end_registration():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Signup
    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    # 2. Login to get token
    auth_payload = {"email": email, "password": password}
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register customer
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "100 Self St",
        "postalCode": "11111",
        "city": "SelfCity",
        "phoneNumber": "555-9999"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    # Follow-up GET /user
    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["customerId"] == customer_id

    # 4. Create Insurance Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "100 Self St", "postalCode": "11111", "city": "SelfCity"},
            "billingAddress": {"streetAddress": "100 Self St", "postalCode": "11111", "city": "SelfCity"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    # Follow-up GET
    resp_quote_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp_quote_get.status_code == 200, f"Expected 200, got {resp_quote_get.status_code}: {resp_quote_get.text}"
    assert resp_quote_get.json()["id"] == quote_id

# --- id=1216  name='Policy Management Create Update' ---
def test_policy_management_create_update_delete():
    # Create a customer in core first
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "BuilderCity",
        "email": "bob@example.com",
        "phoneNumber": "555-0000"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200
    customer_id = resp_cust.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Policy
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Liability"}]}
    }
    resp_policy = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_policy.status_code == 200, f"Expected 200, got {resp_policy.status_code}: {resp_policy.text}"
    policy_id = resp_policy.json()["policyId"]

    # Follow-up GET
    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["policyType"] == "Auto"

    # 2. Update Policy
    policy_payload["policyType"] = "Home"
    resp_put = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    # Follow-up GET
    resp_get2 = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["policyType"] == "Home"

    # 3. Delete Policy
    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

# --- id=1217  name='Policy Management Create Invalid Customer' ---
def test_policy_management_create_invalid_customer():
    # Negative Test: Policy creation for non-existent customer fails with 424
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": "non-existent-customer-id",
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Liability"}]}
    }
    resp_policy = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_policy.status_code == 424, f"Expected 424, got {resp_policy.status_code}: {resp_policy.text}"

# --- id=1218  name='End To End Quote Workflow' ---
def test_end_to_end_quote_workflow():
    # 1. Signup & Login
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_auth.json()["token"]
    self_headers = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Cinema St",
        "postalCode": "90210",
        "city": "Hollywood",
        "phoneNumber": "555-8888"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=self_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    # 3. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Cinema St", "postalCode": "90210", "city": "Hollywood"},
            "billingAddress": {"streetAddress": "123 Cinema St", "postalCode": "90210", "city": "Hollywood"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=self_headers, timeout=10)
    quote_id = resp_quote.json()["id"]

    # 4. Poll policy-management-backend until 200 (asynchronous propagation)
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    max_retries = 10
    found = False
    for _ in range(max_retries):
        resp_poll = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=policy_headers, timeout=10)
        if resp_poll.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    # 5. Policy management drafts quote
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_draft = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=policy_headers, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    # Follow-up GET on policy-management-backend
    resp_draft_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=policy_headers, timeout=10)
    assert resp_draft_get.status_code == 200, f"Expected 200, got {resp_draft_get.status_code}: {resp_draft_get.text}"

    # 6. Poll self-service until QUOTE_RECEIVED (asynchronous propagation)
    status_received = False
    for _ in range(max_retries):
        resp_self_poll = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=self_headers, timeout=10)
        if resp_self_poll.status_code == 200:
            history = resp_self_poll.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                status_received = True
                break
        time.sleep(1)
    assert status_received, "Drafted quote did not propagate back to self-service-backend"

    # 7. Accept Quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=self_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    # Follow-up GET
    resp_accept_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=self_headers, timeout=10)
    assert resp_accept_get.status_code == 200, f"Expected 200, got {resp_accept_get.status_code}: {resp_accept_get.text}"

# --- id=1219  name='Self Accept Quote Too Early' ---
def test_self_service_accept_quote_too_early():
    # Negative Test: Accepting quote before it's drafted fails with 401
    email = f"early_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_auth.json()["token"]
    self_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Early",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Fast St",
        "postalCode": "90210",
        "city": "Speedville",
        "phoneNumber": "555-7777"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=self_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Early",
            "contactAddress": {"streetAddress": "123 Fast St", "postalCode": "90210", "city": "Speedville"},
            "billingAddress": {"streetAddress": "123 Fast St", "postalCode": "90210", "city": "Speedville"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=self_headers, timeout=10)
    quote_id = resp_quote.json()["id"]

    # Try to accept immediately while in REQUEST_SUBMITTED state -> 401
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=self_headers, timeout=10)
    assert resp_accept.status_code == 401, f"Expected 401, got {resp_accept.status_code}: {resp_accept.text}"

# --- id=1220  name='Customer Management Interaction Logs Negative' ---
def test_customer_management_interaction_logs_negative():
    # 1. Create a customer in core to have a real customer ID
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Log",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Log St",
        "postalCode": "12345",
        "city": "Logville",
        "email": "eve@example.com",
        "phoneNumber": "555-2222"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200
    customer_id = resp_cust.json()["customerId"]

    # GET interaction log returns 200 (empty log)
    resp_get = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # PATCH with empty lastAcknowledgedInteractionId -> 400
    patch_payload_empty = {"lastAcknowledgedInteractionId": ""}
    resp_patch_empty = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_empty, timeout=10)
    assert resp_patch_empty.status_code == 400, f"Expected 400, got {resp_patch_empty.status_code}: {resp_patch_empty.text}"

    # PATCH with non-empty lastAcknowledgedInteractionId -> 404 (no log exists yet)
    patch_payload_404 = {"lastAcknowledgedInteractionId": "some-id"}
    resp_patch_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_404, timeout=10)
    assert resp_patch_404.status_code == 404, f"Expected 404, got {resp_patch_404.status_code}: {resp_patch_404.text}"
