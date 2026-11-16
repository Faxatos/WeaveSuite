# Tests generated in iteration 04
# Captured: 2026-07-11T22:19:49
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=34  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    email = f"addr_{random_string()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    reg_payload = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1975-11-11T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Safehouse",
        "postalCode": "10002",
        "phoneNumber": "555-9999"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    customer_id = reg_resp.json().get("customerId")

    new_address = {
        "streetAddress": "456 New Safehouse",
        "postalCode": "10003",
        "city": "New York"
    }
    addr_resp = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), json=new_address, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    assert addr_resp.json().get("streetAddress") == "456 New Safehouse"

# --- id=35  name='Policy Management Customer Policies' ---
def test_policy_management_customer_policies():
    customer_id = str(uuid.uuid4())
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "policyType": "Home",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 300000, "currency": "USD"},
        "insurancePremium": {"amount": 800, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Fire", "description": "Covers fire damage"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("policy-management-backend", f"/customers/{customer_id}/policies"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json()
    assert isinstance(policies, list)
    assert len(policies) > 0
    assert policies[0].get("policyType") == "Home"

# --- id=36  name='Customer Management Notifications' ---
def test_customer_management_notifications():
    resp = requests.get(get_url("customer-management-backend", "/notifications"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)

# --- id=37  name='Policy Management Policies' ---
def test_policy_management_get_policies():
    resp = requests.get(get_url("policy-management-backend", "/policies?limit=5"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "policies" in resp.json()

# --- id=38  name='Customer Core Customers' ---
def test_customer_core_get_customers():
    resp = requests.get(get_url("customer-core", "/customers?limit=5"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customers" in resp.json()

# --- id=28  name='Customer Self Workflow' ---
def test_customer_self_service_workflow():
    email = f"test_{random_string()}@example.com"
    password = "Password123!"
    signup_payload = {"email": email, "password": password}

    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    auth_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=auth_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "New York",
        "streetAddress": "123 Main St",
        "postalCode": "10001",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("email") == email

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "10001", "city": "New York"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "10001", "city": "New York"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json().get("id")
    assert quote_id is not None

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == quote_id

# --- id=29  name='Customer Core Workflow' ---
def test_customer_core_workflow():
    base_url = get_url("customer-core", "/customers")
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "20002",
        "city": "Washington",
        "email": f"alice_{random_string()}@example.com",
        "phoneNumber": "555-5678"
    }
    resp = requests.post(base_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer.get("customerId")

    self_link = customer.get("_links", {}).get("self", {}).get("href")
    customer_url = self_link if self_link else f"{base_url}/{customer_id}"

    payload["firstname"] = "Alicia"
    resp = requests.put(customer_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_payload = {
        "streetAddress": "789 Oak St",
        "postalCode": "30003",
        "city": "Atlanta"
    }
    address_url = f"{customer_url}/address"
    resp = requests.put(address_url, json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(customer_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) > 0
    updated_customer = customers[0]
    assert updated_customer.get("firstname") == "Alicia"
    assert updated_customer.get("city") == "Atlanta"

# --- id=30  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    risk_payload = {
        "birthday": "1980-10-10T00:00:00Z",
        "postalCode": "40004"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

    policy_payload = {
        "customerId": str(uuid.uuid4()),
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Collision", "description": "Covers collision damage"}
            ]
        }
    }
    base_url = get_url("policy-management-backend", "/policies")
    resp = requests.post(base_url, json=policy_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()

    self_link = policy.get("_links", {}).get("self", {}).get("href")
    policy_url = self_link if self_link else f"{base_url}/{policy.get('policyId')}"

    resp = requests.get(policy_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("policyId") == policy.get("policyId")

    resp = requests.delete(policy_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=31  name='Customer Management Workflow' ---
def test_customer_management_workflow():
    core_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1900-01-01T00:00:00Z",
        "streetAddress": "1 Hollywood Blvd",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": f"charlie_{random_string()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=core_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    cm_base = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp = requests.get(cm_base, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    update_payload = {
        "firstname": "Charles",
        "lastname": "Chaplin",
        "birthday": "1900-01-01T00:00:00Z",
        "email": core_payload["email"],
        "phoneNumber": "555-0001",
        "moveHistory": []
    }
    resp = requests.put(cm_base, json=update_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.get(log_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    log_data = resp.json()

    interactions = log_data.get("interactions", [])
    if interactions:
        last_id = interactions[-1].get("id")
        ack_payload = {"lastAcknowledgedInteractionId": last_id}
        resp = requests.patch(log_url, json=ack_payload, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=32  name='Cross Insurance Quote Workflow' ---
def test_cross_service_insurance_quote_workflow():
    email = f"quote_{random_string()}@example.com"
    password = "Password123!"
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    reg_payload = {
        "firstname": "David",
        "lastname": "Tennant",
        "birthday": "1971-04-18T00:00:00Z",
        "city": "London",
        "streetAddress": "100 Police Box",
        "postalCode": "SW1A 1AA",
        "phoneNumber": "07700900000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json().get("customerId")

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "David",
            "lastname": "Tennant",
            "contactAddress": {"streetAddress": "100 Police Box", "postalCode": "SW1A 1AA", "city": "London"},
            "billingAddress": {"streetAddress": "100 Police Box", "postalCode": "SW1A 1AA", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "TimeTravel",
            "deductible": {"amount": 100, "currency": "GBP"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json().get("id")

    pm_get_resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), timeout=10)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"

    quote_response_payload = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "GBP"},
        "policyLimit": {"amount": 1000000, "currency": "GBP"}
    }
    pm_patch_resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=quote_response_payload, timeout=10)
    assert pm_patch_resp.status_code == 200, f"Expected 200, got {pm_patch_resp.status_code}: {pm_patch_resp.text}"

    customer_response_payload = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T23:59:59Z",
        "insurancePremium": {"amount": 500, "currency": "GBP"},
        "policyLimit": {"amount": 1000000, "currency": "GBP"}
    }
    ss_patch_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=customer_response_payload, headers=headers, timeout=10)
    assert ss_patch_resp.status_code == 200, f"Expected 200, got {ss_patch_resp.status_code}: {ss_patch_resp.text}"

    final_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert final_get.status_code == 200, f"Expected 200, got {final_get.status_code}: {final_get.text}"

# --- id=33  name='Cities Reference Data' ---
def test_cities_reference_data():
    postal_code = "10001"
    resp = requests.get(get_url("customer-core", f"/cities/{postal_code}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

    resp2 = requests.get(get_url("customer-self-service-backend", f"/cities/{postal_code}"), timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert "cities" in resp2.json()
