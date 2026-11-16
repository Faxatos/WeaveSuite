import pytest
import requests
import uuid
import random
import string
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

def test_self_service_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    
    login_url = get_url("customer-self-service-backend", "/auth")
    resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}
    
    user_url = get_url("customer-self-service-backend", "/user")
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()
    
    customers_url = get_url("customer-self-service-backend", "/customers")
    customer_data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "phoneNumber": "555-5678"
    }
    resp = requests.post(customers_url, headers=headers, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    resp = requests.get(user_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id
    
    quote_req_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    quote_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Doe",
            "contactAddress": {
                "streetAddress": "123 Main St",
                "postalCode": "12345",
                "city": "Anytown"
            },
            "billingAddress": {
                "streetAddress": "123 Main St",
                "postalCode": "12345",
                "city": "Anytown"
            }
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {
                "amount": 500,
                "currency": "USD"
            }
        }
    }
    resp = requests.post(quote_req_url, headers=headers, json=quote_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]
    
    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id
    
    patch_data = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_quote_url, headers=headers, json=patch_data, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_policy_management_crud():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    
    core_customers_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "John",
        "lastname": "Smith",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"john.smith_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(core_customers_url, headers=core_headers, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    policies_url = get_url("policy-management-backend", "/policies")
    policy_data = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Fire", "description": "Fire coverage"}
            ]
        }
    }
    resp = requests.post(policies_url, headers=pm_headers, json=policy_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]
    
    links = resp.json().get("_links", {})
    self_link = links.get("self", {}).get("href")
    if self_link:
        get_policy_url = self_link
        if not get_policy_url.startswith("http"):
            get_policy_url = get_url("policy-management-backend", get_policy_url)
    else:
        get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
        
    resp = requests.get(get_policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == customer_id
    assert resp.json()["policyType"] == "HOME"
    
    policy_data["policyType"] = "AUTO"
    resp = requests.put(get_policy_url, headers=pm_headers, json=policy_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "AUTO"
    
    resp = requests.get(get_policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyType"] == "AUTO"
    
    resp = requests.delete(get_policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"
    
    list_policies_url = get_url("policy-management-backend", "/policies")
    resp = requests.get(list_policies_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies), "Deleted policy still found in listing"


def test_customer_core_change_address():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_customers_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "1 Punish St",
        "postalCode": "11111",
        "city": "New York",
        "email": f"frank_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9999"
    }
    resp = requests.post(core_customers_url, headers=core_headers, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    address_url = get_url("customer-core", f"/customers/{customer_id}/address")
    new_address = {
        "streetAddress": "2 Safehouse Ave",
        "postalCode": "22222",
        "city": "New Jersey"
    }
    resp = requests.put(address_url, headers=core_headers, json=new_address, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["streetAddress"] == "2 Safehouse Ave"
    
    get_url_core = get_url("customer-core", f"/customers/{customer_id}")
    resp = requests.get(get_url_core, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()["customers"][0]
    assert customer["streetAddress"] == "2 Safehouse Ave"
    assert customer["postalCode"] == "22222"
    assert customer["city"] == "New Jersey"


def test_customer_core_missing_phone_number():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_customers_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1985-01-01T00:00:00Z",
        "streetAddress": "101 Brick Ln",
        "postalCode": "24680",
        "city": "Buildtown",
        "email": f"bob.builder_{uuid.uuid4()}@example.com"
    }
    resp = requests.post(core_customers_url, headers=core_headers, json=customer_data, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"


def test_customer_management_interaction_log_errors():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_customers_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "Alice",
        "lastname": "Wonder",
        "birthday": "1992-01-01T00:00:00Z",
        "streetAddress": "789 Pine St",
        "postalCode": "13579",
        "city": "Sometown",
        "email": f"alice.wonder_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(core_customers_url, headers=core_headers, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    cm_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    
    resp = requests.patch(cm_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"


def test_customer_core_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_customers_url = get_url("customer-core", "/customers")
    customer_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "11111",
        "city": "Hollywood",
        "email": f"charlie_{uuid.uuid4()}@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(core_customers_url, headers=core_headers, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]
    
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    customer_data["firstname"] = "Charles"
    resp = requests.put(update_url, headers=core_headers, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["firstname"] == "Charles"
    
    resp = requests.get(update_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["firstname"] == "Charles"


def test_policy_management_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_url = get_url("policy-management-backend", "/riskfactor/compute")
    risk_data = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(risk_url, headers=pm_headers, json=risk_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()


def test_get_cities_for_postal_code():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cities_url = get_url("customer-core", "/cities/12345")
    resp = requests.get(cities_url, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()


def test_customer_management_notifications():
    notifications_url = get_url("customer-management-backend", "/notifications")
    resp = requests.get(notifications_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)
