# Tests generated in iteration 07
# Captured: 2026-07-11T23:37:32
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=61  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    # Create customer
    customer_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Sample City",
        "email": random_email(),
        "phoneNumber": "555-1234"
    }
    create_url = get_url("customer-core", "/customers")
    resp = requests.post(create_url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    created_customer = resp.json()
    customer_id = created_customer.get("customerId")
    assert customer_id is not None

    # Get customer
    get_url_path = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_path, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_customer = resp.json()
    assert "customers" in fetched_customer
    assert len(fetched_customer["customers"]) > 0
    assert fetched_customer["customers"][0]["customerId"] == customer_id
    assert fetched_customer["customers"][0]["firstname"] == "John"

    # Update customer address
    new_address = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "New City"
    }
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    resp = requests.put(addr_url, json=new_address, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify address update
    resp = requests.get(get_url_path, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_customer = resp.json()
    cust = fetched_customer["customers"][0]
    assert cust["streetAddress"] == "456 New St"
    assert cust["postalCode"] == "54321"
    assert cust["city"] == "New City"

# --- id=62  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    session = requests.Session()
    email = random_email()
    password = "Password123!"

    # Signup
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    signup_data = {"email": email, "password": password}
    resp = session.post(signup_url, json=signup_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = session.post(login_url, json=signup_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})

    # Register Customer Profile
    register_url = get_url("customer-self-service-backend", "/customers")
    reg_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "789 Rabbit Hole",
        "postalCode": "98765",
        "phoneNumber": "555-9876"
    }
    resp = session.post(register_url, json=reg_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    # Get User to verify customerId is linked
    user_url = get_url("customer-self-service-backend", "/user")
    resp = session.get(user_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

    # Create Insurance Quote Request
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {
                "streetAddress": "789 Rabbit Hole",
                "postalCode": "98765",
                "city": "Wonderland"
            },
            "billingAddress": {
                "streetAddress": "789 Rabbit Hole",
                "postalCode": "98765",
                "city": "Wonderland"
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
    resp = session.post(quote_req_url, json=quote_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json().get("id")
    assert quote_id is not None

    # Get Insurance Quote Request
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = session.get(get_quote_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == quote_id

# --- id=63  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    # Compute Risk Factor
    risk_url = get_url("policy-management-backend", "/riskfactor/compute")
    risk_data = {
        "birthday": "1980-10-10T00:00:00Z",
        "postalCode": "10001"
    }
    resp = requests.post(risk_url, json=risk_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

    # Create Policy
    policy_url = get_url("policy-management-backend", "/policies")
    policy_data = {
        "customerId": str(uuid.uuid4()),
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    resp = requests.post(policy_url, json=policy_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json().get("policyId")
    assert policy_id is not None

    # Get Policy
    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_policy_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyId") == policy_id
    assert resp.json().get("policyType") == "Auto"

    # Update Policy
    policy_data["policyType"] = "Home"
    resp = requests.put(get_policy_url, json=policy_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Update
    resp = requests.get(get_policy_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyType") == "Home"

    # Delete Policy
    resp = requests.delete(get_policy_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=64  name='Cross Quote Processing' ---
def test_cross_service_quote_processing():
    session = requests.Session()
    email = random_email()
    password = "Password123!"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    session.post(signup_url, json={"email": email, "password": password}, timeout=10)

    login_url = get_url("customer-self-service-backend", "/auth")
    resp = session.post(login_url, json={"email": email, "password": password}, timeout=10)
    token = resp.json().get("token")
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1975-05-05T00:00:00Z",
        "city": "Construction City",
        "streetAddress": "123 Build St",
        "postalCode": "11111",
        "phoneNumber": "555-0000"
    }
    resp = session.post(reg_url, json=reg_data, timeout=10)
    customer_id = resp.json().get("customerId")

    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {
                "streetAddress": "123 Build St",
                "postalCode": "11111",
                "city": "Construction City"
            },
            "billingAddress": {
                "streetAddress": "123 Build St",
                "postalCode": "11111",
                "city": "Construction City"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Health",
            "deductible": {
                "amount": 200,
                "currency": "USD"
            }
        }
    }
    resp = session.post(quote_req_url, json=quote_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json().get("id")

    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(pm_quote_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    pm_patch_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    patch_data = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T23:59:59Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(pm_patch_url, json=patch_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    css_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = session.get(css_quote_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_resp = resp.json()
    status_history = quote_resp.get("statusHistory", [])
    assert len(status_history) > 0, "Expected status history to be updated"

# --- id=65  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    customer_data = {
        "firstname": "Eve",
        "lastname": "Hacker",
        "birthday": "1999-09-09T00:00:00Z",
        "streetAddress": "999 Cyber Blvd",
        "postalCode": "10101",
        "city": "Tech City",
        "email": random_email(),
        "phoneNumber": "555-9999"
    }
    create_url = get_url("customer-core", "/customers")
    resp = requests.post(create_url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    logs_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.get(logs_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    logs_data = resp.json()
    assert logs_data.get("customerId") == customer_id

    interactions = logs_data.get("interactions", [])
    if interactions:
        interaction_id = interactions[0].get("id")
        ack_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
        ack_data = {"lastAcknowledgedInteractionId": interaction_id}
        resp = requests.patch(ack_url, json=ack_data, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json().get("lastAcknowledgedInteractionId") == interaction_id

# --- id=66  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    customer_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Hollywood Blvd",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": random_email(),
        "phoneNumber": "555-0001"
    }
    create_url = get_url("customer-core", "/customers")
    resp = requests.post(create_url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    update_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    update_data = {
        "firstname": "Charles",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "email": customer_data["email"],
        "phoneNumber": "555-0002",
        "moveHistory": []
    }
    resp = requests.put(update_url, json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    get_url_path = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp = requests.get(get_url_path, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

# --- id=67  name='Customer Core Cities' ---
def test_customer_core_get_cities():
    url = get_url("customer-core", "/cities/12345")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()
