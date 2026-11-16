# Tests generated in iteration 02
# Captured: 2026-07-07T15:09:28
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=530  name='Customer Self Backend E2e Quote Workflow' ---
def test_customer_self_service_backend_e2e_quote_workflow():
    # 1. Signup
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # 2. Login
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    # 3. Complete registration
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # 4. Verify user details
    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    # 5. Create quote request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    # Follow-up GET on SS
    qr_get_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    assert qr_get_resp.status_code == 200, f"Expected 200, got {qr_get_resp.status_code}: {qr_get_resp.text}"
    assert qr_get_resp.json()["id"] == qr_id

    # 6. Poll policy-management until 200
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    for _ in range(15):
        pm_qr_resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if pm_qr_resp.status_code == 200:
            break
        time.sleep(1)
    assert pm_qr_resp.status_code == 200, f"Expected 200, got {pm_qr_resp.status_code}: {pm_qr_resp.text}"

    # 7. Draft quote response
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    draft_resp = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # Follow-up GET on PM
    pm_qr_get_resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
    assert pm_qr_get_resp.status_code == 200, f"Expected 200, got {pm_qr_get_resp.status_code}: {pm_qr_get_resp.text}"
    pm_statuses = [s["status"] for s in pm_qr_get_resp.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in pm_statuses

    # 8. Poll self-service until QUOTE_RECEIVED
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    for _ in range(15):
        ss_qr_resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        assert ss_qr_resp.status_code == 200, f"Expected 200, got {ss_qr_resp.status_code}: {ss_qr_resp.text}"
        statuses = [s["status"] for s in ss_qr_resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in statuses, "QUOTE_RECEIVED not found in statusHistory"

    # 9. Accept quote
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    accept_resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # 10. Verify final state
    final_resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert final_resp.status_code == 200, f"Expected 200, got {final_resp.status_code}: {final_resp.text}"
    final_statuses = [s["status"] for s in final_resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_statuses

# --- id=531  name='Policy Management Backend Policy Lifecycle' ---
def test_policy_management_backend_policy_lifecycle():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer on customer-core
    cc_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 2",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-9876"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    # Follow-up GET
    cc_get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=cc_headers, timeout=10)
    assert cc_get_resp.status_code == 200, f"Expected 200, got {cc_get_resp.status_code}: {cc_get_resp.text}"
    assert cc_get_resp.json()["customers"][0]["customerId"] == customer_id

    # 3. Create policy
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"},
        "insurancePremium": {"amount": 300, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    # 4. Verify policy
    pol_get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert pol_get_resp.status_code == 200, f"Expected 200, got {pol_get_resp.status_code}: {pol_get_resp.text}"
    assert pol_get_resp.json()["policyId"] == policy_id
    assert pol_get_resp.json()["customer"] == customer_id

    # 5. Update policy
    policy_payload["policyType"] = "Home Premium"
    pol_upd_resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=policy_payload, headers=pm_headers, timeout=10)
    assert pol_upd_resp.status_code == 200, f"Expected 200, got {pol_upd_resp.status_code}: {pol_upd_resp.text}"

    # 6. Verify updated policy
    pol_get_upd_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert pol_get_upd_resp.status_code == 200, f"Expected 200, got {pol_get_upd_resp.status_code}: {pol_get_upd_resp.text}"
    assert pol_get_upd_resp.json()["policyType"] == "Home Premium"

    # 7. Delete policy
    pol_del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert pol_del_resp.status_code == 204, f"Expected 204, got {pol_del_resp.status_code}: {pol_del_resp.text}"

    # 8. Verify deletion
    pol_list_resp = requests.get(get_url("policy-management-backend", "/policies"), headers=pm_headers, timeout=10)
    assert pol_list_resp.status_code == 200, f"Expected 200, got {pol_list_resp.status_code}: {pol_list_resp.text}"
    assert not any(p["policyId"] == policy_id for p in pol_list_resp.json().get("policies", []))

# --- id=532  name='Customer Self Backend Quote Request Illegal State' ---
def test_customer_self_service_backend_quote_request_illegal_state():
    # Signup, login, register
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Builder St 1",
        "postalCode": "3000",
        "phoneNumber": "555-4321"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    # Create quote request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "Builder St 1", "postalCode": "3000", "city": "Bern"},
            "billingAddress": {"streetAddress": "Builder St 1", "postalCode": "3000", "city": "Bern"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    qr_id = qr_resp.json()["id"]

    # Immediately attempt to accept quote (illegal state transition)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    accept_resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=533  name='Customer Core Create Customer Missing Phone' ---
def test_customer_core_create_customer_missing_phone():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Cinema St 1",
        "postalCode": "2000",
        "city": "Neuchatel",
        "email": f"charlie_{uuid.uuid4().hex[:8]}@example.com"
        # phoneNumber is missing
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 500, f"Expected 500, got {cc_resp.status_code}: {cc_resp.text}"

# --- id=534  name='Customer Management Backend Acknowledge Interactions Errors' ---
def test_customer_management_backend_acknowledge_interactions_errors():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer
    cc_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "birthday": "1969-01-14T00:00:00Z",
        "streetAddress": "Rock St 1",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"dave_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-6666"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    # Attempt to acknowledge with empty lastAcknowledgedInteractionId
    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    ack_payload_empty = {"lastAcknowledgedInteractionId": ""}
    ack_resp_empty = requests.patch(cm_url, json=ack_payload_empty, timeout=10)
    assert ack_resp_empty.status_code == 400, f"Expected 400, got {ack_resp_empty.status_code}: {ack_resp_empty.text}"

# --- id=535  name='Policy Management Backend Compute Risk Factor' ---
def test_policy_management_backend_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1980-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=536  name='Customer Core Update Customer' ---
def test_customer_core_update_customer():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer
    cc_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Garden St 1",
        "postalCode": "5000",
        "city": "Aarau",
        "email": f"eve_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-7777"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    # Update customer
    cc_payload["firstname"] = "Eve Updated"
    cc_upd_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_upd_resp.status_code == 200, f"Expected 200, got {cc_upd_resp.status_code}: {cc_upd_resp.text}"

    # Follow-up GET
    cc_get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=cc_headers, timeout=10)
    assert cc_get_resp.status_code == 200, f"Expected 200, got {cc_get_resp.status_code}: {cc_get_resp.text}"
    assert cc_get_resp.json()["customers"][0]["firstname"] == "Eve Updated"

# --- id=537  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # Create customer
    cc_payload = {
        "firstname": "Frank",
        "lastname": "Zappa",
        "birthday": "1940-12-21T00:00:00Z",
        "streetAddress": "Music St 1",
        "postalCode": "6000",
        "city": "Lucerne",
        "email": f"frank_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-8888"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    # Change address
    addr_payload = {
        "streetAddress": "New Music St 2",
        "postalCode": "6001",
        "city": "Lucerne"
    }
    addr_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=addr_payload, headers=cc_headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    # Follow-up GET
    cc_get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=cc_headers, timeout=10)
    assert cc_get_resp.status_code == 200, f"Expected 200, got {cc_get_resp.status_code}: {cc_get_resp.text}"
    customer_data = cc_get_resp.json()["customers"][0]
    assert customer_data["streetAddress"] == "New Music St 2"
    assert customer_data["postalCode"] == "6001"

# --- id=538  name='Customer Core Cities' ---
def test_customer_core_get_cities():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "streetAddress": "Code St 1",
        "postalCode": "7000",
        "city": "Chur",
        "email": f"grace_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-9999"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    postal_code = cc_resp.json()["postalCode"]

    resp = requests.get(get_url("customer-core", f"/cities/{postal_code}"), headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()
