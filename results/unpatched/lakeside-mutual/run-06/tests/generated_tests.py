# Tests generated in iteration 01
# Captured: 2026-07-12T09:10:01
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=90  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-15T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "20002",
        "city": "Washington",
        "email": email,
        "phoneNumber": "555-5678"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_data = resp.json()
    customer_id = customer_data.get("customerId")
    assert customer_id is not None

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customers = resp_get.json().get("customers", [])
    assert len(customers) > 0
    customer = customers[0]
    assert customer.get("firstname") == customer_payload["firstname"]
    assert customer.get("email") == customer_payload["email"]

    address_payload = {
        "streetAddress": "789 Oak St",
        "postalCode": "30003",
        "city": "Atlanta"
    }
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    updated_customer = resp_get2.json().get("customers", [])[0]
    assert updated_customer.get("streetAddress") == address_payload["streetAddress"]
    assert updated_customer.get("postalCode") == address_payload["postalCode"]
    assert updated_customer.get("city") == address_payload["city"]

# --- id=91  name='Customer Self Auth And Registration' ---
def test_customer_self_service_auth_and_registration():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    customer_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Main St",
        "postalCode": "10001",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=customer_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json().get("customerId") == customer_id

    resp_get = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("customerId") == customer_id

# --- id=92  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    email = f"policy_{uuid.uuid4().hex[:8]}@example.com"
    customer_payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1975-08-20T00:00:00Z",
        "streetAddress": "321 Pine St",
        "postalCode": "40004",
        "city": "Seattle",
        "email": email,
        "phoneNumber": "555-9012"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Main coverage"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json().get("policyId")
    assert policy_id is not None

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched_policy = resp_get.json()
    assert fetched_policy.get("policyType") == policy_payload["policyType"]
    assert fetched_policy.get("deductible", {}).get("amount") == policy_payload["deductible"]["amount"]

    policy_payload["policyType"] = "Health"
    policy_payload["deductible"]["amount"] = 1000
    resp_put = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=policy_payload, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    updated_policy = resp_get2.json()
    assert updated_policy.get("policyType") == "Health"
    assert updated_policy.get("deductible", {}).get("amount") == 1000

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_list = requests.get(get_url("policy-management-backend", "/policies"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    policies = resp_list.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies)

# --- id=93  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"quote_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    customer_payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1992-11-11T00:00:00Z",
        "city": "Chicago",
        "streetAddress": "111 Dogwood Ln",
        "postalCode": "50005",
        "phoneNumber": "555-3456"
    }
    resp_cust = requests.post(get_url("customer-self-service-backend", "/customers"), json=customer_payload, headers=headers, timeout=10)
    customer_id = resp_cust.json().get("customerId")

    quote_request_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Brown",
            "contactAddress": {
                "streetAddress": "111 Dogwood Ln",
                "postalCode": "50005",
                "city": "Chicago"
            },
            "billingAddress": {
                "streetAddress": "111 Dogwood Ln",
                "postalCode": "50005",
                "city": "Chicago"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 200, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_request_payload, headers=headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_req_id = resp_quote.json().get("id")
    assert quote_req_id is not None

    resp_get_quote = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers, timeout=10)
    assert resp_get_quote.status_code == 200, f"Expected 200, got {resp_get_quote.status_code}: {resp_get_quote.text}"
    assert resp_get_quote.json().get("id") == quote_req_id

    quote_response_payload = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_patch = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), json=quote_response_payload, timeout=10)
    assert resp_patch.status_code == 200, f"Expected 200, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_quote2 = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=headers, timeout=10)
    assert resp_get_quote2.status_code == 200, f"Expected 200, got {resp_get_quote2.status_code}: {resp_get_quote2.text}"
    updated_quote = resp_get_quote2.json()
    insurance_quote = updated_quote.get("insuranceQuote")
    if insurance_quote:
        assert insurance_quote.get("insurancePremium", {}).get("amount") == 150
        assert insurance_quote.get("policyLimit", {}).get("amount") == 50000

# --- id=94  name='Policy Management Risk Factor Computation' ---
def test_policy_management_risk_factor_computation():
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=95  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    email = f"diana_{uuid.uuid4().hex[:8]}@example.com"
    customer_payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1980-03-22T00:00:00Z",
        "streetAddress": "123 Themyscira Ave",
        "postalCode": "60006",
        "city": "Island",
        "email": email,
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    resp_logs = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp_logs.status_code == 200, f"Expected 200, got {resp_logs.status_code}: {resp_logs.text}"
    log_data = resp_logs.json()
    assert log_data.get("customerId") == customer_id

    interactions = log_data.get("interactions", [])
    if interactions:
        last_id = interactions[-1].get("id")
        ack_payload = {"lastAcknowledgedInteractionId": last_id}
        resp_ack = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload, timeout=10)
        assert resp_ack.status_code == 200, f"Expected 200, got {resp_ack.status_code}: {resp_ack.text}"

        resp_logs2 = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
        assert resp_logs2.status_code == 200, f"Expected 200, got {resp_logs2.status_code}: {resp_logs2.text}"
        assert resp_logs2.json().get("lastAcknowledgedInteractionId") == last_id

# --- id=96  name='Customer Core Cities' ---
def test_customer_core_get_cities():
    resp = requests.get(get_url("customer-core", "/cities/10001"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=97  name='Customer Management Notifications' ---
def test_customer_management_notifications():
    resp = requests.get(get_url("customer-management-backend", "/notifications"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)
