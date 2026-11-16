# Tests generated in iteration 03
# Captured: 2026-07-07T05:17:31
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=392  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
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
    customer = resp.json()
    customer_id = customer["customerId"]

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data["customers"][0]["firstname"] == "John"
    assert data["customers"][0]["email"] == payload["email"]

    update_payload = payload.copy()
    update_payload["firstname"] = "Jane"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Jane"

# --- id=393  name='Customer Core Create Missing Phone Number Returns 500' ---
def test_customer_core_create_missing_phone_number_returns_500():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=394  name='Customer Self Signup And Register Customer' ---
def test_customer_self_service_signup_and_register_customer():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    login_payload = {"email": email, "password": password}
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["customerId"] == customer_id

# --- id=395  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "streetAddress": "1 Build St",
        "postalCode": "12345",
        "city": "BuilderTown",
        "email": f"bob.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    resp_cust_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp_cust_get.status_code == 200, f"Expected 200, got {resp_cust_get.status_code}: {resp_cust_get.text}"

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
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
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["policyType"] == "Life"
    assert resp_get.json()["customer"] == customer_id

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

    resp_list = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    policies = resp_list.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies)

# --- id=396  name='Policy Management Create Policy Invalid Customer Returns 424' ---
def test_policy_management_create_policy_invalid_customer_returns_424():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
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
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert resp_pol.status_code == 424, f"Expected 424, got {resp_pol.status_code}: {resp_pol.text}"

# --- id=397  name='Insurance Quote Workflow End To End' ---
def test_insurance_quote_workflow_end_to_end():
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "1 Comedy Way",
        "postalCode": "12345",
        "phoneNumber": "555-2222"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "1 Comedy Way", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "1 Comedy Way", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    resp_qr_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    assert resp_qr_get.status_code == 200, f"Expected 200, got {resp_qr_get.status_code}: {resp_qr_get.text}"

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    max_retries = 10
    found = False
    for _ in range(max_retries):
        resp_pm_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}"), headers=pm_headers, timeout=10)
        if resp_pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_draft = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    received = False
    for _ in range(max_retries):
        resp_ss_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
        if resp_ss_get.status_code == 200:
            history = resp_ss_get.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_final = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    assert resp_final.status_code == 200
    history = resp_final.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=398  name='Customer Self Accept Quote Invalid State Returns 401' ---
def test_customer_self_service_accept_quote_invalid_state_returns_401():
    email = f"quote_invalid_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Danger",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "DangerZone",
        "streetAddress": "1 Danger Way",
        "postalCode": "12345",
        "phoneNumber": "555-3333"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Danger",
            "contactAddress": {"streetAddress": "1 Danger Way", "postalCode": "12345", "city": "DangerZone"},
            "billingAddress": {"streetAddress": "1 Danger Way", "postalCode": "12345", "city": "DangerZone"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    resp_qr_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    assert resp_qr_get.status_code == 200, f"Expected 200, got {resp_qr_get.status_code}: {resp_qr_get.text}"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 401, f"Expected 401, got {resp_accept.status_code}: {resp_accept.text}"

# --- id=399  name='Customer Management Acknowledge Interactions Non Existent Log Returns 404' ---
def test_customer_management_acknowledge_interactions_non_existent_log_returns_404():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Eavesdropper",
        "streetAddress": "1 Eve St",
        "postalCode": "12345",
        "city": "EveTown",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4444"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    resp_cust_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=core_headers, timeout=10)
    assert resp_cust_get.status_code == 200, f"Expected 200, got {resp_cust_get.status_code}: {resp_cust_get.text}"

    ack_payload = {"lastAcknowledgedInteractionId": "some-id"}
    resp_ack = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload, timeout=10)
    assert resp_ack.status_code == 404, f"Expected 404, got {resp_ack.status_code}: {resp_ack.text}"
