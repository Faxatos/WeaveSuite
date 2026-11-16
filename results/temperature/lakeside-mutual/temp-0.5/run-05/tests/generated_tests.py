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

def test_customer_self_service_signup_and_register_customer():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()
    
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}
    
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()
    
    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(reg_url, headers=headers, json=reg_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id
    
    cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp = requests.get(cust_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

def test_customer_self_service_insurance_quote_request_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    headers = {"X-Auth-Token": token}
    
    reg_payload = {
        "firstname": "Jane", "lastname": "Doe", "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich", "streetAddress": "Main St 1", "postalCode": "8000", "phoneNumber": "555-1234"
    }
    customer_id = requests.post(get_url("customer-self-service-backend", "/customers"), headers=headers, json=reg_payload, timeout=10).json()["customerId"]
    
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"},
            "billingAddress": {"streetAddress": "Main St 1", "postalCode": "8000", "city": "Zurich"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(quote_req_url, headers=headers, json=quote_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]
    
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id
    
    patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_quote_url, headers=headers, json=patch_payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_quote_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    
    success = False
    for _ in range(15):
        resp = requests.get(pm_quote_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            success = True
            break
        time.sleep(1)
    assert success, f"Quote request {quote_id} not found in policy-management-backend after polling"
    
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(pm_quote_url, headers=pm_headers, json=draft_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    success = False
    for _ in range(15):
        resp = requests.get(get_quote_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            history = [s["status"] for s in resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                success = True
                break
        time.sleep(1)
    assert success, "Quote request did not reach QUOTE_RECEIVED state in self-service-backend"
    
    resp = requests.patch(get_quote_url, headers=headers, json=patch_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = [s["status"] for s in resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in history

def test_policy_management_create_and_delete_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")
    cc_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 2",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(cc_url, headers=cc_headers, json=cc_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_url = get_url("policy-management-backend", "/policies")
    pm_payload = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp = requests.post(pm_url, headers=pm_headers, json=pm_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]
    
    get_url_pm = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp = requests.get(get_url_pm, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id
    
    resp = requests.delete(get_url_pm, headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url_pm, headers=pm_headers, timeout=10)
    assert resp.status_code != 200, f"Expected non-200 after deletion, got {resp.status_code}"

def test_policy_management_create_policy_missing_customer():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_url = get_url("policy-management-backend", "/policies")
    pm_payload = {
        "customerId": f"non-existent-{uuid.uuid4()}",
        "policyPeriod": {"startDate": "2024-01-01T00:00:00Z", "endDate": "2025-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp = requests.post(pm_url, headers=pm_headers, json=pm_payload, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

def test_customer_core_create_customer_missing_phone_number():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")
    cc_payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "Pine St 3",
        "postalCode": "5678",
        "city": "Bern",
        "email": f"bob_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(cc_url, headers=cc_headers, json=cc_payload, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

def test_customer_core_change_address():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")
    cc_payload = {
        "firstname": "David",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Old St 1",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"david_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    resp = requests.post(cc_url, headers=cc_headers, json=cc_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_payload = {
        "streetAddress": "New St 2",
        "postalCode": "2000",
        "city": "Neuchatel"
    }
    resp = requests.put(addr_url, headers=cc_headers, json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    get_url_cc = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_cc, headers=cc_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["streetAddress"] == "New St 2"
    assert resp.json()["customers"][0]["postalCode"] == "2000"
    assert resp.json()["customers"][0]["city"] == "Neuchatel"

def test_customer_management_acknowledge_interactions_empty_id():
    cm_url = get_url("customer-management-backend", "/interaction-logs/any-id")
    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(cm_url, json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_customer_management_acknowledge_interactions_not_found():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")
    cc_payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1992-02-02T00:00:00Z",
        "streetAddress": "Elm St 4",
        "postalCode": "4321",
        "city": "Basel",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(cc_url, headers=cc_headers, json=cc_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    payload = {"lastAcknowledgedInteractionId": "some-id"}
    resp = requests.patch(cm_url, json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_customer_management_get_interaction_log_empty():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_url = get_url("customer-core", "/customers")
    cc_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "First St 1",
        "postalCode": "1111",
        "city": "Zurich",
        "email": f"eve_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    resp = requests.post(cc_url, headers=cc_headers, json=cc_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.get(cm_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("interactions", []) == []

def test_policy_management_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_url = get_url("policy-management-backend", "/riskfactor/compute")
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(pm_url, headers=pm_headers, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
