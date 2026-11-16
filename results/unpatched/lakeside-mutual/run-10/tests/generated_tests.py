# Tests generated in iteration 02
# Captured: 2026-07-12T09:40:49
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=102  name='Risk Factor Computation' ---
def test_risk_factor_computation():
    # 1. Compute Risk Factor
    payload = {
        "birthday": "1980-05-15T00:00:00Z",
        "postalCode": "12345"
    }
    url = get_url("policy-management-backend", "/riskfactor/compute")
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "riskFactor" in data
    assert isinstance(data["riskFactor"], int)

# --- id=98  name='Customer Core Lifecycle' ---
def test_customer_core_lifecycle():
    # 1. Create a new customer
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
    create_url = get_url("customer-core", "/customers")
    create_resp = requests.post(create_url, json=payload, timeout=10)
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"

    customer_data = create_resp.json()
    customer_id = customer_data.get("customerId")
    assert customer_id is not None
    assert customer_data.get("firstname") == payload["firstname"]

    # 2. Verify creation via GET
    get_url_path = get_url("customer-core", f"/customers/{customer_id}")
    get_resp = requests.get(get_url_path, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    get_data = get_resp.json()
    customers = get_data.get("customers", [])
    assert len(customers) > 0
    fetched_customer = customers[0]
    assert fetched_customer.get("customerId") == customer_id
    assert fetched_customer.get("streetAddress") == payload["streetAddress"]

    # 3. Update customer address
    addr_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_resp = requests.put(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    # 4. Verify address update via GET
    get_resp2 = requests.get(get_url_path, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    updated_customer = get_resp2.json().get("customers", [])[0]
    assert updated_customer.get("streetAddress") == addr_payload["streetAddress"]
    assert updated_customer.get("postalCode") == addr_payload["postalCode"]
    assert updated_customer.get("city") == addr_payload["city"]

# --- id=99  name='Self Auth Workflow' ---
def test_self_service_auth_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass123!"

    # 1. Signup
    signup_payload = {"email": email, "password": password}
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    signup_resp = requests.post(signup_url, json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json().get("email") == email

    # 2. Login
    login_payload = {"email": email, "password": password}
    login_url = get_url("customer-self-service-backend", "/auth")
    login_resp = requests.post(login_url, json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json().get("token")
    assert token is not None

    # 3. Verify User Details
    user_url = get_url("customer-self-service-backend", "/user")
    headers = {"Authorization": f"Bearer {token}"}
    user_resp = requests.get(user_url, headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json().get("email") == email

# --- id=100  name='Policy Management Lifecycle' ---
def test_policy_management_lifecycle():
    # 1. Create Policy
    payload = {
        "customerId": f"cust-{uuid.uuid4().hex[:8]}",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "policyType": "Life",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Basic Coverage"}
            ]
        }
    }
    create_url = get_url("policy-management-backend", "/policies")
    create_resp = requests.post(create_url, json=payload, timeout=10)
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"

    policy_data = create_resp.json()
    policy_id = policy_data.get("policyId")
    assert policy_id is not None

    # 2. Verify Create
    get_url_path = get_url("policy-management-backend", f"/policies/{policy_id}")
    get_resp = requests.get(get_url_path, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("policyType") == payload["policyType"]
    assert get_resp.json().get("deductible", {}).get("amount") == payload["deductible"]["amount"]

    # 3. Update Policy
    payload["policyType"] = "Health"
    payload["deductible"]["amount"] = 1000
    put_resp = requests.put(get_url_path, json=payload, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    # 4. Verify Update
    get_resp2 = requests.get(get_url_path, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json().get("policyType") == "Health"
    assert get_resp2.json().get("deductible", {}).get("amount") == 1000

    # 5. Delete Policy
    del_resp = requests.delete(get_url_path, timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

# --- id=101  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    # 1. Create Quote Request (Self-Service)
    payload = {
        "customerInfo": {
            "customerId": f"cust-{uuid.uuid4().hex[:8]}",
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"},
            "billingAddress": {"streetAddress": "123 Main St", "postalCode": "12345", "city": "Anytown"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    create_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    create_resp = requests.post(create_url, json=payload, timeout=10)
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"

    quote_data = create_resp.json()
    quote_id = quote_data.get("id")
    assert quote_id is not None

    # 2. Verify Create (Self-Service)
    get_url_path = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    get_resp = requests.get(get_url_path, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("insuranceOptions", {}).get("insuranceType") == "Auto"

    # 3. Update Status (Policy Management)
    patch_payload = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00Z",
        "insurancePremium": {"amount": 150, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    patch_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    patch_resp = requests.patch(patch_url, json=patch_payload, timeout=10)
    assert patch_resp.status_code == 200, f"Expected 200, got {patch_resp.status_code}: {patch_resp.text}"

    # 4. Verify Update (Self-Service)
    get_resp2 = requests.get(get_url_path, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    updated_data = get_resp2.json()
    assert "insuranceQuote" in updated_data
    assert updated_data["insuranceQuote"]["insurancePremium"]["amount"] == 150
    assert updated_data["insuranceQuote"]["policyLimit"]["amount"] == 50000
