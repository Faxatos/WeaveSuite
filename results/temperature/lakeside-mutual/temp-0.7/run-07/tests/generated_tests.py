# Tests generated in iteration 07
# Captured: 2026-07-09T21:50:43
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1257  name='Self Quote Workflow' ---
def test_self_service_quote_workflow():
    # 1. Signup
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email

    # 2. Login & Follow-up GET for User
    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers_ss,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["email"] == email

    # 3. Register Customer
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=headers_ss,
        json={
            "firstname": "John",
            "lastname": "Doe",
            "birthday": "1990-01-01T00:00:00Z",
            "city": "Zurich",
            "streetAddress": "Test Street 1",
            "postalCode": "8000",
            "phoneNumber": "555-1234"
        },
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # Follow-up GET for Register Customer
    cust_get_resp = requests.get(
        get_url("customer-self-service-backend", f"/customers/{customer_id}"),
        headers=headers_ss,
        timeout=10
    )
    assert cust_get_resp.status_code == 200, f"Expected 200, got {cust_get_resp.status_code}: {cust_get_resp.text}"
    assert cust_get_resp.json()["customerId"] == customer_id

    # 4. Create Quote Request
    quote_req_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        headers=headers_ss,
        json={
            "customerInfo": {
                "customerId": customer_id,
                "firstname": "John",
                "lastname": "Doe",
                "contactAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Test Street 1"},
                "billingAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Test Street 1"}
            },
            "insuranceOptions": {
                "startDate": "2025-01-01T00:00:00Z",
                "insuranceType": "Life",
                "deductible": {"amount": 100, "currency": "CHF"}
            }
        },
        timeout=10
    )
    assert quote_req_resp.status_code == 200, f"Expected 200, got {quote_req_resp.status_code}: {quote_req_resp.text}"
    quote_id = quote_req_resp.json()["id"]

    # Follow-up GET for Quote Request
    quote_get_resp = requests.get(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        headers=headers_ss,
        timeout=10
    )
    assert quote_get_resp.status_code == 200, f"Expected 200, got {quote_get_resp.status_code}: {quote_get_resp.text}"
    assert quote_get_resp.json()["id"] == quote_id

    # 5. Policy Management polls for the quote request
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    for _ in range(15):
        pm_get_resp = requests.get(pm_quote_url, headers=headers_pm, timeout=10)
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"

    # 6. Policy Management drafts quote
    expiration_date = "2099-12-31T23:59:59Z"
    draft_resp = requests.patch(
        pm_quote_url,
        headers=headers_pm,
        json={
            "status": "QUOTE_RECEIVED",
            "expirationDate": expiration_date,
            "insurancePremium": {"amount": 500, "currency": "CHF"},
            "policyLimit": {"amount": 100000, "currency": "CHF"}
        },
        timeout=10
    )
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # Follow-up GET in Policy Management
    pm_get_draft = requests.get(pm_quote_url, headers=headers_pm, timeout=10)
    assert pm_get_draft.status_code == 200, f"Expected 200, got {pm_get_draft.status_code}: {pm_get_draft.text}"
    pm_statuses = [s["status"] for s in pm_get_draft.json().get("statusHistory", [])]
    assert "QUOTE_RECEIVED" in pm_statuses, "Expected QUOTE_RECEIVED in Policy Management statusHistory"

    # 7. Self-Service polls for QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    for _ in range(15):
        ss_get_resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
        assert ss_get_resp.status_code == 200, f"Expected 200, got {ss_get_resp.status_code}: {ss_get_resp.text}"
        statuses = [s["status"] for s in ss_get_resp.json().get("statusHistory", [])]
        if "QUOTE_RECEIVED" in statuses:
            break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in statuses, f"Expected QUOTE_RECEIVED in statusHistory, got {statuses}"

    # 8. Self-Service accepts quote
    accept_resp = requests.patch(
        ss_quote_url,
        headers=headers_ss,
        json={
            "status": "QUOTE_ACCEPTED",
            "expirationDate": expiration_date,
            "insurancePremium": {"amount": 500, "currency": "CHF"},
            "policyLimit": {"amount": 100000, "currency": "CHF"}
        },
        timeout=10
    )
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # 9. Verify final state with follow-up GET
    final_resp = requests.get(ss_quote_url, headers=headers_ss, timeout=10)
    assert final_resp.status_code == 200, f"Expected 200, got {final_resp.status_code}: {final_resp.text}"
    final_statuses = [s["status"] for s in final_resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_statuses, "Expected QUOTE_ACCEPTED in final status history"

# --- id=1258  name='Self Invalid Quote Transition' ---
def test_self_service_invalid_quote_transition():
    # 1. Signup & Login
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    # 2. Register Customer
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        headers=headers_ss,
        json={
            "firstname": "Alice",
            "lastname": "Smith",
            "birthday": "1985-05-05T00:00:00Z",
            "city": "Bern",
            "streetAddress": "Test 2",
            "postalCode": "3000",
            "phoneNumber": "555-4321"
        },
        timeout=10
    )
    customer_id = reg_resp.json()["customerId"]

    # Follow-up GET
    cust_get = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers_ss, timeout=10)
    assert cust_get.status_code == 200, f"Expected 200, got {cust_get.status_code}: {cust_get.text}"
    assert cust_get.json()["customerId"] == customer_id

    # 3. Create Quote Request
    quote_req_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        headers=headers_ss,
        json={
            "customerInfo": {
                "customerId": customer_id,
                "firstname": "Alice",
                "lastname": "Smith",
                "contactAddress": {"city": "Bern", "postalCode": "3000", "streetAddress": "Test 2"},
                "billingAddress": {"city": "Bern", "postalCode": "3000", "streetAddress": "Test 2"}
            },
            "insuranceOptions": {
                "startDate": "2025-01-01T00:00:00Z",
                "insuranceType": "Life",
                "deductible": {"amount": 200, "currency": "CHF"}
            }
        },
        timeout=10
    )
    quote_id = quote_req_resp.json()["id"]

    # Follow-up GET
    quote_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_ss, timeout=10)
    assert quote_get.status_code == 200, f"Expected 200, got {quote_get.status_code}: {quote_get.text}"
    assert quote_get.json()["id"] == quote_id

    # 4. Attempt to accept quote while still in REQUEST_SUBMITTED state
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_resp = requests.patch(
        ss_quote_url,
        headers=headers_ss,
        json={
            "status": "QUOTE_ACCEPTED",
            "expirationDate": "2099-12-31T23:59:59Z",
            "insurancePremium": {"amount": 500, "currency": "CHF"},
            "policyLimit": {"amount": 100000, "currency": "CHF"}
        },
        timeout=10
    )
    assert accept_resp.status_code == 401, f"Expected 401 for illegal status transition, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=1259  name='Policy Management Create Policy' ---
def test_policy_management_create_delete_policy():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    # 1. Create customer in core
    core_cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers_core,
        json={
            "firstname": "Bob",
            "lastname": "Builder",
            "birthday": "1980-01-01T00:00:00Z",
            "streetAddress": "Build St 1",
            "postalCode": "1000",
            "city": "Lausanne",
            "email": f"bob_{uuid.uuid4()}@example.com",
            "phoneNumber": "555-9999"
        },
        timeout=10
    )
    assert core_cust_resp.status_code == 200, f"Expected 200, got {core_cust_resp.status_code}: {core_cust_resp.text}"
    customer_id = core_cust_resp.json()["customerId"]

    # Follow-up GET for customer
    core_get_cust = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers_core,
        timeout=10
    )
    assert core_get_cust.status_code == 200, f"Expected 200, got {core_get_cust.status_code}: {core_get_cust.text}"
    assert core_get_cust.json()["customers"][0]["customerId"] == customer_id

    # 2. Create policy in policy management
    headers_pm = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_policy_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        headers=headers_pm,
        json={
            "customerId": customer_id,
            "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
            "policyType": "Auto",
            "deductible": {"amount": 500, "currency": "CHF"},
            "policyLimit": {"amount": 50000, "currency": "CHF"},
            "insurancePremium": {"amount": 1200, "currency": "CHF"},
            "insuringAgreement": {
                "agreementItems": [
                    {"title": "Coverage A", "description": "Liability"}
                ]
            }
        },
        timeout=10
    )
    assert pm_policy_resp.status_code == 200, f"Expected 200, got {pm_policy_resp.status_code}: {pm_policy_resp.text}"
    policy_id = pm_policy_resp.json()["policyId"]

    # 3. Follow-up GET policy
    pm_get_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}?expand=customer"),
        headers=headers_pm,
        timeout=10
    )
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"
    assert pm_get_resp.json()["policyId"] == policy_id
    assert pm_get_resp.json()["customer"]["customerId"] == customer_id

    # 4. Delete policy
    pm_del_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=headers_pm,
        timeout=10
    )
    assert pm_del_resp.status_code == 204, f"Expected 204, got {pm_del_resp.status_code}: {pm_del_resp.text}"

    # 5. Follow-up GET after delete via listing
    pm_list_get = requests.get(
        get_url("policy-management-backend", "/policies"),
        headers=headers_pm,
        timeout=10
    )
    assert pm_list_get.status_code == 200, f"Expected 200, got {pm_list_get.status_code}: {pm_list_get.text}"
    policies = pm_list_get.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies), "Policy should be deleted and not appear in listing"

# --- id=1260  name='Customer Core Missing Phone Number Error' ---
def test_customer_core_missing_phone_number_error():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    # 1. Create customer in core (valid)
    core_cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers_core,
        json={
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "birthday": "1900-01-01T00:00:00Z",
            "streetAddress": "Silent St 1",
            "postalCode": "2000",
            "city": "Neuchatel",
            "email": f"charlie_{uuid.uuid4()}@example.com",
            "phoneNumber": "555-0000"
        },
        timeout=10
    )
    assert core_cust_resp.status_code == 200, f"Expected 200, got {core_cust_resp.status_code}: {core_cust_resp.text}"
    customer_id = core_cust_resp.json()["customerId"]

    # Follow-up GET
    core_get_cust = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers_core,
        timeout=10
    )
    assert core_get_cust.status_code == 200, f"Expected 200, got {core_get_cust.status_code}: {core_get_cust.text}"
    assert core_get_cust.json()["customers"][0]["customerId"] == customer_id

    # 2. Update without phoneNumber -> expect 500
    update_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=headers_core,
        json={
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "birthday": "1900-01-01T00:00:00Z",
            "streetAddress": "Silent St 2",
            "postalCode": "2000",
            "city": "Neuchatel",
            "email": f"charlie_{uuid.uuid4()}@example.com"
            # phoneNumber omitted
        },
        timeout=10
    )
    assert update_resp.status_code == 500, f"Expected 500 for missing phoneNumber, got {update_resp.status_code}: {update_resp.text}"

# --- id=1261  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    # 1. Create customer in core
    core_cust_resp = requests.post(
        get_url("customer-core", "/customers"),
        headers=headers_core,
        json={
            "firstname": "Diana",
            "lastname": "Prince",
            "birthday": "1980-01-01T00:00:00Z",
            "streetAddress": "Themyscira 1",
            "postalCode": "1234",
            "city": "Island",
            "email": f"diana_{uuid.uuid4()}@example.com",
            "phoneNumber": "555-1111"
        },
        timeout=10
    )
    assert core_cust_resp.status_code == 200, f"Expected 200, got {core_cust_resp.status_code}: {core_cust_resp.text}"
    customer_id = core_cust_resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    # 2. Test 400 for empty lastAcknowledgedInteractionId
    resp_400 = requests.patch(
        patch_url,
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert resp_400.status_code == 400, f"Expected 400 for empty lastAcknowledgedInteractionId, got {resp_400.status_code}: {resp_400.text}"

    # 3. Test 404 for non-existent log (valid body)
    resp_404 = requests.patch(
        patch_url,
        json={"lastAcknowledgedInteractionId": "dummy-id"},
        timeout=10
    )
    assert resp_404.status_code == 404, f"Expected 404 for non-existent log, got {resp_404.status_code}: {resp_404.text}"
