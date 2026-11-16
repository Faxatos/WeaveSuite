import pytest
import requests
import uuid
import random
import string
from urllib.parse import urljoin
import time

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

def test_customer_self_service_backend_registration_and_quote():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}
    
    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert "customerId" not in user_resp.json()
    
    customer_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "555-1234"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]
    
    user_resp2 = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert user_resp2.status_code == 200, f"Expected 200, got {user_resp2.status_code}: {user_resp2.text}"
    assert user_resp2.json()["customerId"] == customer_id
    
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
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]
    
    get_quote_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"
    assert get_quote_resp.json()["id"] == quote_id

def test_customer_self_service_backend_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    ss_headers = {"X-Auth-Token": login_resp.json()["token"]}
    
    customer_data = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "birthday": "1906-12-09T00:00:00Z",
        "city": "New York",
        "streetAddress": "Tech St 9",
        "postalCode": "10001",
        "phoneNumber": "555-5555"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=customer_data, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]
    
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Grace",
            "lastname": "Hopper",
            "contactAddress": {"city": "New York", "postalCode": "10001", "streetAddress": "Tech St 9"},
            "billingAddress": {"city": "New York", "postalCode": "10001", "streetAddress": "Tech St 9"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=ss_headers, timeout=10)
    quote_id = quote_resp.json()["id"]
    
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_get_resp = None
    for _ in range(15):
        pm_get_resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    assert pm_get_resp is not None and pm_get_resp.status_code == 200, "Quote request did not propagate to policy-management"
    
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    draft_resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_data, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"
    
    ss_get_resp = None
    status_history = []
    for _ in range(15):
        ss_get_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
        if ss_get_resp.status_code == 200:
            status_history = [s.get("status") for s in ss_get_resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in status_history:
                break
        time.sleep(1)
    assert "QUOTE_RECEIVED" in status_history, "QUOTE_RECEIVED status did not propagate to self-service"
    
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_data, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"
    
    final_get_resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    assert final_get_resp.status_code == 200, f"Expected 200, got {final_get_resp.status_code}: {final_get_resp.text}"
    final_status_history = [s.get("status") for s in final_get_resp.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_status_history

def test_policy_management_backend_create_and_delete_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Test St 2",
        "postalCode": "9000",
        "city": "Bern",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-9876"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]
    
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_data = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-01-01T00:00:00Z"},
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage A", "description": "Liability"}]}
    }
    pm_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_data, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    policy_id = pm_resp.json()["policyId"]
    
    get_pm_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert get_pm_resp.status_code == 200, f"Expected 200, got {get_pm_resp.status_code}: {get_pm_resp.text}"
    assert get_pm_resp.json()["policyId"] == policy_id
    assert get_pm_resp.json()["customer"] == customer_id
    
    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"
    
    list_resp = requests.get(get_url("policy-management-backend", "/policies"), headers=pm_headers, timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policies = list_resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

def test_customer_core_update_profile_and_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Bob",
        "lastname": "Brown",
        "birthday": "1980-10-10T00:00:00Z",
        "streetAddress": "Old St 3",
        "postalCode": "1000",
        "city": "Lausanne",
        "email": f"bob_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1111"
    }
    create_resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert create_resp.status_code == 200, f"Expected 200, got {create_resp.status_code}: {create_resp.text}"
    customer_id = create_resp.json()["customerId"]
    
    update_data = customer_data.copy()
    update_data["firstname"] = "Robert"
    update_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_data, headers=headers, timeout=10)
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"
    
    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customers"][0]["firstname"] == "Robert"
    
    address_data = {
        "streetAddress": "New St 4",
        "postalCode": "2000",
        "city": "Neuchatel"
    }
    addr_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_data, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    
    get_resp2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    customer = get_resp2.json()["customers"][0]
    assert customer["streetAddress"] == "New St 4"
    assert customer["postalCode"] == "2000"
    assert customer["city"] == "Neuchatel"

def test_customer_core_create_missing_phone_number_internal_error():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1900-01-01T00:00:00Z",
        "streetAddress": "Silent St 5",
        "postalCode": "3000",
        "city": "Geneva",
        "email": f"charlie_{uuid.uuid4().hex[:8]}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

def test_customer_management_backend_acknowledge_interactions_errors():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Dave",
        "lastname": "Davis",
        "birthday": "1995-05-05T00:00:00Z",
        "streetAddress": "Log St 6",
        "postalCode": "4000",
        "city": "Basel",
        "email": f"dave_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-2222"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]
    
    patch_data_empty = {"lastAcknowledgedInteractionId": ""}
    resp_400 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_data_empty, timeout=10)
    assert resp_400.status_code == 400, f"Expected 400, got {resp_400.status_code}: {resp_400.text}"
    
    patch_data_valid = {"lastAcknowledgedInteractionId": "int-123"}
    resp_404 = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=patch_data_valid, timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

def test_customer_self_service_backend_illegal_quote_status_transition():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers = {"X-Auth-Token": login_resp.json()["token"]}
    
    customer_data = {
        "firstname": "Eve",
        "lastname": "Evans",
        "birthday": "1992-02-02T00:00:00Z",
        "city": "Lugano",
        "streetAddress": "Lake St 7",
        "postalCode": "6000",
        "phoneNumber": "555-3333"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=customer_data, headers=headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]
    
    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "Evans",
            "contactAddress": {"city": "Lugano", "postalCode": "6000", "streetAddress": "Lake St 7"},
            "billingAddress": {"city": "Lugano", "postalCode": "6000", "streetAddress": "Lake St 7"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    quote_id = quote_resp.json()["id"]
    
    accept_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_data, headers=headers, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

def test_policy_management_backend_patch_unknown_quote_request_404():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    unknown_id = random.randint(1000000, 9999999)
    draft_data = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 100000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{unknown_id}"), json=draft_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_customer_management_backend_update_customer():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_data = {
        "firstname": "Frank",
        "lastname": "Franklin",
        "birthday": "1988-08-08T00:00:00Z",
        "streetAddress": "Mgmt St 8",
        "postalCode": "5000",
        "city": "Aarau",
        "email": f"frank_{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-4444"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=customer_data, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]
    
    update_data = {
        "firstname": "Frankie",
        "lastname": "Franklin",
        "birthday": "1988-08-08T00:00:00Z",
        "email": customer_data["email"],
        "phoneNumber": "555-4444",
        "moveHistory": [
            {"streetAddress": "Mgmt St 8", "postalCode": "5000", "city": "Aarau"}
        ]
    }
    upd_resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_data, timeout=10)
    assert upd_resp.status_code == 200, f"Expected 200, got {upd_resp.status_code}: {upd_resp.text}"
    
    get_resp = requests.get(get_url("customer-management-backend", f"/customers/{customer_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id

def test_policy_management_backend_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_data = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "8000"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=risk_data, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
