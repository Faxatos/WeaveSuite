# Tests generated in iteration 01
# Captured: 2026-07-11T21:08:48
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    email = f"test_{random_string()}@example.com"
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": email,
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data.get("customerId")
    assert customer_id is not None
    assert data.get("email") == email

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_data = resp.json()
    customers = get_data.get("customers", [])
    assert len(customers) > 0
    assert customers[0].get("customerId") == customer_id
    assert customers[0].get("email") == email

    update_payload = payload.copy()
    update_payload["firstname"] = "Jane"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    update_data = resp.json()
    assert update_data.get("firstname") == "Jane"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_data = resp.json()
    customers = get_data.get("customers", [])
    assert len(customers) > 0
    assert customers[0].get("firstname") == "Jane"

# --- id=2  name='Customer Self Auth Flow' ---
def test_customer_self_service_auth_flow():
    email = f"user_{random_string()}@example.com"
    password = "password123"

    signup_payload = {
        "email": email,
        "password": password
    }
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    signup_data = resp.json()
    assert signup_data.get("email") == email

    login_payload = {
        "email": email,
        "password": password
    }
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    login_data = resp.json()
    token = login_data.get("token")
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_data = resp.json()
    assert user_data.get("email") == email

# --- id=3  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    email = f"test_{random_string()}@example.com"
    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": email,
        "phoneNumber": "555-5678"
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
        "deductible": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 10000,
            "currency": "USD"
        },
        "insurancePremium": {
            "amount": 100,
            "currency": "USD"
        },
        "insuringAgreement": {
            "agreementItems": [
                {
                    "title": "Coverage A",
                    "description": "Main coverage"
                }
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_data = resp.json()
    policy_id = policy_data.get("policyId")
    assert policy_id is not None
    assert policy_data.get("policyType") == "Life"

    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_data = resp.json()
    assert get_data.get("policyId") == policy_id
    assert get_data.get("policyType") == "Life"

    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=4  name='Customer Self Insurance Quote' ---
def test_customer_self_service_insurance_quote():
    email = f"test_{random_string()}@example.com"
    customer_payload = {
        "firstname": "Bob",
        "lastname": "Brown",
        "birthday": "1980-10-10T00:00:00Z",
        "streetAddress": "789 Oak St",
        "postalCode": "67890",
        "city": "Sometown",
        "email": email,
        "phoneNumber": "555-9012"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Brown",
            "contactAddress": {
                "streetAddress": "789 Oak St",
                "postalCode": "67890",
                "city": "Sometown"
            },
            "billingAddress": {
                "streetAddress": "789 Oak St",
                "postalCode": "67890",
                "city": "Sometown"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_data = resp.json()
    quote_id = quote_data.get("id")
    assert quote_id is not None

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_data = resp.json()
    assert get_data.get("id") == quote_id

    patch_payload = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {
            "amount": 100,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 10000,
            "currency": "USD"
        }
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=patch_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_data = resp.json()
    status_history = updated_data.get("statusHistory", [])
    if status_history:
        statuses = [s.get("status") for s in status_history]
        assert "ACCEPTED" in statuses

# --- id=5  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "riskFactor" in data

# --- id=6  name='Customer Management Customers' ---
def test_customer_management_get_customers():
    resp = requests.get(get_url("customer-management-backend", "/customers?limit=5"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "customers" in data
    assert isinstance(data["customers"], list)

# --- id=7  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    email = f"test_{random_string()}@example.com"
    payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "11111",
        "city": "London",
        "email": email,
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    address_payload = {
        "streetAddress": "2 Hollywood Blvd",
        "postalCode": "90210",
        "city": "Los Angeles"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_data = resp.json()
    customers = get_data.get("customers", [])
    assert len(customers) > 0
    assert customers[0].get("streetAddress") == "2 Hollywood Blvd"
    assert customers[0].get("city") == "Los Angeles"
    assert customers[0].get("postalCode") == "90210"

# --- id=8  name='Customer Self Register Customer' ---
def test_customer_self_service_register_customer():
    payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Themyscira",
        "streetAddress": "1 Palace Way",
        "postalCode": "00001",
        "phoneNumber": "555-7777"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data.get("customerId")
    assert customer_id is not None

    resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_data = resp.json()
    assert get_data.get("customerId") == customer_id

# --- id=9  name='Cities Reference Data' ---
def test_cities_reference_data():
    postal_code = "12345"
    resp = requests.get(get_url("customer-core", f"/cities/{postal_code}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "cities" in data
    assert isinstance(data["cities"], list)

# --- id=10  name='Customer Management Interaction Log' ---
def test_customer_management_interaction_log():
    email = f"test_{random_string()}@example.com"
    payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "123 Eden St",
        "postalCode": "11111",
        "city": "Paradise",
        "email": email,
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("customerId") == customer_id
    assert "interactions" in data

# --- id=11  name='Policy Management Insurance Quote Requests' ---
def test_policy_management_insurance_quote_requests():
    resp = requests.get(get_url("policy-management-backend", "/insurance-quote-requests"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert isinstance(data, list)

# --- id=12  name='Customer Management Notifications' ---
def test_customer_management_notifications():
    resp = requests.get(get_url("customer-management-backend", "/notifications"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert isinstance(data, list)
