# Tests generated in iteration 17
# Captured: 2026-07-09T15:30:48
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1181  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    # 1. Create a new customer
    email = f"john.doe.{generate_random_string()}@example.com"
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": email,
        "phoneNumber": "555-1234"
    }
    create_url = get_url("customer-core", "/customers")
    resp = requests.post(create_url, json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer.get("customerId")
    assert customer_id is not None

    # 2. Verify customer creation
    get_url_path = get_url("customer-core", f"/customers/{customer_id}")
    resp_get = requests.get(get_url_path, headers=CORE_HEADERS, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_body = resp_get.json()
    assert "customers" in get_body, "Expected customers wrapper"
    fetched_customer = get_body["customers"][0]
    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["firstname"] == "John"
    assert fetched_customer["email"] == email

    # 3. Update customer profile
    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    put_url = get_url("customer-core", f"/customers/{customer_id}")
    resp_put = requests.put(put_url, json=update_payload, headers=CORE_HEADERS, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    # 4. Verify update
    resp_get_after_put = requests.get(get_url_path, headers=CORE_HEADERS, timeout=10)
    assert resp_get_after_put.status_code == 200, f"Expected 200, got {resp_get_after_put.status_code}: {resp_get_after_put.text}"
    fetched_updated = resp_get_after_put.json()["customers"][0]
    assert fetched_updated["firstname"] == "Johnny"

# --- id=1182  name='Customer Core Missing Phone Number Returns 500' ---
def test_customer_core_missing_phone_number_returns_500():
    # Negative test: missing phone number
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Test City",
        "email": f"jane.doe.{generate_random_string()}@example.com"
        # phoneNumber is intentionally omitted
    }
    create_url = get_url("customer-core", "/customers")
    resp = requests.post(create_url, json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1183  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    # 1. Signup
    email = f"user.{generate_random_string()}@example.com"
    password = "password123"
    signup_payload = {"email": email, "password": password}
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp_signup = requests.post(signup_url, json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    # 2. Login
    login_payload = {"email": email, "password": password}
    login_url = get_url("customer-self-service-backend", "/auth")
    resp_login = requests.post(login_url, json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json().get("token")
    assert token is not None

    auth_headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "Rabbit Hole 1",
        "postalCode": "12345",
        "phoneNumber": "555-9999"
    }
    reg_url = get_url("customer-self-service-backend", "/customers")
    resp_reg = requests.post(reg_url, json=reg_payload, headers=auth_headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json().get("customerId")
    assert customer_id is not None

    # 4. Verify user details
    user_url = get_url("customer-self-service-backend", "/user")
    resp_user = requests.get(user_url, headers=auth_headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    user_data = resp_user.json()
    assert user_data.get("customerId") == customer_id
    assert user_data.get("email") == email

    # 5. Create Insurance Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {
                "streetAddress": "Rabbit Hole 1",
                "postalCode": "12345",
                "city": "Wonderland"
            },
            "billingAddress": {
                "streetAddress": "Rabbit Hole 1",
                "postalCode": "12345",
                "city": "Wonderland"
            }
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    quote_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    resp_quote = requests.post(quote_url, json=quote_req_payload, headers=auth_headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json().get("id")
    assert quote_id is not None

    # 6. Verify quote request
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_get_quote = requests.get(get_quote_url, headers=auth_headers, timeout=10)
    assert resp_get_quote.status_code == 200, f"Expected 200, got {resp_get_quote.status_code}: {resp_get_quote.text}"
    fetched_quote = resp_get_quote.json()
    assert fetched_quote.get("id") == quote_id
    assert fetched_quote["customerInfo"]["customerId"] == customer_id

    # 7. Negative: Accept quote in REQUEST_SUBMITTED state (401)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    patch_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_patch = requests.patch(patch_quote_url, json=accept_payload, headers=auth_headers, timeout=10)
    assert resp_patch.status_code == 401, f"Expected 401, got {resp_patch.status_code}: {resp_patch.text}"

# --- id=1184  name='Policy Management Create Policy And Missing Customer' ---
def test_policy_management_create_policy_and_missing_customer():
    # 1. Create customer in customer-core
    payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "456 Build St",
        "postalCode": "67890",
        "city": "Builder City",
        "email": f"bob.{generate_random_string()}@example.com",
        "phoneNumber": "555-5678"
    }
    create_url = get_url("customer-core", "/customers")
    resp_cust = requests.post(create_url, json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json().get("customerId")

    # 2. Create policy in policy-management
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Fire", "description": "Fire coverage"}
            ]
        }
    }
    policy_url = get_url("policy-management-backend", "/policies")
    resp_pol = requests.post(policy_url, json=policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json().get("policyId")
    assert policy_id is not None

    # 3. Verify policy
    get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp_get_pol = requests.get(get_pol_url, headers=POLICY_HEADERS, timeout=10)
    assert resp_get_pol.status_code == 200, f"Expected 200, got {resp_get_pol.status_code}: {resp_get_pol.text}"
    fetched_pol = resp_get_pol.json()
    assert fetched_pol.get("policyId") == policy_id
    assert fetched_pol.get("customer") == customer_id
    assert fetched_pol.get("policyType") == "Home"

    # 4. Negative: Create policy for non-existent customer (424)
    bad_policy_payload = policy_payload.copy()
    bad_policy_payload["customerId"] = "non-existent-id-12345"
    resp_bad_pol = requests.post(policy_url, json=bad_policy_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp_bad_pol.status_code == 424, f"Expected 424, got {resp_bad_pol.status_code}: {resp_bad_pol.text}"

# --- id=1185  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    # 1. Create customer in customer-core
    payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "789 Silent Way",
        "postalCode": "13579",
        "city": "Hollywood",
        "email": f"charlie.{generate_random_string()}@example.com",
        "phoneNumber": "555-0000"
    }
    create_url = get_url("customer-core", "/customers")
    resp_cust = requests.post(create_url, json=payload, headers=CORE_HEADERS, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json().get("customerId")

    # 2. Get customer in customer-management
    get_cust_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp_get_cust = requests.get(get_cust_url, timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"
    assert resp_get_cust.json().get("customerId") == customer_id

    # 3. Negative: Acknowledge with empty lastAcknowledgedInteractionId (400)
    ack_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    bad_ack_payload = {"lastAcknowledgedInteractionId": ""}
    resp_bad_ack = requests.patch(ack_url, json=bad_ack_payload, timeout=10)
    assert resp_bad_ack.status_code == 400, f"Expected 400, got {resp_bad_ack.status_code}: {resp_bad_ack.text}"

    # 4. Negative: Acknowledge for customer with no log (404)
    valid_ack_payload = {"lastAcknowledgedInteractionId": "some-id-123"}
    resp_not_found_ack = requests.patch(ack_url, json=valid_ack_payload, timeout=10)
    assert resp_not_found_ack.status_code == 404, f"Expected 404, got {resp_not_found_ack.status_code}: {resp_not_found_ack.text}"

# --- id=1186  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    risk_payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    risk_url = get_url("policy-management-backend", "/riskfactor/compute")
    resp_risk = requests.post(risk_url, json=risk_payload, headers=POLICY_HEADERS, timeout=10)
    assert resp_risk.status_code == 200, f"Expected 200, got {resp_risk.status_code}: {resp_risk.text}"
    assert "riskFactor" in resp_risk.json()
