# Tests generated in iteration 05
# Captured: 2026-07-08T11:46:44
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=780  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"quote_{uuid.uuid4()}@example.com"
    password = "password123"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    requests.post(signup_url, json={"email": email, "password": password}, timeout=10)

    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonder",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Basel",
        "streetAddress": "Wonderland 1",
        "postalCode": "4000",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(reg_url, headers=ss_headers, json=reg_payload, timeout=10)
    customer_id = resp.json()["customerId"]

    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonder",
            "contactAddress": {"streetAddress": "Wonderland 1", "postalCode": "4000", "city": "Basel"},
            "billingAddress": {"streetAddress": "Wonderland 1", "postalCode": "4000", "city": "Basel"}
        },
        "insuranceOptions": {
            "startDate": "2023-10-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    resp = requests.post(qr_url, headers=ss_headers, json=qr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    qr_id = resp.json()["id"]

    qr_get_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    resp = requests.get(qr_get_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.patch(qr_get_url, headers=ss_headers, json={"status": "QUOTE_ACCEPTED"}, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(15):
        resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-12-31T00:00:00Z",
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"}
    }
    resp = requests.patch(pm_qr_url, headers=pm_headers, json=draft_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    received = False
    for _ in range(15):
        resp = requests.get(qr_get_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "Quote draft did not propagate back to self-service"

    resp = requests.patch(qr_get_url, headers=ss_headers, json={"status": "QUOTE_ACCEPTED"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(qr_get_url, headers=ss_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

# --- id=781  name='Customer Management Interactions Errors' ---
def test_customer_management_interactions_errors():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "streetAddress": "789 Ave",
        "postalCode": "9012",
        "city": "Lucerne",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(core_cust_url, headers=core_headers, json=cust_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    int_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    resp = requests.patch(int_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.patch(int_url, json={"lastAcknowledgedInteractionId": "some-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=777  name='Customer Self Signup And Registration' ---
def test_customer_self_service_signup_and_registration():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()

    auth_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, headers=headers, json=reg_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "New St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    resp = requests.put(addr_url, headers=headers, json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

# --- id=778  name='Customer Core Crud And Errors' ---
def test_customer_core_crud_and_errors():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    base_url = get_url("customer-core", "/customers")

    bad_payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Lane",
        "postalCode": "1234",
        "city": "Bern",
        "email": f"jane_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(base_url, headers=headers, json=bad_payload, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

    good_payload = bad_payload.copy()
    good_payload["phoneNumber"] = "555-9999"
    resp = requests.post(base_url, headers=headers, json=good_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "Jane"

    get_url_cust = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_cust, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()["customers"][0]
    assert fetched["customerId"] == customer_id
    assert fetched["email"] == good_payload["email"]

    update_payload = good_payload.copy()
    update_payload["firstname"] = "Janet"
    resp = requests.put(get_url_cust, headers=headers, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["firstname"] == "Janet"

    resp = requests.get(get_url_cust, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Janet"

# --- id=779  name='Policy Management Create And Dependency Error' ---
def test_policy_management_create_and_dependency_error():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    policies_url = get_url("policy-management-backend", "/policies")
    fake_customer_id = str(uuid.uuid4())
    policy_payload = {
        "customerId": fake_customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(policies_url, headers=policy_headers, json=policy_payload, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

    core_cust_url = get_url("customer-core", "/customers")
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Smith",
        "streetAddress": "456 Road",
        "postalCode": "5678",
        "city": "Geneva",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(core_cust_url, headers=core_headers, json=cust_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    real_customer_id = resp.json()["customerId"]

    policy_payload["customerId"] = real_customer_id
    resp = requests.post(policies_url, headers=policy_headers, json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == real_customer_id
