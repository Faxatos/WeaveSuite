# Tests generated in iteration 09
# Captured: 2026-07-12T00:09:42
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=74  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    # Create customer
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00.000Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    # Get customer
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Update customer
    payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) > 0
    assert customers[0]["firstname"] == "Johnny"

    # Change address
    address_payload = {
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify address change
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_customer = resp.json().get("customers", [])[0]
    assert updated_customer["streetAddress"] == "456 Oak St"

# --- id=75  name='Customer Self Auth And Register' ---
def test_customer_self_service_auth_and_register():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "Password123!"

    # Signup
    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Register Customer
    register_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00.000Z",
        "city": "Wonderland",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=register_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Get User
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # Change Address
    address_payload = {
        "streetAddress": "2 Rabbit Hole",
        "postalCode": "12345",
        "city": "Wonderland"
    }
    resp = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Address Change via core
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    if resp.status_code == 200:
        customers = resp.json().get("customers", [])
        if customers:
            assert customers[0]["streetAddress"] == "2 Rabbit Hole"

# --- id=76  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    # Compute Risk Factor
    risk_payload = {
        "birthday": "1980-01-01T00:00:00.000Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

    # Create Policy
    policy_payload = {
        "customerId": "cust-" + str(uuid.uuid4()),
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00.000Z",
            "endDate": "2024-01-01T00:00:00.000Z"
        },
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Get Policy
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Life"

    # Update Policy
    policy_payload["policyType"] = "Health"
    resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Update
    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "Health"

    # Delete Policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Deletion
    resp = requests.get(get_url("policy-management-backend", "/policies"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=77  name='Cross Insurance Quote Request Workflow' ---
def test_cross_service_insurance_quote_request_workflow():
    # 1. Create Quote Request via Self-Service
    quote_request_payload = {
        "customerInfo": {
            "customerId": "cust-" + str(uuid.uuid4()),
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"streetAddress": "1 Build St", "postalCode": "12345", "city": "Buildtown"},
            "billingAddress": {"streetAddress": "1 Build St", "postalCode": "12345", "city": "Buildtown"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00.000Z",
            "insuranceType": "Home",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_request_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req_id = resp.json()["id"]

    # 2. Verify it appears in Policy Management
    resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Respond to Quote Request via Policy Management
    quote_response_payload = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00.000Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), json=quote_response_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Verify updated status in Self-Service
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert any(s.get("status") == "ACCEPTED" for s in status_history) or resp.json().get("insuranceQuote") is not None

    # 5. Customer accepts the quote via Self-Service
    customer_response_payload = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00.000Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), json=customer_response_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=78  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    # Create customer in core to ensure it exists
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1992-02-02T00:00:00.000Z",
        "streetAddress": "789 Pine St",
        "postalCode": "67890",
        "city": "Sometown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Get interaction logs in management backend
    resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    log_data = resp.json()

    # Acknowledge interactions
    ack_payload = {
        "lastAcknowledgedInteractionId": "interaction-123"
    }
    interactions = log_data.get("interactions", [])
    if interactions:
        ack_payload["lastAcknowledgedInteractionId"] = interactions[0]["id"]

    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify acknowledgment
    resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    if interactions:
        assert resp.json().get("lastAcknowledgedInteractionId") == ack_payload["lastAcknowledgedInteractionId"]

# --- id=79  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    # Create customer in core
    payload = {
        "firstname": "Mark",
        "lastname": "Twain",
        "birthday": "1835-11-30T00:00:00.000Z",
        "streetAddress": "123 Writer Way",
        "postalCode": "12345",
        "city": "Hannibal",
        "email": f"mark.twain.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    # Update customer in management backend
    update_payload = {
        "firstname": "Samuel",
        "lastname": "Clemens",
        "birthday": "1835-11-30T00:00:00.000Z",
        "email": payload["email"],
        "phoneNumber": "555-1111",
        "moveHistory": []
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update in core
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) > 0
    assert customers[0]["firstname"] == "Samuel"
    assert customers[0]["lastname"] == "Clemens"

# --- id=80  name='Customer Self Cities' ---
def test_customer_self_service_get_cities():
    postal_code = "12345"
    resp = requests.get(get_url("customer-self-service-backend", f"/cities/{postal_code}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=81  name='Policy Management Customer Policies' ---
def test_policy_management_customer_policies():
    # Create policy for a new customer
    customer_id = "cust-" + str(uuid.uuid4())
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00.000Z",
            "endDate": "2024-01-01T00:00:00.000Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Auto Coverage", "description": "Covers auto accidents"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    # Get policies for customer
    resp = requests.get(get_url("policy-management-backend", f"/customers/{customer_id}/policies"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json()
    assert isinstance(policies, list)
    assert any(p.get("policyId") == policy_id for p in policies)

# --- id=82  name='Customer Management Notifications' ---
def test_customer_management_notifications():
    resp = requests.get(get_url("customer-management-backend", "/notifications"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)
