# Tests generated in iteration 12
# Captured: 2026-07-08T15:28:13
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=836  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert "customers" in get_data, "Expected 'customers' array in response"
    assert len(get_data["customers"]) == 1, "Expected exactly one customer in array"
    fetched_customer = get_data["customers"][0]
    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["firstname"] == payload["firstname"]
    assert fetched_customer["lastname"] == payload["lastname"]
    assert fetched_customer["email"] == payload["email"]
    assert "phoneNumber" in fetched_customer

# --- id=837  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4().hex}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=838  name='Customer Core Update Address' ---
def test_customer_core_update_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "David",
        "lastname": "Bowie",
        "streetAddress": "123 Space St",
        "postalCode": "11111",
        "city": "Mars",
        "email": f"david.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    addr_payload = {
        "streetAddress": "456 Earth St",
        "postalCode": "22222",
        "city": "London"
    }
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=addr_payload, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    fetched_customer = get_resp.json()["customers"][0]
    assert fetched_customer["streetAddress"] == addr_payload["streetAddress"]
    assert fetched_customer["postalCode"] == addr_payload["postalCode"]
    assert fetched_customer["city"] == addr_payload["city"]

# --- id=839  name='Customer Management Acknowledge Interactions Errors' ---
def test_customer_management_acknowledge_interactions_errors():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"alice.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-5678"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    patch_payload_empty = {"lastAcknowledgedInteractionId": ""}
    patch_resp_empty = requests.patch(patch_url, json=patch_payload_empty, timeout=10)
    assert patch_resp_empty.status_code == 400, f"Expected 400, got {patch_resp_empty.status_code}: {patch_resp_empty.text}"

    get_log_resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert get_log_resp.status_code == 200, f"Expected 200, got {get_log_resp.status_code}: {get_log_resp.text}"

    patch_payload_valid = {"lastAcknowledgedInteractionId": "dummy-id-123"}
    patch_resp_404 = requests.patch(patch_url, json=patch_payload_valid, timeout=10)
    assert patch_resp_404.status_code == 404, f"Expected 404, got {patch_resp_404.status_code}: {patch_resp_404.text}"

    get_log_resp_2 = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert get_log_resp_2.status_code == 200, f"Expected 200, got {get_log_resp_2.status_code}: {get_log_resp_2.text}"

# --- id=840  name='Customer Self Workflow And Illegal Transition' ---
def test_customer_self_service_workflow_and_illegal_transition():
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "password123"
    signup_payload = {"email": email, "password": password}
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email
    assert "customerId" not in signup_resp.json()

    login_payload = {"email": email, "password": password}
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-05-05T00:00:00Z",
        "city": "Buildtown",
        "streetAddress": "123 Brick Ln",
        "postalCode": "10001",
        "phoneNumber": "555-9999"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "123 Brick Ln", "postalCode": "10001", "city": "Buildtown"},
            "billingAddress": {"streetAddress": "123 Brick Ln", "postalCode": "10001", "city": "Buildtown"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    get_quote_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"

    patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    patch_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=patch_payload, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

    get_quote_resp_after = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert get_quote_resp_after.status_code == 200, f"Expected 200, got {get_quote_resp_after.status_code}: {get_quote_resp_after.text}"

# --- id=841  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "streetAddress": "789 Cinema Blvd",
        "postalCode": "90210",
        "city": "Hollywood",
        "email": f"charlie.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-0000"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    pol_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pol_payload = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "All Risk"}]}
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=pol_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy = pol_resp.json()
    policy_id = policy["policyId"]

    get_pol_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pol_headers, timeout=10)
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id
    assert get_pol_resp.json()["customer"] == customer_id

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pol_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    list_resp = requests.get(get_url("policy-management-backend", "/policies"), headers=pol_headers, timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policies = list_resp.json().get("policies", [])
    assert all(p["policyId"] != policy_id for p in policies), "Deleted policy still found in list"

# --- id=842  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
