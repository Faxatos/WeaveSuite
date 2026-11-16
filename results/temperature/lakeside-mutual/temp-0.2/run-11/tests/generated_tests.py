# Tests generated in iteration 11
# Captured: 2026-07-07T09:05:17
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=447  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    login_payload = {"email": email, "password": password}
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["email"] == email

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Constructville",
        "streetAddress": "1 Build St",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    resp_get_cust = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=ss_headers, timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"
    assert resp_get_cust.json()["customerId"] == customer_id

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "1 Build St", "postalCode": "12345", "city": "Constructville"},
            "billingAddress": {"streetAddress": "1 Build St", "postalCode": "12345", "city": "Constructville"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    accept_payload = {"status": "QUOTE_ACCEPTED"}
    resp_bad_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_bad_accept.status_code == 401, f"Expected 401, got {resp_bad_accept.status_code}: {resp_bad_accept.text}"

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
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
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
    assert received, "Quote draft did not propagate back to customer-self-service-backend"

    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_final = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    assert resp_final.status_code == 200, f"Expected 200, got {resp_final.status_code}: {resp_final.text}"
    final_history = resp_final.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in final_history)

# --- id=448  name='Customer Management Interaction Log Not Found' ---
def test_customer_management_interaction_log_not_found():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "streetAddress": "789 Oak St",
        "postalCode": "67890",
        "city": "Snoopyville",
        "email": f"charlie.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    ack_payload = {"lastAcknowledgedInteractionId": "123"}
    resp_ack = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload, timeout=10)
    assert resp_ack.status_code == 404, f"Expected 404, got {resp_ack.status_code}: {resp_ack.text}"

# --- id=449  name='Policy Management Quote Request Not Found' ---
def test_policy_management_quote_request_not_found():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    resp = requests.get(get_url("policy-management-backend", "/insurance-quote-requests/999999999"), headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=444  name='Customer Core Create Update Customer' ---
def test_customer_core_create_update_customer():
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

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customers"][0]["firstname"] == "John"

    payload["firstname"] = "Johnny"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Johnny"

# --- id=445  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=446  name='Policy Management Create Policy And Dependency Error' ---
def test_policy_management_create_policy_and_dependency_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "456 Elm St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]

    resp_get_pol = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert resp_get_pol.status_code == 200, f"Expected 200, got {resp_get_pol.status_code}: {resp_get_pol.text}"
    assert resp_get_pol.json()["customer"] == customer_id

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

    bad_policy_payload = policy_payload.copy()
    bad_policy_payload["customerId"] = "non-existent-id-12345"
    resp_bad = requests.post(get_url("policy-management-backend", "/policies"), json=bad_policy_payload, headers=headers, timeout=10)
    assert resp_bad.status_code == 424, f"Expected 424, got {resp_bad.status_code}: {resp_bad.text}"
