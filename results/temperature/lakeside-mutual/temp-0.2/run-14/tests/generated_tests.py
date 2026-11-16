# Tests generated in iteration 14
# Captured: 2026-07-07T10:35:20
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=467  name='Customer Core And Policy Management Workflow' ---
def test_customer_core_and_policy_management_workflow():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create Customer in Customer-Core
    cc_payload = {
        "firstname": "Alice", "lastname": "Smith", "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Oak St", "postalCode": "67890", "city": "Othertown",
        "email": f"alice.{uuid.uuid4()}@example.com", "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cc_data = resp.json()
    customer_id = cc_data["customerId"]

    # Verify Customer creation
    customer_url = get_resource_url("customer-core", f"/customers/{customer_id}", cc_data)
    resp_get = requests.get(customer_url, headers=cc_headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert len(get_data["customers"]) > 0
    assert get_data["customers"][0]["customerId"] == customer_id
    assert get_data["customers"][0]["firstname"] == "Alice"

    # 2. Create Policy in Policy-Management
    policy_payload = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    pol_data = resp_pol.json()
    policy_id = pol_data["policyId"]

    # Verify Policy creation
    policy_url = get_resource_url("policy-management-backend", f"/policies/{policy_id}", pol_data)
    resp_pol_get = requests.get(policy_url, headers=pm_headers, timeout=10)
    assert resp_pol_get.status_code == 200, f"Expected 200, got {resp_pol_get.status_code}: {resp_pol_get.text}"
    pol_get_data = resp_pol_get.json()
    assert pol_get_data["policyId"] == policy_id
    assert pol_get_data["customer"] == customer_id
    assert pol_get_data["policyType"] == "HOME"

    # 3. Update Policy
    policy_payload["policyType"] = "AUTO"
    resp_pol_upd = requests.put(policy_url, json=policy_payload, headers=pm_headers, timeout=10)
    assert resp_pol_upd.status_code == 200, f"Expected 200, got {resp_pol_upd.status_code}: {resp_pol_upd.text}"

    # Verify Policy update
    resp_pol_get2 = requests.get(policy_url, headers=pm_headers, timeout=10)
    assert resp_pol_get2.status_code == 200, f"Expected 200, got {resp_pol_get2.status_code}: {resp_pol_get2.text}"
    assert resp_pol_get2.json()["policyType"] == "AUTO"

    # 4. Delete Policy
    resp_pol_del = requests.delete(policy_url, headers=pm_headers, timeout=10)
    assert resp_pol_del.status_code == 204, f"Expected 204, got {resp_pol_del.status_code}: {resp_pol_del.text}"

# --- id=468  name='Self Quote Request Lifecycle' ---
def test_self_service_quote_request_lifecycle():
    ss_base = "customer-self-service-backend"
    pm_base = "policy-management-backend"
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Signup & Login
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    resp_signup = requests.post(get_url(ss_base, "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    resp_login = requests.post(get_url(ss_base, "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_payload = {
        "firstname": "John", "lastname": "Doe", "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown",
        "phoneNumber": "555-1234"
    }
    resp_reg = requests.post(get_url(ss_base, "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    # Verify Customer
    customer_url = get_resource_url(ss_base, f"/customers/{customer_id}", resp_reg.json())
    resp_reg_get = requests.get(customer_url, headers=ss_headers, timeout=10)
    assert resp_reg_get.status_code == 200, f"Expected 200, got {resp_reg_get.status_code}: {resp_reg_get.text}"
    assert resp_reg_get.json()["customerId"] == customer_id

    # 3. Create Quote Request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John", "lastname": "Doe",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url(ss_base, "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    # Verify Quote Request in Self-Service
    ss_quote_url = get_resource_url(ss_base, f"/insurance-quote-requests/{quote_id}", resp_quote.json())
    resp_quote_get = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp_quote_get.status_code == 200, f"Expected 200, got {resp_quote_get.status_code}: {resp_quote_get.text}"
    assert resp_quote_get.json()["id"] == quote_id

    # 4. Poll Policy-Management until quote request appears
    pm_quote_url = get_url(pm_base, f"/insurance-quote-requests/{quote_id}")
    found = False
    for _ in range(15):
        resp_pm_get = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp_pm_get.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to Policy-Management"

    # 5. Draft Quote in Policy-Management
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_draft = requests.patch(pm_quote_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    # Verify Draft in Policy-Management
    resp_pm_get2 = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
    assert resp_pm_get2.status_code == 200, f"Expected 200, got {resp_pm_get2.status_code}: {resp_pm_get2.text}"
    pm_history = [s["status"] for s in resp_pm_get2.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in pm_history

    # 6. Poll Self-Service until QUOTE_RECEIVED appears
    received = False
    for _ in range(15):
        resp_ss_get = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        assert resp_ss_get.status_code == 200, f"Expected 200, got {resp_ss_get.status_code}: {resp_ss_get.text}"
        ss_history = [s["status"] for s in resp_ss_get.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in ss_history:
            received = True
            break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to Self-Service"

    # 7. Accept Quote in Self-Service
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_accept = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    # Verify Final State
    resp_final = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp_final.status_code == 200, f"Expected 200, got {resp_final.status_code}: {resp_final.text}"
    final_history = [s["status"] for s in resp_final.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_history

# --- id=469  name='Negative Policy Creation Missing Customer' ---
def test_negative_policy_creation_missing_customer():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_customer_id = str(uuid.uuid4())

    policy_payload = {
        "customerId": fake_customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=470  name='Negative Quote Accept Invalid State' ---
def test_negative_quote_accept_invalid_state():
    ss_base = "customer-self-service-backend"

    # Signup & Login
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url(ss_base, "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url(ss_base, "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # Register Customer
    reg_payload = {
        "firstname": "John", "lastname": "Doe", "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown",
        "phoneNumber": "555-1234"
    }
    resp_reg = requests.post(get_url(ss_base, "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = resp_reg.json()["customerId"]

    # Create Quote Request
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John", "lastname": "Doe",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url(ss_base, "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10)
    quote_id = resp_quote.json()["id"]

    # Immediately try to accept it (invalid state transition, should be 401 as per spec)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    ss_quote_url = get_resource_url(ss_base, f"/insurance-quote-requests/{quote_id}", resp_quote.json())
    resp_accept = requests.patch(ss_quote_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 401, f"Expected 401, got {resp_accept.status_code}: {resp_accept.text}"

# --- id=471  name='Negative Customer Core Missing Phone' ---
def test_negative_customer_core_missing_phone():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Bob", "lastname": "Builder", "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "789 Pine St", "postalCode": "11223", "city": "Sometown",
        "email": f"bob.{uuid.uuid4()}@example.com"
        # phoneNumber is missing
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=472  name='Negative Interaction Log Not Found' ---
def test_negative_interaction_log_not_found():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create Customer in Customer-Core
    cc_payload = {
        "firstname": "Charlie", "lastname": "Chaplin", "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Cinema Rd", "postalCode": "90210", "city": "Hollywood",
        "email": f"charlie.{uuid.uuid4()}@example.com", "phoneNumber": "555-0000"
    }
    resp_cc = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert resp_cc.status_code == 200, f"Expected 200, got {resp_cc.status_code}: {resp_cc.text}"
    customer_id = resp_cc.json()["customerId"]

    # Attempt to acknowledge interactions in Customer-Management for a customer with no log
    ack_payload = {"lastAcknowledgedInteractionId": "12345"}
    resp_ack = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload, timeout=10)
    assert resp_ack.status_code == 404, f"Expected 404, got {resp_ack.status_code}: {resp_ack.text}"
