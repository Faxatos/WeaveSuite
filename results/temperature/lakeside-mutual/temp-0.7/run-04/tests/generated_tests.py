# Tests generated in iteration 04
# Captured: 2026-07-09T20:16:52
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1235  name='Insurance Quote Request Illegal Transition' ---
def test_insurance_quote_request_illegal_transition():
    email, token = create_self_service_user()
    customer_id = register_self_service_customer(token)
    headers_ss = {"X-Auth-Token": token}

    payload_req = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "S1", "postalCode": "1234", "city": "C1"},
            "billingAddress": {"streetAddress": "S1", "postalCode": "1234", "city": "C1"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp_req = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=payload_req, headers=headers_ss, timeout=10)
    assert resp_req.status_code == 200, f"Expected 200, got {resp_req.status_code}: {resp_req.text}"
    quote_id = resp_req.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED"
    }
    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_ss_patch = requests.patch(ss_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp_ss_patch.status_code == 401, f"Expected 401, got {resp_ss_patch.status_code}: {resp_ss_patch.text}"

# --- id=1236  name='Policy Management Crud' ---
def test_policy_management_crud():
    headers_core = get_auth_headers_core()
    headers_pm = get_auth_headers_policy()

    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Main St 1",
        "postalCode": "1234",
        "city": "Metropolis",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-0000"
    }
    resp_core = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=headers_core, timeout=10)
    assert resp_core.status_code == 200, f"Expected 200, got {resp_core.status_code}: {resp_core.text}"
    customer_id = resp_core.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full auto coverage"}]}
    }
    resp_pm_post = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers_pm, timeout=10)
    assert resp_pm_post.status_code == 200, f"Expected 200, got {resp_pm_post.status_code}: {resp_pm_post.text}"
    policy_id = resp_pm_post.json()["policyId"]

    # Follow-up GET
    pm_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp_pm_get = requests.get(pm_url, headers=headers_pm, timeout=10)
    assert resp_pm_get.status_code == 200, f"Expected 200, got {resp_pm_get.status_code}: {resp_pm_get.text}"
    assert resp_pm_get.json()["policyType"] == "Auto"

    policy_payload["policyType"] = "Home"
    resp_pm_put = requests.put(pm_url, json=policy_payload, headers=headers_pm, timeout=10)
    assert resp_pm_put.status_code == 200, f"Expected 200, got {resp_pm_put.status_code}: {resp_pm_put.text}"

    # Follow-up GET
    resp_pm_get_updated = requests.get(pm_url, headers=headers_pm, timeout=10)
    assert resp_pm_get_updated.status_code == 200, f"Expected 200, got {resp_pm_get_updated.status_code}: {resp_pm_get_updated.text}"
    assert resp_pm_get_updated.json()["policyType"] == "Home"

    resp_pm_delete = requests.delete(pm_url, headers=headers_pm, timeout=10)
    assert resp_pm_delete.status_code == 204, f"Expected 204, got {resp_pm_delete.status_code}: {resp_pm_delete.text}"

# --- id=1237  name='Policy Management Missing Customer' ---
def test_policy_management_missing_customer():
    headers_pm = get_auth_headers_policy()
    fake_customer_id = str(uuid.uuid4())

    policy_payload = {
        "customerId": fake_customer_id,
        "policyType": "Auto",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full auto coverage"}]}
    }
    resp_pm_post = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers_pm, timeout=10)
    assert resp_pm_post.status_code == 424, f"Expected 424, got {resp_pm_post.status_code}: {resp_pm_post.text}"

# --- id=1238  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    headers_core = get_auth_headers_core()
    customer_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1990-05-05T00:00:00Z",
        "streetAddress": "Build St 1",
        "postalCode": "5678",
        "city": "Builderland",
        "email": f"bob_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-9999"
    }
    resp_core = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=headers_core, timeout=10)
    assert resp_core.status_code == 200, f"Expected 200, got {resp_core.status_code}: {resp_core.text}"
    customer_id = resp_core.json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    resp_patch_400 = requests.patch(cm_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp_patch_400.status_code == 400, f"Expected 400, got {resp_patch_400.status_code}: {resp_patch_400.text}"

    resp_patch_404 = requests.patch(cm_url, json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp_patch_404.status_code == 404, f"Expected 404, got {resp_patch_404.status_code}: {resp_patch_404.text}"

# --- id=1239  name='Customer Core Phone Number Missing' ---
def test_customer_core_phone_number_missing():
    headers_core = get_auth_headers_core()
    customer_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1900-01-01T00:00:00Z",
        "streetAddress": "Cinema St 1",
        "postalCode": "0000",
        "city": "Hollywood",
        "email": f"charlie_{uuid.uuid4().hex[:8]}@example.com"
    }
    resp_core = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=headers_core, timeout=10)
    assert resp_core.status_code == 500, f"Expected 500, got {resp_core.status_code}: {resp_core.text}"

# --- id=1240  name='Policy Management Insurance Quote Request Not Found' ---
def test_policy_management_insurance_quote_request_not_found():
    headers = get_auth_headers_policy()
    fake_id = 999999999
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"), headers=headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1241  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    headers_core = get_auth_headers_core()
    customer_payload = {
        "firstname": "Dave",
        "lastname": "Mustaine",
        "birthday": "1961-09-13T00:00:00Z",
        "streetAddress": "Symphony Blvd 1",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": f"dave_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-6666"
    }
    resp_core = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=headers_core, timeout=10)
    assert resp_core.status_code == 200, f"Expected 200, got {resp_core.status_code}: {resp_core.text}"
    customer_id = resp_core.json()["customerId"]

    cm_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_payload = {
        "firstname": "David",
        "lastname": "Mustaine",
        "birthday": "1961-09-13T00:00:00Z",
        "email": customer_payload["email"],
        "phoneNumber": "555-7777",
        "moveHistory": []
    }
    resp_cm_put = requests.put(cm_url, json=update_payload, timeout=10)
    assert resp_cm_put.status_code == 200, f"Expected 200, got {resp_cm_put.status_code}: {resp_cm_put.text}"

    # Follow-up GET on customer-core to verify the update propagated (or is shared DB)
    core_url = get_url("customer-core", f"/customers/{customer_id}")
    resp_core_get = requests.get(core_url, headers=headers_core, timeout=10)
    assert resp_core_get.status_code == 200, f"Expected 200, got {resp_core_get.status_code}: {resp_core_get.text}"
    core_cust = resp_core_get.json()["customers"][0]
    assert core_cust["firstname"] == "David"

# --- id=1242  name='Risk Factor Compute' ---
def test_risk_factor_compute():
    headers = get_auth_headers_policy()
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=1233  name='Customer Self Registration And Update' ---
def test_customer_self_service_registration_and_update():
    email, token = create_self_service_user()
    headers = {"X-Auth-Token": token}

    # Register customer
    customer_id = register_self_service_customer(token)

    # Get user to verify customerId is now present
    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json().get("customerId") == customer_id

    # Update address
    new_address = {
        "streetAddress": "New Street 2",
        "postalCode": "9000",
        "city": "Geneva"
    }
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    resp_addr = requests.put(addr_url, json=new_address, headers=headers, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    # Follow-up GET to verify address update on customer-core
    core_url = get_url("customer-core", f"/customers/{customer_id}")
    resp_core_get = requests.get(core_url, headers=get_auth_headers_core(), timeout=10)
    assert resp_core_get.status_code == 200, f"Expected 200, got {resp_core_get.status_code}: {resp_core_get.text}"
    core_cust = resp_core_get.json()["customers"][0]
    assert core_cust["streetAddress"] == "New Street 2"
    assert core_cust["postalCode"] == "9000"
    assert core_cust["city"] == "Geneva"

# --- id=1234  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email, token = create_self_service_user()
    customer_id = register_self_service_customer(token)
    headers_ss = {"X-Auth-Token": token}
    headers_pm = get_auth_headers_policy()

    # Create quote request
    payload_req = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "S1", "postalCode": "1234", "city": "C1"},
            "billingAddress": {"streetAddress": "S1", "postalCode": "1234", "city": "C1"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp_req = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=payload_req, headers=headers_ss, timeout=10)
    assert resp_req.status_code == 200, f"Expected 200, got {resp_req.status_code}: {resp_req.text}"
    quote_id = resp_req.json()["id"]

    # Follow-up GET on self-service
    ss_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_ss_verify_req = requests.get(ss_url, headers=headers_ss, timeout=10)
    assert resp_ss_verify_req.status_code == 200, f"Expected 200, got {resp_ss_verify_req.status_code}: {resp_ss_verify_req.text}"

    # Poll policy-management until 200
    pm_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(15):
        resp_pm_get = requests.get(pm_url, headers=headers_pm, timeout=10)
        if resp_pm_get.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management")

    # Draft quote on policy-management
    future_date = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat() + "Z"
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": future_date,
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp_pm_patch = requests.patch(pm_url, json=draft_payload, headers=headers_pm, timeout=10)
    assert resp_pm_patch.status_code == 200, f"Expected 200, got {resp_pm_patch.status_code}: {resp_pm_patch.text}"

    # Follow-up GET on policy-management
    resp_pm_verify = requests.get(pm_url, headers=headers_pm, timeout=10)
    assert resp_pm_verify.status_code == 200, f"Expected 200, got {resp_pm_verify.status_code}: {resp_pm_verify.text}"
    pm_history = resp_pm_verify.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in pm_history)

    # Poll self-service until QUOTE_RECEIVED
    for _ in range(15):
        resp_ss_get = requests.get(ss_url, headers=headers_ss, timeout=10)
        assert resp_ss_get.status_code == 200, f"Expected 200, got {resp_ss_get.status_code}: {resp_ss_get.text}"
        status_history = resp_ss_get.json().get("statusHistory", [])
        if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
            break
        time.sleep(1)
    else:
        pytest.fail("Quote draft did not propagate to self-service")

    # Accept quote on self-service
    accept_payload = {
        "status": "QUOTE_ACCEPTED"
    }
    resp_ss_patch = requests.patch(ss_url, json=accept_payload, headers=headers_ss, timeout=10)
    assert resp_ss_patch.status_code == 200, f"Expected 200, got {resp_ss_patch.status_code}: {resp_ss_patch.text}"

    # Follow-up GET on self-service
    resp_ss_verify_accept = requests.get(ss_url, headers=headers_ss, timeout=10)
    assert resp_ss_verify_accept.status_code == 200, f"Expected 200, got {resp_ss_verify_accept.status_code}: {resp_ss_verify_accept.text}"
    status_history_final = resp_ss_verify_accept.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history_final)
