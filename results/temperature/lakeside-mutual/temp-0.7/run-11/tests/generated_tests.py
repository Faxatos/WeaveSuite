# Tests generated in iteration 11
# Captured: 2026-07-09T23:46:44
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1280  name='Customer Core Crud Customer' ---
def test_customer_core_crud_customer():
    session = requests.Session()
    headers_cc = {"Authorization": "Bearer b318ad736c6c844b"}

    # Negative: Missing phone number -> 500
    bad_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"john.doe.{uuid.uuid4()}@example.com"
    }
    r_bad = session.post(get_url("customer-core", "/customers"), json=bad_payload, headers=headers_cc, timeout=10)
    assert r_bad.status_code == 500, f"Expected 500, got {r_bad.status_code}: {r_bad.text}"

    # Valid create
    payload = bad_payload.copy()
    payload["phoneNumber"] = "555-1234"
    r_create = session.post(get_url("customer-core", "/customers"), json=payload, headers=headers_cc, timeout=10)
    assert r_create.status_code == 200, f"Expected 200, got {r_create.status_code}: {r_create.text}"
    customer_id = r_create.json()["customerId"]

    # Get via /customers/{ids}
    r_get = session.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers_cc, timeout=10)
    assert r_get.status_code == 200, f"Expected 200, got {r_get.status_code}: {r_get.text}"
    cust = r_get.json()["customers"][0]
    assert cust["firstname"] == "John"

    # Update
    payload["firstname"] = "Johnny"
    r_update = session.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=headers_cc, timeout=10)
    assert r_update.status_code == 200, f"Expected 200, got {r_update.status_code}: {r_update.text}"

    # Get again and verify update
    r_get2 = session.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers_cc, timeout=10)
    assert r_get2.status_code == 200, f"Expected 200, got {r_get2.status_code}: {r_get2.text}"
    assert r_get2.json()["customers"][0]["firstname"] == "Johnny"

# --- id=1281  name='Customer Self Auth And Registration' ---
def test_customer_self_service_auth_and_registration():
    session = requests.Session()
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup
    signup_resp = session.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert "customerId" not in signup_resp.json()

    # Auth
    auth_resp = session.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # GET user (no customerId)
    r_user = session.get(get_url("customer-self-service-backend", "/user"), headers=headers_ss, timeout=10)
    assert r_user.status_code == 200, f"Expected 200, got {r_user.status_code}: {r_user.text}"
    assert "customerId" not in r_user.json()

    # Register customer
    reg_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Testville",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    reg_resp = session.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # GET user (customerId present)
    r_user2 = session.get(get_url("customer-self-service-backend", "/user"), headers=headers_ss, timeout=10)
    assert r_user2.status_code == 200, f"Expected 200, got {r_user2.status_code}: {r_user2.text}"
    assert r_user2.json()["customerId"] == customer_id

# --- id=1282  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    session = requests.Session()
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer first in customer-core
    cust_payload = {
        "firstname": "Alice",
        "lastname": "Wonder",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    r_cust = session.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert r_cust.status_code == 200, f"Expected 200, got {r_cust.status_code}: {r_cust.text}"
    customer_id = r_cust.json()["customerId"]

    # Create policy
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    r_pol = session.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=headers, timeout=10)
    assert r_pol.status_code == 200, f"Expected 200, got {r_pol.status_code}: {r_pol.text}"
    policy_id = r_pol.json()["policyId"]

    # Get policy
    r_get = session.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert r_get.status_code == 200, f"Expected 200, got {r_get.status_code}: {r_get.text}"
    assert r_get.json()["customer"] == customer_id

    # Delete policy
    r_del = session.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert r_del.status_code == 204, f"Expected 204, got {r_del.status_code}: {r_del.text}"

# --- id=1283  name='Quote Request Workflow' ---
def test_quote_request_workflow():
    session = requests.Session()
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Signup & Auth
    session.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = session.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # Register customer
    reg_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Testville",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    reg_resp = session.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    # Create quote request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Testville"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Testville"}
        },
        "insuranceOptions": {
            "startDate": "2030-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    quote_resp = session.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_ss, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    # Self-service: Try to accept quote while still REQUEST_SUBMITTED -> 401
    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    ss_patch_early = session.patch(ss_url, json={"status": "QUOTE_ACCEPTED"}, headers=headers_ss, timeout=10)
    assert ss_patch_early.status_code == 401, f"Expected 401, got {ss_patch_early.status_code}: {ss_patch_early.text}"

    # Policy-management: Poll GET
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    success = False
    for _ in range(15):
        r = session.get(pm_url, headers=headers_pm, timeout=10)
        if r.status_code == 200:
            success = True
            break
        elif r.status_code == 404:
            pass # Expected while waiting
        else:
            assert False, f"Unexpected status {r.status_code}: {r.text}"
        time.sleep(1)
    assert success, "Quote request did not propagate to policy-management-backend"

    # Policy-management: Draft quote
    pm_patch_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    pm_patch_resp = session.patch(pm_url, json=pm_patch_payload, headers=headers_pm, timeout=10)
    assert pm_patch_resp.status_code == 200, f"Expected 200, got {pm_patch_resp.status_code}: {pm_patch_resp.text}"

    # Self-service: Poll GET until QUOTE_RECEIVED
    success = False
    for _ in range(15):
        r = session.get(ss_url, headers=headers_ss, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        statuses = [s.get("status") for s in r.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            success = True
            break
        time.sleep(1)
    assert success, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    # Self-service: Send unrecognised status -> 200 (ignored)
    ss_patch_unrec = session.patch(ss_url, json={"status": "INVALID_STATUS"}, headers=headers_ss, timeout=10)
    assert ss_patch_unrec.status_code == 200, f"Expected 200, got {ss_patch_unrec.status_code}: {ss_patch_unrec.text}"

    # Self-service: Accept quote
    ss_patch_resp = session.patch(ss_url, json={"status": "QUOTE_ACCEPTED"}, headers=headers_ss, timeout=10)
    assert ss_patch_resp.status_code == 200, f"Expected 200, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

    # Verify final state
    r_final = session.get(ss_url, headers=headers_ss, timeout=10)
    assert r_final.status_code == 200
    statuses = [s.get("status") for s in r_final.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=1284  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    session = requests.Session()
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    pol_payload = {
        "customerId": f"nonexistent-{uuid.uuid4()}",
        "policyType": "Life",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    r_pol = session.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=headers, timeout=10)
    assert r_pol.status_code == 424, f"Expected 424, got {r_pol.status_code}: {r_pol.text}"

# --- id=1285  name='Customer Management Interaction Logs Negative' ---
def test_customer_management_interaction_logs_negative():
    session = requests.Session()
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer in customer-core
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"bob.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    r_cust = session.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert r_cust.status_code == 200, f"Expected 200, got {r_cust.status_code}: {r_cust.text}"
    customer_id = r_cust.json()["customerId"]

    # PATCH with empty lastAcknowledgedInteractionId -> 400
    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    r_patch_400 = session.patch(patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert r_patch_400.status_code == 400, f"Expected 400, got {r_patch_400.status_code}: {r_patch_400.text}"

    # PATCH with valid lastAcknowledgedInteractionId but no log -> 404
    r_patch_404 = session.patch(patch_url, json={"lastAcknowledgedInteractionId": "interaction-123"}, timeout=10)
    assert r_patch_404.status_code == 404, f"Expected 404, got {r_patch_404.status_code}: {r_patch_404.text}"
