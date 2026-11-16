# Tests generated in iteration 13
# Captured: 2026-07-09T13:30:58
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1156  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    payload = {
        "firstname": random_string(),
        "lastname": random_string(),
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": f"{random_string()}@test.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_AUTH, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data["customers"][0]["customerId"] == customer_id
    assert get_data["customers"][0]["firstname"] == payload["firstname"]

    update_payload = payload.copy()
    update_payload["firstname"] = "UpdatedName"
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=CORE_AUTH, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    get_resp2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=CORE_AUTH, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json()["customers"][0]["firstname"] == "UpdatedName"

# --- id=1157  name='Customer Core Create Missing Phone Number 500' ---
def test_customer_core_create_missing_phone_number_500():
    payload = {
        "firstname": random_string(),
        "lastname": random_string(),
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": f"{random_string()}@test.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=CORE_AUTH, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1158  name='Customer Self Signup Auth Register' ---
def test_customer_self_service_signup_auth_register():
    email = f"{random_string()}@test.com"
    password = random_string(12)

    signup_payload = {"email": email, "password": password}
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email

    auth_payload = {"email": email, "password": password}
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": random_string(),
        "lastname": random_string(),
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Test City",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

# --- id=1159  name='Policy Management Create Policy Missing Customer 424' ---
def test_policy_management_create_policy_missing_customer_424():
    fake_customer_id = str(uuid.uuid4())
    payload = {
        "customerId": fake_customer_id,
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=payload, headers=POLICY_AUTH, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1160  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    cust_payload = {
        "firstname": random_string(),
        "lastname": random_string(),
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": f"{random_string()}@test.com",
        "phoneNumber": "555-1234"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=CORE_AUTH, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=POLICY_AUTH, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    get_pol_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_AUTH, timeout=10)
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=POLICY_AUTH, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    list_resp = requests.get(get_url("policy-management-backend", "/policies"), headers=POLICY_AUTH, timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policies = [p["policyId"] for p in list_resp.json().get("policies", [])]
    assert policy_id not in policies

# --- id=1161  name='Customer Management Interaction Log Errors' ---
def test_customer_management_interaction_log_errors():
    cust_payload = {
        "firstname": random_string(),
        "lastname": random_string(),
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": f"{random_string()}@test.com",
        "phoneNumber": "555-1234"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=CORE_AUTH, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    patch_payload_400 = {"lastAcknowledgedInteractionId": ""}
    patch_resp_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_400, timeout=10)
    assert patch_resp_400.status_code == 400, f"Expected 400, got {patch_resp_400.status_code}: {patch_resp_400.text}"

    patch_payload_404 = {"lastAcknowledgedInteractionId": "some-id"}
    patch_resp_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload_404, timeout=10)
    assert patch_resp_404.status_code == 404, f"Expected 404, got {patch_resp_404.status_code}: {patch_resp_404.text}"

# --- id=1162  name='Customer Self Quote Request Illegal Transition 401' ---
def test_customer_self_service_quote_request_illegal_transition_401():
    email = f"{random_string()}@test.com"
    password = random_string(12)

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": random_string(),
        "lastname": random_string(),
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Test City",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": reg_payload["firstname"],
            "lastname": reg_payload["lastname"],
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Test City"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Test City"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    get_quote_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"
    assert get_quote_resp.json()["id"] == quote_id

    patch_payload = {"status": "QUOTE_ACCEPTED"}
    patch_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=patch_payload, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"
