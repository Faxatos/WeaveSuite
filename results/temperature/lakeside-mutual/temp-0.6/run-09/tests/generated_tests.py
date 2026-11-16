# Tests generated in iteration 09
# Captured: 2026-07-09T11:18:49
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1124  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
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
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]

    get_url_1 = get_url("customer-core", f"/customers/{customer_id}")
    resp_get = requests.get(get_url_1, headers=HEADERS_CORE, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customers"][0]["customerId"] == customer_id

    payload["firstname"] = "Johnny"
    put_url = get_url("customer-core", f"/customers/{customer_id}")
    resp_put = requests.put(put_url, json=payload, headers=HEADERS_CORE, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url_1, headers=HEADERS_CORE, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Johnny"

# --- id=1125  name='Customer Core Create Missing Phone Number 500' ---
def test_customer_core_create_missing_phone_number_500():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1126  name='Self Signup Register Change Address' ---
def test_self_service_signup_register_change_address():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp_signup = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    auth_url = get_url("customer-self-service-backend", "/auth")
    resp_auth = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    reg_url = get_url("customer-self-service-backend", "/customers")
    resp_reg = requests.post(reg_url, json=reg_payload, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    addr_payload = {
        "streetAddress": "Queen Castle 2",
        "postalCode": "54321",
        "city": "Wonderland"
    }
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    resp_addr = requests.put(addr_url, json=addr_payload, headers=headers, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    assert resp_addr.json()["streetAddress"] == "Queen Castle 2"

    get_url_1 = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp_get = requests.get(get_url_1, headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customerId"] == customer_id

# --- id=1127  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    url = get_url("policy-management-backend", "/riskfactor/compute")
    resp = requests.post(url, json=payload, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=1128  name='Policy Management Create Policy 424 Failed Dependency' ---
def test_policy_management_create_policy_424_failed_dependency():
    payload = {
        "customerId": "non-existent-customer-id",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    url = get_url("policy-management-backend", "/policies")
    resp = requests.post(url, json=payload, headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1129  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildtown",
        "email": f"bob.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_url = get_url("customer-core", "/customers")
    resp_cust = requests.post(cust_url, json=cust_payload, headers=HEADERS_CORE, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Home",
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 200000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Dwelling"}
            ]
        }
    }
    pol_url = get_url("policy-management-backend", "/policies")
    resp_pol = requests.post(pol_url, json=pol_payload, headers=HEADERS_POLICY, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]

    get_url_1 = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp_get = requests.get(get_url_1, headers=HEADERS_POLICY, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["policyId"] == policy_id
    assert resp_get.json()["customer"] == customer_id

    resp_del = requests.delete(get_url_1, headers=HEADERS_POLICY, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

# --- id=1130  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"quote.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_auth.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "London",
        "streetAddress": "Street 1",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "Street 1", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "Street 1", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_ss, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    pol_get_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")
    found = False
    for _ in range(15):
        resp_pol_get = requests.get(pol_get_url, headers=HEADERS_POLICY, timeout=10)
        if resp_pol_get.status_code == 200:
            found = True
            break
        time.sleep(1)

    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_draft = requests.patch(pol_get_url, json=draft_payload, headers=HEADERS_POLICY, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    ss_get_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(15):
        resp_ss_get = requests.get(ss_get_url, headers=headers_ss, timeout=10)
        if resp_ss_get.status_code == 200:
            status_history = resp_ss_get.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                received = True
                break
        time.sleep(1)

    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_accept = requests.patch(ss_get_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

# --- id=1131  name='Insurance Quote Request Illegal Transition 401' ---
def test_insurance_quote_request_illegal_transition_401():
    email = f"quote2.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_auth.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Dog",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "London",
        "streetAddress": "Street 1",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_ss, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Dog",
            "contactAddress": {"streetAddress": "Street 1", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "Street 1", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_ss, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    ss_patch_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    resp_accept = requests.patch(ss_patch_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp_accept.status_code == 401, f"Expected 401, got {resp_accept.status_code}: {resp_accept.text}"

# --- id=1132  name='Customer Management Acknowledge Interactions 400' ---
def test_customer_management_acknowledge_interactions_400():
    customer_id = "any-id"
    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1133  name='Customer Management Acknowledge Interactions 404' ---
def test_customer_management_acknowledge_interactions_404():
    cust_payload = {
        "firstname": "Eve",
        "lastname": "Eagle",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Nest St",
        "postalCode": "12345",
        "city": "Tree",
        "email": f"eve.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    cust_url = get_url("customer-core", "/customers")
    resp_cust = requests.post(cust_url, json=cust_payload, headers=HEADERS_CORE, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload = {"lastAcknowledgedInteractionId": "some-id"}
    resp = requests.patch(url, json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
