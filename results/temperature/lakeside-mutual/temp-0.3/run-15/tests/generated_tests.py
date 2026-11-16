# Tests generated in iteration 15
# Captured: 2026-07-08T01:36:54
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=691  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
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
    get_data = resp_get.json()
    assert get_data["customers"][0]["customerId"] == customer_id
    assert get_data["customers"][0]["firstname"] == "John"

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Johnny"

    bad_payload = payload.copy()
    del bad_payload["phoneNumber"]
    resp_bad = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=headers, timeout=10)
    assert resp_bad.status_code == 500, f"Expected 500, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=692  name='Customer Self Signup And Register' ---
def test_customer_self_service_signup_and_register():
    email = f"user.{uuid.uuid4()}@example.com"
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
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "98765",
        "phoneNumber": "555-9876"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["customerId"] == customer_id

    resp_cust = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    assert resp_cust.json()["customerId"] == customer_id

# --- id=693  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "789 Construction Way",
        "postalCode": "11111",
        "city": "Buildtown",
        "email": f"bob.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=policy_headers, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["policyId"] == policy_id
    assert resp_get.json()["customer"] == customer_id

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

# --- id=694  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    pol_payload = {
        "customerId": f"non-existent-{uuid.uuid4()}",
        "policyType": "Life",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=policy_headers, timeout=10)
    assert resp_pol.status_code == 424, f"Expected 424, got {resp_pol.status_code}: {resp_pol.text}"

# --- id=695  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"quote.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "00000",
        "phoneNumber": "555-0000"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "1 Cinema Rd", "postalCode": "00000", "city": "London"},
            "billingAddress": {"streetAddress": "1 Cinema Rd", "postalCode": "00000", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        resp_pm_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}"), headers=pm_headers, timeout=10)
        if resp_pm_get.status_code == 200:
            break
        time.sleep(1)
    assert resp_pm_get.status_code == 200, "Quote request did not propagate to policy-management"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_pm_patch = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp_pm_patch.status_code == 200, f"Expected 200, got {resp_pm_patch.status_code}: {resp_pm_patch.text}"

    for _ in range(15):
        resp_ss_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
        if resp_ss_get.status_code == 200:
            history = [s["status"] for s in resp_ss_get.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in history, "Status QUOTE_RECEIVED did not propagate to self-service"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_ss_patch = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_ss_patch.status_code == 200, f"Expected 200, got {resp_ss_patch.status_code}: {resp_ss_patch.text}"

    resp_ss_final = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    final_history = [s["status"] for s in resp_ss_final.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_history

# --- id=696  name='Insurance Quote Request Illegal Transition' ---
def test_insurance_quote_request_illegal_transition():
    email = f"illegal.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Defiant",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Rebel City",
        "streetAddress": "99 Rulebreaker Ave",
        "postalCode": "12345",
        "phoneNumber": "555-9999"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Defiant",
            "contactAddress": {"streetAddress": "99 Rulebreaker Ave", "postalCode": "12345", "city": "Rebel City"},
            "billingAddress": {"streetAddress": "99 Rulebreaker Ave", "postalCode": "12345", "city": "Rebel City"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    qr_id = resp_qr.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_ss_patch = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_ss_patch.status_code == 401, f"Expected 401, got {resp_ss_patch.status_code}: {resp_ss_patch.text}"

# --- id=697  name='Customer Management Interaction Logs Negative' ---
def test_customer_management_interaction_logs_negative():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Eve",
        "lastname": "Eavesdropper",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "101 Secret St",
        "postalCode": "54321",
        "city": "Spytown",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1010"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    bad_payload = {"lastAcknowledgedInteractionId": ""}
    resp_patch_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=bad_payload, timeout=10)
    assert resp_patch_400.status_code == 400, f"Expected 400, got {resp_patch_400.status_code}: {resp_patch_400.text}"

    not_found_payload = {"lastAcknowledgedInteractionId": "interaction-123"}
    resp_patch_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=not_found_payload, timeout=10)
    assert resp_patch_404.status_code == 404, f"Expected 404, got {resp_patch_404.status_code}: {resp_patch_404.text}"
