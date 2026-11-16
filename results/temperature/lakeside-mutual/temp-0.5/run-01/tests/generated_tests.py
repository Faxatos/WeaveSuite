# Tests generated in iteration 01
# Captured: 2026-07-08T20:30:38
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=917  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"john.doe_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    cust_id = customer["customerId"]

    resp_get = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert len(data["customers"]) == 1
    fetched = data["customers"][0]
    assert fetched["firstname"] == "John"

    payload["firstname"] = "Johnny"
    resp_put = requests.put(get_url("customer-core", f"/customers/{cust_id}"), json=payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Johnny"

# --- id=918  name='Customer Core Create Missing Phone Error' ---
def test_customer_core_create_missing_phone_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"john.doe_{uuid.uuid4().hex[:8]}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=919  name='Customer Management Acknowledge Interactions Errors' ---
def test_customer_management_acknowledge_interactions_errors():
    cust_id = f"test-id-{uuid.uuid4().hex[:8]}"

    payload_400 = {"lastAcknowledgedInteractionId": ""}
    resp_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{cust_id}"), json=payload_400, timeout=10)
    assert resp_400.status_code == 400, f"Expected 400, got {resp_400.status_code}: {resp_400.text}"

    payload_404 = {"lastAcknowledgedInteractionId": "interaction-1"}
    resp_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{cust_id}"), json=payload_404, timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=920  name='Self Signup And Registration' ---
def test_self_service_signup_and_registration():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert resp_signup.json()["email"] == email
    assert "customerId" not in resp_signup.json()

    auth_payload = {"email": email, "password": password}
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json()["token"]
    headers = {"X-Auth-Token": token}

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert "customerId" not in resp_user.json()

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
    cust_id = resp_reg.json()["customerId"]

    resp_user2 = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user2.status_code == 200, f"Expected 200, got {resp_user2.status_code}: {resp_user2.text}"
    assert resp_user2.json()["customerId"] == cust_id

# --- id=921  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildville",
        "email": f"bob_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1111"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers_core, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    cust_id = resp_cust.json()["customerId"]

    policy_payload = {
        "customerId": cust_id,
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
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers_policy, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]

    resp_get_pol = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_policy, timeout=10)
    assert resp_get_pol.status_code == 200, f"Expected 200, got {resp_get_pol.status_code}: {resp_get_pol.text}"
    assert resp_get_pol.json()["policyType"] == "Life"
    assert resp_get_pol.json()["customer"] == cust_id

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_policy, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

    resp_list = requests.get(get_url("policy-management-backend", "/policies"), headers=headers_policy, timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    policies = resp_list.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=922  name='Insurance Quote Workflow And Illegal Transition' ---
def test_insurance_quote_workflow_and_illegal_transition():
    email = f"quote_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_auth.json()["token"]
    headers_self = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "1 Comedy Way",
        "postalCode": "12345",
        "phoneNumber": "555-2222"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_self, timeout=10)
    cust_id = resp_reg.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": cust_id,
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
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_self, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    resp_get_quote = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_self, timeout=10)
    assert resp_get_quote.status_code == 200, f"Expected 200, got {resp_get_quote.status_code}: {resp_get_quote.text}"

    illegal_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_illegal = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=illegal_payload, headers=headers_self, timeout=10)
    assert resp_illegal.status_code == 401, f"Expected 401, got {resp_illegal.status_code}: {resp_illegal.text}"

    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        resp_poll = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_policy, timeout=10)
        if resp_poll.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management-backend")

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_draft = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=headers_policy, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    resp_get_draft = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_policy, timeout=10)
    assert resp_get_draft.status_code == 200, f"Expected 200, got {resp_get_draft.status_code}: {resp_get_draft.text}"

    for _ in range(15):
        resp_poll_self = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_self, timeout=10)
        if resp_poll_self.status_code == 200:
            history = [s.get("status") for s in resp_poll_self.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                break
        time.sleep(1)
    else:
        pytest.fail("QUOTE_RECEIVED status did not propagate to customer-self-service-backend")

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=headers_self, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_final = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_self, timeout=10)
    assert resp_final.status_code == 200, f"Expected 200, got {resp_final.status_code}: {resp_final.text}"
    history = [s.get("status") for s in resp_final.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

# --- id=923  name='Policy Management Create Policy Missing Customer Error' ---
def test_policy_management_create_policy_missing_customer_error():
    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}

    policy_payload = {
        "customerId": f"non-existent-{uuid.uuid4().hex[:8]}",
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
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers_policy, timeout=10)
    assert resp_pol.status_code == 424, f"Expected 424, got {resp_pol.status_code}: {resp_pol.text}"

# --- id=924  name='Customer Core Update Address' ---
def test_customer_core_update_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Eve",
        "lastname": "Hacker",
        "streetAddress": "123 Old St",
        "postalCode": "11111",
        "city": "Oldville",
        "email": f"eve_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_id = resp.json()["customerId"]

    address_payload = {
        "streetAddress": "456 New St",
        "postalCode": "22222",
        "city": "Newville"
    }
    resp_addr = requests.put(get_url("customer-core", f"/customers/{cust_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    resp_get = requests.get(get_url("customer-core", f"/customers/{cust_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()["customers"][0]
    assert customer["streetAddress"] == "456 New St"
    assert customer["postalCode"] == "22222"
    assert customer["city"] == "Newville"

# --- id=925  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
