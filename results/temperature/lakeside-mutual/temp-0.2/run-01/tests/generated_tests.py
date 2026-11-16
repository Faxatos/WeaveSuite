# Tests generated in iteration 01
# Captured: 2026-07-07T04:17:00
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=377  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    links = customer.get("_links", {})
    self_link = links.get("self", {}).get("href")
    if self_link:
        get_url_id = self_link if self_link.startswith("http") else get_url("customer-core", self_link)
    else:
        get_url_id = get_url("customer-core", f"/customers/{customer_id}")

    resp_get = requests.get(get_url_id, headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer_get = resp_get.json()
    assert "customers" in customer_get, f"Expected 'customers' in response: {customer_get}"
    assert len(customer_get["customers"]) == 1
    assert customer_get["customers"][0]["customerId"] == customer_id
    assert customer_get["customers"][0]["firstname"] == "John"
    assert "phoneNumber" in customer_get["customers"][0]

    payload["firstname"] = "Jane"
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    resp_put = requests.put(update_url, json=payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url_id, headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Jane"

# --- id=378  name='Customer Core Missing Phone Number Error' ---
def test_customer_core_missing_phone_number_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=379  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": "alice@example.com",
        "phoneNumber": "555-5678"
    }
    cc_url = get_url("customer-core", "/customers")
    cc_resp = requests.post(cc_url, json=customer_payload, headers=headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

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
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    pm_url = get_url("policy-management-backend", "/policies")
    pm_resp = requests.post(pm_url, json=policy_payload, headers=headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    policy = pm_resp.json()
    policy_id = policy["policyId"]

    links = policy.get("_links", {})
    self_link = links.get("self", {}).get("href")
    if self_link:
        get_pm_url = self_link if self_link.startswith("http") else get_url("policy-management-backend", self_link)
    else:
        get_pm_url = get_url("policy-management-backend", f"/policies/{policy_id}")

    get_pm_resp = requests.get(get_pm_url, headers=headers, timeout=10)
    assert get_pm_resp.status_code == 200, f"Expected 200, got {get_pm_resp.status_code}: {get_pm_resp.text}"
    assert get_pm_resp.json()["policyId"] == policy_id
    assert get_pm_resp.json()["customer"] == customer_id
    assert get_pm_resp.json()["policyType"] == "Life"

    del_pm_resp = requests.delete(get_pm_url, headers=headers, timeout=10)
    assert del_pm_resp.status_code == 204, f"Expected 204, got {del_pm_resp.status_code}: {del_pm_resp.text}"

# --- id=380  name='Policy Management Create Policy Failed Dependency' ---
def test_policy_management_create_policy_failed_dependency():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": "non-existent-id-12345",
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
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    pm_url = get_url("policy-management-backend", "/policies")
    pm_resp = requests.post(pm_url, json=policy_payload, headers=headers, timeout=10)
    assert pm_resp.status_code == 424, f"Expected 424, got {pm_resp.status_code}: {pm_resp.text}"

# --- id=381  name='End To End Quote Request Workflow' ---
def test_end_to_end_quote_request_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_payload = {"email": email, "password": password}
    ss_signup_url = get_url("customer-self-service-backend", "/auth/signup")
    ss_signup_resp = requests.post(ss_signup_url, json=signup_payload, timeout=10)
    assert ss_signup_resp.status_code == 200, f"Expected 200, got {ss_signup_resp.status_code}: {ss_signup_resp.text}"

    login_payload = {"email": email, "password": password}
    ss_login_url = get_url("customer-self-service-backend", "/auth")
    ss_login_resp = requests.post(ss_login_url, json=login_payload, timeout=10)
    assert ss_login_resp.status_code == 200, f"Expected 200, got {ss_login_resp.status_code}: {ss_login_resp.text}"
    token = ss_login_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "city": "Constructville",
        "streetAddress": "1 Build St",
        "postalCode": "10101",
        "phoneNumber": "555-9999"
    }
    ss_reg_url = get_url("customer-self-service-backend", "/customers")
    ss_reg_resp = requests.post(ss_reg_url, json=reg_payload, headers=ss_headers, timeout=10)
    assert ss_reg_resp.status_code == 200, f"Expected 200, got {ss_reg_resp.status_code}: {ss_reg_resp.text}"
    customer_id = ss_reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {
                "streetAddress": "1 Build St",
                "postalCode": "10101",
                "city": "Constructville"
            },
            "billingAddress": {
                "streetAddress": "1 Build St",
                "postalCode": "10101",
                "city": "Constructville"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    ss_qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    ss_qr_resp = requests.post(ss_qr_url, json=quote_req_payload, headers=ss_headers, timeout=10)
    assert ss_qr_resp.status_code == 200, f"Expected 200, got {ss_qr_resp.status_code}: {ss_qr_resp.text}"
    quote_request_id = ss_qr_resp.json()["id"]

    ss_qr_get_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_request_id}")
    ss_qr_get_resp = requests.get(ss_qr_get_url, headers=ss_headers, timeout=10)
    assert ss_qr_get_resp.status_code == 200, f"Expected 200, got {ss_qr_get_resp.status_code}: {ss_qr_get_resp.text}"

    ss_accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    ss_accept_resp = requests.patch(ss_qr_get_url, json=ss_accept_payload, headers=ss_headers, timeout=10)
    assert ss_accept_resp.status_code == 401, f"Expected 401, got {ss_accept_resp.status_code}: {ss_accept_resp.text}"

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_get_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_request_id}")

    found = False
    for _ in range(15):
        pm_qr_get_resp = requests.get(pm_qr_get_url, headers=pm_headers, timeout=10)
        if pm_qr_get_resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    pm_draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    pm_draft_resp = requests.patch(pm_qr_get_url, json=pm_draft_payload, headers=pm_headers, timeout=10)
    assert pm_draft_resp.status_code == 200, f"Expected 200, got {pm_draft_resp.status_code}: {pm_draft_resp.text}"

    quote_received = False
    for _ in range(15):
        ss_qr_get_resp = requests.get(ss_qr_get_url, headers=ss_headers, timeout=10)
        if ss_qr_get_resp.status_code == 200:
            status_history = ss_qr_get_resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                quote_received = True
                break
        time.sleep(1)
    assert quote_received, "QUOTE_RECEIVED status did not propagate to self-service-backend"

    ss_accept_resp2 = requests.patch(ss_qr_get_url, json=ss_accept_payload, headers=ss_headers, timeout=10)
    assert ss_accept_resp2.status_code == 200, f"Expected 200, got {ss_accept_resp2.status_code}: {ss_accept_resp2.text}"

    ss_qr_final_resp = requests.get(ss_qr_get_url, headers=ss_headers, timeout=10)
    assert ss_qr_final_resp.status_code == 200
    final_history = ss_qr_final_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in final_history), "Expected QUOTE_ACCEPTED in status history"

# --- id=382  name='Customer Management Interaction Logs Not Found' ---
def test_customer_management_interaction_logs_not_found():
    customer_id = f"non-existent-{uuid.uuid4().hex[:8]}"
    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    get_resp = requests.get(url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    patch_payload = {"lastAcknowledgedInteractionId": "123"}
    patch_resp = requests.patch(url, json=patch_payload, timeout=10)
    assert patch_resp.status_code == 404, f"Expected 404, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=383  name='Customer Self Auth Header Rejected' ---
def test_customer_self_service_auth_header_rejected():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(url, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=384  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    url = get_url("policy-management-backend", "/riskfactor/compute")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
