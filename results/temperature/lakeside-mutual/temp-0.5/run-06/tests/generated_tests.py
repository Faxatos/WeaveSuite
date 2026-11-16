import pytest
import requests
import uuid
import time
from urllib.parse import urljoin

MICROSERVICES = {
    "customer-core": "http://customer-core.default.svc.cluster.local:8110",
    "customer-management-backend": "http://customer-management-backend.default.svc.cluster.local:8100",
    "customer-self-service-backend": "http://customer-self-service-backend.default.svc.cluster.local:8080",
    "policy-management-backend": "http://policy-management-backend.default.svc.cluster.local:8090",
}

def get_url(service: str, path: str) -> str:
    base = MICROSERVICES.get(service)
    if not base:
        raise ValueError(f"Service {service} not found")
    return urljoin(base, path)

# --- Tests ---

def test_insurance_quote_workflow():
    # 1. Signup user on self-service
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # 2. Login user to get token
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}
    
    # 3. Register Customer
    reg_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    
    # Verify Customer creation via GET /user
    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
    
    # 4. Create Quote Request
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"},
            "billingAddress": {"city": "Zurich", "postalCode": "8000", "streetAddress": "Main St 1"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_req = resp.json()
    quote_id = quote_req["id"]
    
    # Verify Quote Request created
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_quote = resp.json()
    assert fetched_quote["customerInfo"]["customerId"] == customer_id
    assert fetched_quote["insuranceOptions"]["insuranceType"] == "Life"
    
    # 5. Back-office polls for quote request
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # 6. Back-office drafts response
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # 7. Self-service polls for QUOTE_RECEIVED
    for _ in range(15):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
        if resp.status_code == 200:
            status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in status_history:
                break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in status_history
    
    # 8. Self-service accepts quote
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_data, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify final status
    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in status_history

def test_customer_self_service_illegal_status_transition():
    # Establish realistic context: Create a quote request in REQUEST_SUBMITTED state
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}
    
    reg_data = {
        "firstname": "Jane",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Bern",
        "streetAddress": "Main St 2",
        "postalCode": "3000",
        "phoneNumber": "555-4321"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers, timeout=10)
    customer_id = resp.json()["customerId"]
    
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Smith",
            "contactAddress": {"city": "Bern", "postalCode": "3000", "streetAddress": "Main St 2"},
            "billingAddress": {"city": "Bern", "postalCode": "3000", "streetAddress": "Main St 2"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    quote_id = resp.json()["id"]
    
    # Trigger error: Try to accept immediately (illegal transition from REQUEST_SUBMITTED)
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_data, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_customer_core_missing_phone_number():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Build St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"bob_{uuid.uuid4()}@example.com"
        # Missing phoneNumber intentionally to trigger 500
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

def test_interaction_log_acknowledgement_validation():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1995-01-01T00:00:00Z",
        "streetAddress": "Wonder St 1",
        "postalCode": "2000",
        "city": "Neuchatel",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    customer_id = resp.json()["customerId"]
    
    # Empty lastAcknowledgedInteractionId -> 400
    ack_data_invalid = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_data_invalid, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_customer_core_update_and_verify():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "Comedy St 1",
        "postalCode": "1000",
        "city": "Vevey",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    
    # Update customer
    update_data = customer_data.copy()
    update_data["streetAddress"] = "Comedy St 2"
    update_data["city"] = "Geneva"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_data, headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify update
    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    resp_data = resp.json()
    updated_customer = resp_data["customers"][0] if "customers" in resp_data else resp_data
    assert updated_customer["firstname"] == "Charlie"
    assert updated_customer["streetAddress"] == "Comedy St 2"
    assert updated_customer["city"] == "Geneva"
    assert updated_customer["email"] == update_data["email"]
    assert "phoneNumber" in updated_customer

def test_policy_management_create_and_get_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    
    # Create customer
    customer_data = {
        "firstname": "David",
        "lastname": "Bowie",
        "birthday": "1947-01-08T00:00:00Z",
        "streetAddress": "Space Oddity 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"david_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    customer_id = resp.json()["customerId"]
    
    # Create policy
    policy_data = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    policy_id = policy["policyId"]
    
    # Verify policy creation using self link if available
    href = policy.get("_links", {}).get("self", {}).get("href")
    if href:
        policy_url = href if href.startswith("http") else get_url("policy-management-backend", href)
        resp = requests.get(policy_url, headers=pm_headers, timeout=10)
    else:
        resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_policy = resp.json()
    assert fetched_policy["policyId"] == policy_id
    assert fetched_policy["customer"] == customer_id
    assert fetched_policy["policyType"] == "Life"
    assert fetched_policy["deductible"]["amount"] == 500
    assert fetched_policy["policyLimit"]["amount"] == 100000
    assert fetched_policy["insurancePremium"]["amount"] == 100

def test_policy_management_delete_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    
    # Create customer
    customer_data = {
        "firstname": "Eve",
        "lastname": "Polastri",
        "birthday": "1985-01-01T00:00:00Z",
        "streetAddress": "Spy St 1",
        "postalCode": "1000",
        "city": "London",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    customer_id = resp.json()["customerId"]
    
    # Create policy
    policy_data = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"},
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Item 1", "description": "Desc 1"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=pm_headers, timeout=10)
    policy_id = resp.json()["policyId"]
    
    # Delete policy
    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"
    
    # Verify deletion by listing policies
    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert not any(p["policyId"] == policy_id for p in policies)

def test_policy_management_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_data = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

def test_customer_management_update_customer():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Punish St 1",
        "postalCode": "1000",
        "city": "New York",
        "email": f"frank_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4444"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    customer_id = resp.json()["customerId"]
    
    update_data = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1980-01-01T00:00:00Z",
        "email": f"frank_updated_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5555",
        "moveHistory": [{"streetAddress": "Punish St 2", "postalCode": "1001", "city": "New York"}]
    }
    resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify update
    resp = requests.get(get_url("customer-management-backend", f"/customers/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
