# Tests generated in iteration 03
# Captured: 2026-07-11T21:47:08
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=18  name='Customer Self Signup And Login' ---
def test_customer_self_service_signup_and_login():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    user_data = resp.json()
    assert user_data["email"] == email

    login_payload = {"email": email, "password": password}
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    token = resp.json().get("token")
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

# --- id=19  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    create_url = get_url("customer-core", "/customers")
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(create_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    get_url_str = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_str, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    update_url = get_url("customer-core", f"/customers/{customer_id}")
    payload["firstname"] = "Johnny"
    resp = requests.put(update_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url_str, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers_resp = resp.json()
    assert len(customers_resp["customers"]) > 0
    assert customers_resp["customers"][0]["firstname"] == "Johnny"

# --- id=20  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    create_url = get_url("customer-core", "/customers")
    payload = {
        "firstname": "David",
        "lastname": "Bowie",
        "birthday": "1947-01-08T00:00:00Z",
        "streetAddress": "123 Music St",
        "postalCode": "12345",
        "city": "London",
        "email": f"david.bowie.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(create_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "456 New Music St",
        "postalCode": "67890",
        "city": "New York"
    }
    resp = requests.put(addr_url, json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    get_url_str = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_str, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers_resp = resp.json()
    assert len(customers_resp["customers"]) > 0
    updated_customer = customers_resp["customers"][0]
    assert updated_customer["streetAddress"] == "456 New Music St"
    assert updated_customer["city"] == "New York"
    assert updated_customer["postalCode"] == "67890"

# --- id=21  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    create_url = get_url("policy-management-backend", "/policies")
    payload = {
        "customerId": f"cust-{uuid.uuid4().hex[:8]}",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    resp = requests.post(create_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    policy = resp.json()
    policy_id = policy["policyId"]

    get_url_str = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_url_str, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id

    delete_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.delete(delete_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=22  name='Policy Management Create Policy Boundary Values' ---
def test_policy_management_create_policy_boundary_values():
    create_url = get_url("policy-management-backend", "/policies")
    payload = {
        "customerId": f"cust-{uuid.uuid4().hex[:8]}",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 0, "currency": "USD"},
        "policyLimit": {"amount": 999999999999, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    resp = requests.post(create_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    policy = resp.json()
    policy_id = policy["policyId"]

    get_url_str = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_url_str, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["deductible"]["amount"] == 0
    assert resp.json()["policyLimit"]["amount"] == 999999999999

# --- id=23  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    create_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    payload = {
        "customerInfo": {
            "customerId": f"cust-{uuid.uuid4().hex[:8]}",
            "firstname": "Jane",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "123 Main", "postalCode": "12345", "city": "City"},
            "billingAddress": {"streetAddress": "123 Main", "postalCode": "12345", "city": "City"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    resp = requests.post(create_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    quote_req = resp.json()
    quote_id = quote_req["id"]

    get_url_str = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_url_str, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id

    respond_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    respond_payload = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp = requests.patch(respond_url, json=respond_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url_str, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    if status_history:
        statuses = [s.get("status") for s in status_history]
        assert "ACCEPTED" in statuses

# --- id=24  name='Customer Management Interactions' ---
def test_customer_management_interactions():
    core_create_url = get_url("customer-core", "/customers")
    core_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildtown",
        "email": f"bob.builder.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(core_create_url, json=core_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    cm_put_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    cm_put_payload = {
        "firstname": "Bob Updated",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "email": core_payload["email"],
        "phoneNumber": "555-2222",
        "moveHistory": []
    }
    put_resp = requests.put(cm_put_url, json=cm_put_payload, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    logs_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    logs_resp = requests.get(logs_url, timeout=10)
    assert logs_resp.status_code == 200, f"Expected 200, got {logs_resp.status_code}: {logs_resp.text}"

    logs_data = logs_resp.json()
    if logs_data.get("interactions") and len(logs_data["interactions"]) > 0:
        interaction_id = logs_data["interactions"][0]["id"]

        ack_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
        ack_payload = {"lastAcknowledgedInteractionId": interaction_id}
        ack_resp = requests.patch(ack_url, json=ack_payload, timeout=10)
        assert ack_resp.status_code == 200, f"Expected 200, got {ack_resp.status_code}: {ack_resp.text}"
        assert ack_resp.json().get("lastAcknowledgedInteractionId") == interaction_id

# --- id=25  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    url = get_url("policy-management-backend", "/riskfactor/compute")
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=26  name='Customer Self Cities' ---
def test_customer_self_service_get_cities():
    postal_code = "12345"
    url = get_url("customer-self-service-backend", f"/cities/{postal_code}")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=27  name='Customer Self Register Customer' ---
def test_customer_self_service_register_customer():
    url = get_url("customer-self-service-backend", "/customers")
    payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Cinema St",
        "postalCode": "NW1",
        "phoneNumber": "123456789"
    }
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    customer = resp.json()
    customer_id = customer["customerId"]

    get_url_str = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(get_url_str, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
