# Tests generated in iteration 02
# Captured: 2026-07-11T21:44:47
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=17  name='Customer Management Interaction Log' ---
def test_customer_management_interaction_log():
    # 1. Create customer in core
    customer_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-10-10T00:00:00Z",
        "streetAddress": "999 Construction Way",
        "postalCode": "22222",
        "city": "Buildtown",
        "email": f"bob.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9999"
    }
    url_cust = get_url("customer-core", "/customers")
    resp_cust = requests.post(url_cust, json=customer_data, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    # 2. Get interaction log in management backend
    url_log = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp_log = requests.get(url_log, timeout=10)
    assert resp_log.status_code == 200, f"Expected 200, got {resp_log.status_code}: {resp_log.text}"
    log_data = resp_log.json()
    assert log_data["customerId"] == customer_id

    # 3. Acknowledge interactions
    ack_data = {
        "lastAcknowledgedInteractionId": "interaction-0"
    }
    resp_ack = requests.patch(url_log, json=ack_data, timeout=10)
    assert resp_ack.status_code == 200, f"Expected 200, got {resp_ack.status_code}: {resp_ack.text}"

# --- id=13  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    # 1. Create customer
    customer_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "New York",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    created_customer = resp.json()
    customer_id = created_customer["customerId"]
    assert created_customer["firstname"] == "John"

    # 2. Get customer
    url_get = get_url("customer-core", f"/customers/{customer_id}")
    resp_get = requests.get(url_get, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched_customer = resp_get.json()
    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["city"] == "New York"

    # 3. Update address
    new_address = {
        "streetAddress": "456 Elm St",
        "postalCode": "54321",
        "city": "Boston"
    }
    url_addr = get_url("customer-core", f"/customers/{customer_id}/address")
    resp_addr = requests.put(url_addr, json=new_address, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    # 4. Verify address update
    resp_get2 = requests.get(url_get, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    fetched_customer2 = resp_get2.json()
    assert fetched_customer2["city"] == "Boston"
    assert fetched_customer2["postalCode"] == "54321"
    assert fetched_customer2["streetAddress"] == "456 Elm St"

# --- id=14  name='Insurance Quote Workflow' ---
def test_insurance_quote_workflow():
    # 1. Register customer via self-service
    customer_data = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "789 Oak St",
        "postalCode": "67890",
        "city": "Chicago",
        "phoneNumber": "555-5678"
    }
    url_reg = get_url("customer-self-service-backend", "/customers")
    resp_reg = requests.post(url_reg, json=customer_data, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    # 2. Create insurance quote request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {
                "streetAddress": "789 Oak St",
                "postalCode": "67890",
                "city": "Chicago"
            },
            "billingAddress": {
                "streetAddress": "789 Oak St",
                "postalCode": "67890",
                "city": "Chicago"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    url_quote = get_url("customer-self-service-backend", "/insurance-quote-requests")
    resp_quote = requests.post(url_quote, json=quote_req_data, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json()["id"]

    # 3. Policy management responds to quote
    quote_resp_data = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T23:59:59Z",
        "insurancePremium": {
            "amount": 100,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        }
    }
    url_quote_resp = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    resp_quote_resp = requests.patch(url_quote_resp, json=quote_resp_data, timeout=10)
    assert resp_quote_resp.status_code == 200, f"Expected 200, got {resp_quote_resp.status_code}: {resp_quote_resp.text}"

    # 4. Verify quote status in self-service
    url_quote_get = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_quote_get = requests.get(url_quote_get, timeout=10)
    assert resp_quote_get.status_code == 200, f"Expected 200, got {resp_quote_get.status_code}: {resp_quote_get.text}"
    fetched_quote = resp_quote_get.json()
    assert fetched_quote["id"] == quote_id

# --- id=15  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    # 1. Create customer in core
    customer_data = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "123 Fantasy Ln",
        "postalCode": "11111",
        "city": "Dreamland",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    url_cust = get_url("customer-core", "/customers")
    resp_cust = requests.post(url_cust, json=customer_data, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    # 2. Compute risk factor
    risk_data = {
        "birthday": "1992-02-02T00:00:00Z",
        "postalCode": "11111"
    }
    url_risk = get_url("policy-management-backend", "/riskfactor/compute")
    resp_risk = requests.post(url_risk, json=risk_data, timeout=10)
    assert resp_risk.status_code == 200, f"Expected 200, got {resp_risk.status_code}: {resp_risk.text}"
    assert "riskFactor" in resp_risk.json()

    # 3. Create policy
    policy_data = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Health",
        "deductible": {
            "amount": 200,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 50000,
            "currency": "USD"
        },
        "insurancePremium": {
            "amount": 150,
            "currency": "USD"
        },
        "insuringAgreement": {
            "agreementItems": [
                {
                    "title": "Coverage A",
                    "description": "General coverage"
                }
            ]
        }
    }
    url_pol = get_url("policy-management-backend", "/policies")
    resp_pol = requests.post(url_pol, json=policy_data, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy_id = resp_pol.json()["policyId"]

    # 4. Get policy
    url_pol_get = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp_pol_get = requests.get(url_pol_get, timeout=10)
    assert resp_pol_get.status_code == 200, f"Expected 200, got {resp_pol_get.status_code}: {resp_pol_get.text}"
    assert resp_pol_get.json()["policyId"] == policy_id

    # 5. Delete policy
    resp_pol_del = requests.delete(url_pol_get, timeout=10)
    assert resp_pol_del.status_code == 200, f"Expected 200, got {resp_pol_del.status_code}: {resp_pol_del.text}"

# --- id=16  name='Customer Self Auth And User' ---
def test_customer_self_service_auth_and_user():
    # 1. Signup
    email = f"user.{uuid.uuid4()}@example.com"
    password = "SecurePassword123!"
    signup_data = {
        "email": email,
        "password": password
    }
    url_signup = get_url("customer-self-service-backend", "/auth/signup")
    resp_signup = requests.post(url_signup, json=signup_data, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    # 2. Login
    login_data = {
        "email": email,
        "password": password
    }
    url_login = get_url("customer-self-service-backend", "/auth")
    resp_login = requests.post(url_login, json=login_data, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json().get("token")

    # 3. Get current user
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url_user = get_url("customer-self-service-backend", "/user")
    resp_user = requests.get(url_user, headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json()["email"] == email
