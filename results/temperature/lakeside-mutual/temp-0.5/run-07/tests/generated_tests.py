import pytest
import requests
import uuid
import random
import string
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

def random_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

API_KEY = "b318ad736c6c844b"
HEADERS_CORE = {"Authorization": f"Bearer {API_KEY}"}
HEADERS_POLICY = {"Authorization": f"Bearer {API_KEY}"}

# --- Tests ---

def test_customer_self_service_signup_login_register_and_quote():
    email = random_email()
    password = "Password123!"
    signup_payload = {"email": email, "password": password}
    
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email

    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers = {"X-Auth-Token": token}

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()

    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "0791234567"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=headers, json=reg_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    new_address = {
        "streetAddress": "New St 2",
        "postalCode": "8001",
        "city": "Zurich"
    }
    resp = requests.put(get_url("customer-self-service-backend", f"/customers/{customer_id}/address"), headers=headers, json=new_address, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("customer-self-service-backend", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
            "lastname": "Doe",
            "contactAddress": new_address,
            "billingAddress": new_address
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), headers=headers, json=quote_req_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == quote_id


def test_customer_core_create_update_customer():
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Test Ave 5",
        "postalCode": "1234",
        "city": "Geneva",
        "email": random_email(),
        "phoneNumber": "+41791234567"
    }
    resp = requests.post(get_url("customer-core", "/customers"), headers=HEADERS_CORE, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers = resp.json().get("customers", [])
    assert len(customers) == 1
    assert customers[0]["customerId"] == customer_id

    payload["city"] = "Lausanne"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), headers=HEADERS_CORE, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["city"] == "Lausanne"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=HEADERS_CORE, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["city"] == "Lausanne"


def test_customer_core_create_missing_phone_error():
    payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "Test St 1",
        "postalCode": "1000",
        "city": "Bern",
        "email": random_email()
    }
    resp = requests.post(get_url("customer-core", "/customers"), headers=HEADERS_CORE, json=payload, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"


def test_policy_management_create_and_delete_policy():
    cust_payload = {
        "firstname": "Charlie",
        "lastname": "Brown",
        "birthday": "1980-08-08T00:00:00Z",
        "streetAddress": "Policy St 9",
        "postalCode": "4000",
        "city": "Basel",
        "email": random_email(),
        "phoneNumber": "0790000000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), headers=HEADERS_CORE, json=cust_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 1000000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage", "description": "Full coverage"}
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), headers=HEADERS_POLICY, json=pol_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id

    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("policy-management-backend", "/policies"), headers=HEADERS_POLICY, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policies = resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies)


def test_customer_management_acknowledge_interactions_errors():
    cust_payload = {
        "firstname": "Diana",
        "lastname": "Prince",
        "birthday": "1975-03-22T00:00:00Z",
        "streetAddress": "Amazon Ave 1",
        "postalCode": "1234",
        "city": "Geneva",
        "email": random_email(),
        "phoneNumber": "0791112233"
    }
    resp = requests.post(get_url("customer-core", "/customers"), headers=HEADERS_CORE, json=cust_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    ack_payload_empty = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload_empty, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    ack_payload_valid = {"lastAcknowledgedInteractionId": "int-123"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=ack_payload_valid, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"


def test_self_service_accept_quote_prematurely_error():
    email = random_email()
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1992-02-02T00:00:00Z",
        "city": "Lugano",
        "streetAddress": "Lake St 1",
        "postalCode": "6900",
        "phoneNumber": "0793334455"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=headers_ss, json=reg_payload, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Eve",
            "lastname": "Adams",
            "contactAddress": {"streetAddress": "Lake St 1", "postalCode": "6900", "city": "Lugano"},
            "billingAddress": {"streetAddress": "Lake St 1", "postalCode": "6900", "city": "Lugano"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Home",
            "deductible": {"amount": 200, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), headers=headers_ss, json=quote_req_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 500000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_ss, json=accept_payload, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_insurance_quote_workflow_cross_service():
    email = random_email()
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp.json()["token"]
    headers_ss = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Frank",
        "lastname": "Castle",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Lucerne",
        "streetAddress": "Bridge St 1",
        "postalCode": "6000",
        "phoneNumber": "0795556677"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), headers=headers_ss, json=reg_payload, timeout=10)
    customer_id = resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Frank",
            "lastname": "Castle",
            "contactAddress": {"streetAddress": "Bridge St 1", "postalCode": "6000", "city": "Lucerne"},
            "billingAddress": {"streetAddress": "Bridge St 1", "postalCode": "6000", "city": "Lucerne"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "CHF"}
        }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), headers=headers_ss, json=quote_req_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    max_retries = 10
    found = False
    for _ in range(max_retries):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=HEADERS_POLICY, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 1000000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=HEADERS_POLICY, json=draft_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    received = False
    for _ in range(max_retries):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_ss, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate back to customer-self-service-backend"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2026-01-01T00:00:00Z",
        "insurancePremium": {"amount": 200, "currency": "CHF"},
        "policyLimit": {"amount": 1000000, "currency": "CHF"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_ss, json=accept_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_ss, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)
