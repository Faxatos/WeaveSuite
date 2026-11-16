# Tests generated in iteration 01
# Captured: 2026-07-10T04:55:44
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1355  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_url = get_url("customer-core", "/customers")
    cust_data = generate_core_customer()
    resp = requests.post(core_url, json=cust_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_data = {
        "firstname": "UpdatedName",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "email": cust_data["email"],
        "phoneNumber": "+1987654321",
        "moveHistory": [
            {"streetAddress": "456 Elm St", "postalCode": "20002", "city": "Washington"}
        ]
    }
    resp = requests.put(mgmt_url, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(mgmt_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=1348  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = generate_email()
    password = "password123"

    # 1. Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register customer
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_data = generate_customer_registration()
    resp = requests.post(reg_url, json=reg_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 4. Get User to verify customerId
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 5. Change address
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    new_address = {"streetAddress": "789 Oak Ave", "postalCode": "30003", "city": "Atlanta"}
    resp = requests.put(addr_url, json=new_address, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 6. Verify address change in core service (strongest post-condition observable)
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_cust_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_cust_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    core_cust = resp.json()["customers"][0]
    assert core_cust["streetAddress"] == "789 Oak Ave"
    assert core_cust["city"] == "Atlanta"
    assert core_cust["postalCode"] == "30003"

# --- id=1349  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    # 1. Create customer in core
    core_url = get_url("customer-core", "/customers")
    cust_data = generate_core_customer()
    resp = requests.post(core_url, json=cust_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Create policy
    pol_url = get_url("policy-management-backend", "/policies")
    pol_data = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    resp = requests.post(pol_url, json=pol_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # 3. GET policy to verify full state
    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_pol_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    assert resp_json["policyId"] == policy_id
    assert resp_json["customer"] == customer_id
    assert resp_json["policyType"] == "HOME"
    assert resp_json["deductible"]["amount"] == 500
    assert resp_json["policyLimit"]["amount"] == 100000
    assert resp_json["insurancePremium"]["amount"] == 1000

    # 4. DELETE policy
    del_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.delete(del_pol_url, headers=core_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # 5. Verify deletion via list endpoint
    list_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = [p["policyId"] for p in resp.json().get("policies", [])]
    assert policy_id not in policies

# --- id=1350  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = generate_email()
    password = "password123"

    # Setup self-service customer
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    requests.post(get_url("customer-self-service-backend", "/customers"), json=generate_customer_registration(), headers=ss_headers, timeout=10)
    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    customer_id = user_resp.json()["customerId"]

    # Create quote request (self-service)
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "123 Main", "postalCode": "10001", "city": "NY"},
            "billingAddress": {"streetAddress": "123 Main", "postalCode": "10001", "city": "NY"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_data, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Poll policy-management until it arrives
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    arrived = False
    for _ in range(15):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            arrived = True
            break
        time.sleep(1)
    assert arrived, "Quote request did not arrive in policy-management-backend"

    # Draft quote (policy-management)
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 1500, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    resp = requests.patch(pm_quote_url, json=draft_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Poll self-service until QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    received = False
    for _ in range(15):
        resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = [h["status"] for h in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to self-service"

    # Accept quote (self-service)
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 1500, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    resp = requests.patch(ss_quote_url, json=accept_data, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify final state
    resp = requests.get(ss_quote_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    history = [h["status"] for h in resp_json.get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history
    assert resp_json["insuranceQuote"]["insurancePremium"]["amount"] == 1500
    assert resp_json["insuranceQuote"]["policyLimit"]["amount"] == 500000

# --- id=1351  name='Customer Self Quote Illegal Transition' ---
def test_customer_self_service_quote_illegal_transition():
    email = generate_email()
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    requests.post(get_url("customer-self-service-backend", "/customers"), json=generate_customer_registration(), headers=ss_headers, timeout=10)
    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    customer_id = user_resp.json()["customerId"]

    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "123 Main", "postalCode": "10001", "city": "NY"},
            "billingAddress": {"streetAddress": "123 Main", "postalCode": "10001", "city": "NY"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp = requests.post(quote_req_url, json=quote_data, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Attempt to accept quote before QUOTE_RECEIVED
    ss_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 1500, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    resp = requests.patch(ss_quote_url, json=accept_data, headers=ss_headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1352  name='Customer Core Missing Phone Number Error' ---
def test_customer_core_missing_phone_number_error():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_url = get_url("customer-core", "/customers")

    cust_data = generate_core_customer()
    del cust_data["phoneNumber"]  # Remove required field to trigger 500

    resp = requests.post(core_url, json=cust_data, headers=core_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1353  name='Customer Management Interaction Logs Errors' ---
def test_customer_management_interaction_logs_errors():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_url = get_url("customer-core", "/customers")
    cust_data = generate_core_customer()
    resp = requests.post(core_url, json=cust_data, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    # Empty lastAcknowledgedInteractionId -> 400
    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # Valid lastAcknowledgedInteractionId but no logs exist -> 404
    resp = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": "12345"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1354  name='Policy Management Risk Factor' ---
def test_policy_management_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    url = get_url("policy-management-backend", "/riskfactor/compute")
    payload = {
        "birthday": "1980-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(url, json=payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
