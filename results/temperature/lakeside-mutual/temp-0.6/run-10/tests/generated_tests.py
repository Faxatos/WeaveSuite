# Tests generated in iteration 10
# Captured: 2026-07-09T11:53:52
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1134  name='Customer Self Registration And Address Update' ---
def test_customer_self_service_registration_and_address_update():
    email = random_email()
    password = "password123"

    # 1. Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # 2. Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # Follow-up GET for signup/login
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    # 3. Register customer
    cust_url = get_url("customer-self-service-backend", "/customers")
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(cust_url, headers=headers, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    get_cust_url = get_self_link_or_fallback(resp.json(), get_url("customer-self-service-backend", f"/customers/{customer_id}"))
    resp_get_cust = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"

    # Follow-up GET to verify customerId is now present in user profile
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # 4. Update address
    address_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    new_address = {
        "streetAddress": "New St 2",
        "postalCode": "9000",
        "city": "Bern"
    }
    resp = requests.put(address_url, headers=headers, json=new_address, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["city"] == "Bern"

    # Follow-up GET in customer-core to verify the address update propagated/is visible
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    core_get_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_get_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["city"] == "Bern"
    assert resp.json()["customers"][0]["streetAddress"] == "New St 2"

# --- id=1135  name='Customer Core Create And Policy Lifecycle' ---
def test_customer_core_create_and_policy_lifecycle():
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}

    # 1. Create customer in core
    core_url = get_url("customer-core", "/customers")
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Core St",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": random_email(),
        "phoneNumber": "555-9999"
    }
    resp = requests.post(core_url, headers=core_headers, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Follow-up GET
    get_core_url = get_self_link_or_fallback(resp.json(), get_url("customer-core", f"/customers/{customer_id}"))
    resp = requests.get(get_core_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["customerId"] == customer_id
    assert resp.json()["customers"][0]["firstname"] == "Alice"

    # 2. Create policy in policy-management
    policy_headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    policy_url = get_url("policy-management-backend", "/policies")
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
                {"title": "Item 1", "description": "Desc 1"}
            ]
        }
    }
    resp = requests.post(policy_url, headers=policy_headers, json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Follow-up GET
    get_policy_url = get_self_link_or_fallback(resp.json(), get_url("policy-management-backend", f"/policies/{policy_id}"))
    resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id

    # 3. Update policy
    update_payload = policy_payload.copy()
    update_payload["policyType"] = "Health"
    resp = requests.put(get_policy_url, headers=policy_headers, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Health"

    # Follow-up GET
    resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Health"

    # 4. Delete policy
    resp = requests.delete(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify absence via listing
    list_policies_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_policies_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies)

# --- id=1136  name='Insurance Quote Request Lifecycle And 401' ---
def test_insurance_quote_request_lifecycle_and_401():
    # Setup: Signup, Login, Register Customer
    email = random_email()
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers = {"X-Auth-Token": resp.json()["token"]}

    payload = {
        "firstname": "Eve",
        "lastname": "Adam",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=headers, json=payload, timeout=10)
    customer_id = resp.json()["customerId"]

    # 1. Create Quote Request
    url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "Adam",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(url, headers=headers, json=quote_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    # Follow-up GET on self-service
    get_url_ss = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_url_ss, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id

    # 2. Negative test: Try to accept quote while it's in REQUEST_SUBMITTED -> 401
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url_ss, headers=headers, json=accept_payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 3. Poll policy-management until it appears (async propagation)
    policy_headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    get_url_pm = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")

    found = False
    for _ in range(15):
        resp = requests.get(get_url_pm, headers=policy_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management"

    # 4. Draft quote in policy-management
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url_pm, headers=policy_headers, json=draft_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET in policy-management
    resp = requests.get(get_url_pm, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_RECEIVED" for s in history)

    # 5. Poll self-service until QUOTE_RECEIVED appears
    received = False
    for _ in range(15):
        resp = requests.get(get_url_ss, headers=headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to self-service"

    # 6. Now accept the quote
    resp = requests.patch(get_url_ss, headers=headers, json=accept_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify accepted
    resp = requests.get(get_url_ss, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in history)

# --- id=1137  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    # 1. Create in core
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    core_url = get_url("customer-core", "/customers")
    email = random_email()
    payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "streetAddress": "Comedy St",
        "postalCode": "3000",
        "city": "Vevey",
        "email": email,
        "phoneNumber": "555-0000"
    }
    resp = requests.post(core_url, headers=core_headers, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. Update in management
    mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_payload = {
        "firstname": "Charles",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "email": email,
        "phoneNumber": "555-0001",
        "moveHistory": []
    }
    resp = requests.put(mgmt_url, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET in management
    resp = requests.get(mgmt_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    # Follow-up GET in core to verify fields updated
    core_get_url = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(core_get_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Charles"

# --- id=1138  name='Customer Management Interaction Logs Negative' ---
def test_customer_management_interaction_logs_negative():
    # 1. Create a real customer in customer-core to get a valid ID
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    core_url = get_url("customer-core", "/customers")
    payload = {
        "firstname": "Log",
        "lastname": "Test",
        "streetAddress": "Log St",
        "postalCode": "4000",
        "city": "Basel",
        "email": random_email(),
        "phoneNumber": "555-1111"
    }
    resp = requests.post(core_url, headers=core_headers, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # 2. 400 Bad Request: lastAcknowledgedInteractionId empty
    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    # 3. 404 Not Found: valid body but no log exists for this new customer
    resp = requests.patch(url, json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1139  name='Customer Core Missing Phone Number 500' ---
def test_customer_core_missing_phone_number_500():
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    core_url = get_url("customer-core", "/customers")
    payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "streetAddress": "Build St",
        "postalCode": "2000",
        "city": "Geneva",
        "email": random_email()
        # phoneNumber missing
    }
    resp = requests.post(core_url, headers=core_headers, json=payload, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1140  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    policy_headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    url = get_url("policy-management-backend", "/riskfactor/compute")
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(url, headers=policy_headers, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=1141  name='Customer Self Cities' ---
def test_customer_self_service_get_cities():
    url = get_url("customer-self-service-backend", "/cities/8000")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()
    assert isinstance(resp.json()["cities"], list)

# --- id=1142  name='Customer Management Notifications' ---
def test_customer_management_get_notifications():
    url = get_url("customer-management-backend", "/notifications")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)

# --- id=1143  name='Customer Core Customers Pagination' ---
def test_customer_core_get_customers_pagination():
    core_headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    url = get_url("customer-core", "/customers?limit=5&offset=0")
    resp = requests.get(url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customers" in resp.json()
    assert isinstance(resp.json()["customers"], list)

# --- id=1144  name='Policy Management Policies Pagination' ---
def test_policy_management_get_policies_pagination():
    policy_headers = {"Authorization": f"Bearer {POLICY_API_KEY}"}
    url = get_url("policy-management-backend", "/policies?limit=5&offset=0")
    resp = requests.get(url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "policies" in resp.json()
    assert isinstance(resp.json()["policies"], list)
