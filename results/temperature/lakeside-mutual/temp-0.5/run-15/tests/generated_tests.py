# Tests generated in iteration 15
# Captured: 2026-07-09T03:45:28
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1024  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    auth = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=auth, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customers"][0]["customerId"] == customer_id
    assert resp_get.json()["customers"][0]["firstname"] == "John"

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=auth, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get_updated = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=auth, timeout=10)
    assert resp_get_updated.status_code == 200, f"Expected 200, got {resp_get_updated.status_code}: {resp_get_updated.text}"
    assert resp_get_updated.json()["customers"][0]["firstname"] == "Johnny"

    bad_payload = payload.copy()
    del bad_payload["phoneNumber"]
    resp_bad = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=auth, timeout=10)
    assert resp_bad.status_code == 500, f"Expected 500, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=1025  name='Customer Self Backend Auth And Registration' ---
def test_customer_self_service_backend_auth_and_registration():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()

    login_payload = {"email": email, "password": password}
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    auth = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=auth, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=auth, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["customerId"] == customer_id

# --- id=1026  name='Policy Management Backend Create Policy' ---
def test_policy_management_backend_create_policy():
    core_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "streetAddress": "789 Construction Way",
        "postalCode": "98765",
        "city": "Buildville",
        "email": f"bob_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=core_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    policy_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_auth, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_auth, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["policyId"] == policy_id
    assert resp_get.json()["customer"] == customer_id

    bad_policy_payload = policy_payload.copy()
    bad_policy_payload["customerId"] = "non-existent-id-123"
    resp_bad = requests.post(get_url("policy-management-backend", "/policies"), json=bad_policy_payload, headers=policy_auth, timeout=10)
    assert resp_bad.status_code == 424, f"Expected 424, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=1027  name='Customer Management Backend Interaction Logs Errors' ---
def test_customer_management_backend_interaction_logs_errors():
    core_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "streetAddress": "1 Hollywood Blvd",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": f"charlie_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=core_auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    patch_payload_empty = {"lastAcknowledgedInteractionId": ""}
    resp_empty = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_empty, timeout=10)
    assert resp_empty.status_code == 400, f"Expected 400, got {resp_empty.status_code}: {resp_empty.text}"

    patch_payload_valid = {"lastAcknowledgedInteractionId": "interaction-123"}
    resp_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_valid, timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=1028  name='Customer Self Backend Quote Request Workflow' ---
def test_customer_self_service_backend_quote_request_workflow():
    email = f"quote_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    ss_auth = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "city": "Seattle",
        "streetAddress": "123 Grunge St",
        "postalCode": "98101",
        "phoneNumber": "555-3333"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_auth, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Grohl",
            "contactAddress": {"streetAddress": "123 Grunge St", "postalCode": "98101", "city": "Seattle"},
            "billingAddress": {"streetAddress": "123 Grunge St", "postalCode": "98101", "city": "Seattle"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_auth, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    resp_bad_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json={"status": "QUOTE_ACCEPTED"}, headers=ss_auth, timeout=10)
    assert resp_bad_accept.status_code == 401, f"Expected 401, got {resp_bad_accept.status_code}: {resp_bad_accept.text}"

    pm_auth = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")
    found = False
    for _ in range(15):
        resp_pm_get = requests.get(pm_url, headers=pm_auth, timeout=10)
        if resp_pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy management"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_draft = requests.patch(pm_url, json=draft_payload, headers=pm_auth, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(15):
        resp_ss_get = requests.get(ss_url, headers=ss_auth, timeout=10)
        if resp_ss_get.status_code == 200:
            history = [s.get("status") for s in resp_ss_get.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate back to self-service"

    resp_accept = requests.patch(ss_url, json={"status": "QUOTE_ACCEPTED"}, headers=ss_auth, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"
    assert resp_accept.json()["insuranceQuote"]["insurancePremium"]["amount"] == 150
