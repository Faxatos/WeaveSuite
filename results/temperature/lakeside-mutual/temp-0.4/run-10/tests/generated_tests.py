# Tests generated in iteration 10
# Captured: 2026-07-08T14:22:07
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=816  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == payload["firstname"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data["customers"][0]["customerId"] == customer_id
    assert get_data["customers"][0]["firstname"] == payload["firstname"]

# --- id=817  name='Customer Core Create Customer Missing Phone' ---
def test_customer_core_create_customer_missing_phone():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=818  name='Customer Management Backend Acknowledge Interactions Invalid Body' ---
def test_customer_management_backend_acknowledge_interactions_invalid_body():
    customer_id = str(uuid.uuid4())
    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=819  name='Customer Management Backend Acknowledge Interactions Not Found' ---
def test_customer_management_backend_acknowledge_interactions_not_found():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Log",
        "lastname": "Test",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"log.test.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    core_resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert core_resp.status_code == 200, f"Expected 200, got {core_resp.status_code}: {core_resp.text}"
    customer_id = core_resp.json()["customerId"]

    patch_payload = {"lastAcknowledgedInteractionId": "interaction-1"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=820  name='Customer Self Backend Signup Login And Register Customer' ---
def test_customer_self_service_backend_signup_login_and_register_customer():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "Password123!"

    signup_payload = {"email": email, "password": password}
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email
    assert "customerId" not in signup_resp.json()

    auth_payload = {"email": email, "password": password}
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]

    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Self",
        "lastname": "Service",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Anytown",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    cust_resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json()["customerId"] == customer_id

# --- id=821  name='Customer Self Backend Respond To Quote Illegal Transition' ---
def test_customer_self_service_backend_respond_to_quote_illegal_transition():
    email = f"quote.{uuid.uuid4()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Quote", "lastname": "Test", "birthday": "1990-01-01T00:00:00Z",
        "city": "Anytown", "streetAddress": "123 Main St", "postalCode": "12345", "phoneNumber": "555-9876"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Quote",
            "lastname": "Test",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    get_quote_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"
    assert get_quote_resp.json()["id"] == quote_id

    patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    patch_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=patch_payload, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=822  name='Policy Management Backend Create And Policy' ---
def test_policy_management_backend_create_and_get_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Policy",
        "lastname": "Maker",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "456 Policy St",
        "postalCode": "54321",
        "city": "Policytown",
        "email": f"policy.maker.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    core_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert core_resp.status_code == 200, f"Expected 200, got {core_resp.status_code}: {core_resp.text}"
    customer_id = core_resp.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Fire", "description": "Fire coverage"}]
        }
    }
    policy_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert policy_resp.status_code == 200, f"Expected 200, got {policy_resp.status_code}: {policy_resp.text}"
    policy_id = policy_resp.json()["policyId"]
    assert policy_resp.json()["customer"] == customer_id

    get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["policyId"] == policy_id
    assert get_resp.json()["customer"] == customer_id

# --- id=823  name='Policy Management Backend Create Policy Missing Customer' ---
def test_policy_management_backend_create_policy_missing_customer():
    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": "non-existent-customer-id",
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Fire", "description": "Fire coverage"}]
        }
    }
    policy_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert policy_resp.status_code == 424, f"Expected 424, got {policy_resp.status_code}: {policy_resp.text}"

# --- id=824  name='Policy Management Backend Quote Request Not Found' ---
def test_policy_management_backend_quote_request_not_found():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_id = random.randint(1000000, 9999999)
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"), headers=headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=825  name='Policy Management Backend Respond To Quote Request Not Found' ---
def test_policy_management_backend_respond_to_quote_request_not_found():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_id = random.randint(1000000, 9999999)
    patch_payload = {
        "status": "REQUEST_REJECTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}"), json=patch_payload, headers=headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
