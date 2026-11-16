import pytest
import requests
import uuid
import random
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

def get_self_link_or_build(service: str, data: dict, fallback_path: str) -> str:
    links = data.get("_links", {})
    if "self" in links and "href" in links["self"]:
        return urljoin(MICROSERVICES[service], links["self"]["href"])
    return get_url(service, fallback_path)

# --- Tests ---

def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]
    
    get_url_path = get_self_link_or_build("customer-core", data, f"/customers/{customer_id}")
    get_resp = requests.get(get_url_path, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    
    if "customers" in get_data:
        fetched_customer = get_data["customers"][0]
    else:
        fetched_customer = get_data
        
    assert fetched_customer["customerId"] == customer_id
    assert fetched_customer["firstname"] == "John"
    assert fetched_customer["email"] == payload["email"]

def test_customer_core_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"jane.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newville",
        "email": payload["email"],
        "phoneNumber": "555-9999"
    }
    put_url = get_url("customer-core", f"/customers/{customer_id}")
    put_resp = requests.put(put_url, json=update_payload, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
    
    get_url_path = get_url("customer-core", f"/customers/{customer_id}")
    get_resp = requests.get(get_url_path, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    fetched_customer = get_resp.json()["customers"][0]
    assert fetched_customer["lastname"] == "Smith"
    assert fetched_customer["streetAddress"] == "456 New St"

def test_customer_core_create_missing_phone_number_500():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"john.doe.{uuid.uuid4()}@example.com"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

def test_policy_management_compute_risk_factor():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    url = get_url("policy-management-backend", "/riskfactor/compute")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

def test_policy_management_create_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Oaktown",
        "email": f"alice.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5678"
    }
    cc_url = get_url("customer-core", "/customers")
    cc_resp = requests.post(cc_url, json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_payload = {
        "customerId": customer_id,
        "policyType": "AUTO",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    pm_url = get_url("policy-management-backend", "/policies")
    pm_resp = requests.post(pm_url, json=pm_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    data = pm_resp.json()
    policy_id = data["policyId"]

    pm_get_url = get_self_link_or_build("policy-management-backend", data, f"/policies/{policy_id}")
    pm_get_resp = requests.get(pm_get_url, headers=pm_headers, timeout=10)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"
    assert pm_get_resp.json()["policyId"] == policy_id
    assert pm_get_resp.json()["customer"] == customer_id

def test_policy_management_create_policy_non_existent_customer_424():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_payload = {
        "customerId": f"fake-cust-{uuid.uuid4()}",
        "policyType": "AUTO",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    pm_url = get_url("policy-management-backend", "/policies")
    pm_resp = requests.post(pm_url, json=pm_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 424, f"Expected 424, got {pm_resp.status_code}: {pm_resp.text}"

def test_policy_management_delete_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "Delete",
        "lastname": "Me",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"delete.me.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    cc_url = get_url("customer-core", "/customers")
    cc_resp = requests.post(cc_url, json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_payload = {
        "customerId": customer_id,
        "policyType": "AUTO",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Coverage A", "description": "Liability"}
            ]
        }
    }
    pm_url = get_url("policy-management-backend", "/policies")
    pm_resp = requests.post(pm_url, json=pm_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    policy_id = pm_resp.json()["policyId"]

    del_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    del_resp = requests.delete(del_url, headers=pm_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    list_url = get_url("policy-management-backend", "/policies")
    list_resp = requests.get(list_url, headers=pm_headers, timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policies = list_resp.json().get("policies", [])
    assert all(p.get("policyId") != policy_id for p in policies)

def test_self_service_workflow_and_quote_request():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    auth_url = get_url("customer-self-service-backend", "/auth")
    auth_resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    cust_url = get_url("customer-self-service-backend", "/customers")
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Constructville",
        "streetAddress": "1 Build St",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(cust_url, json=cust_payload, headers=headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    cust_data = cust_resp.json()
    customer_id = cust_data["customerId"]

    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"city": "Constructville", "postalCode": "12345", "streetAddress": "1 Build St"},
            "billingAddress": {"city": "Constructville", "postalCode": "12345", "streetAddress": "1 Build St"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_resp = requests.post(qr_url, json=qr_payload, headers=headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_data = qr_resp.json()
    qr_id = qr_data["id"]

    qr_get_url = get_self_link_or_build("customer-self-service-backend", qr_data, f"/insurance-quote-requests/{qr_id}")
    qr_get_resp = requests.get(qr_get_url, headers=headers, timeout=10)
    assert qr_get_resp.status_code == 200, f"Expected 200, got {qr_get_resp.status_code}: {qr_get_resp.text}"
    assert qr_get_resp.json()["id"] == qr_id
    assert qr_get_resp.json()["customerInfo"]["customerId"] == customer_id

def test_self_service_accept_quote_in_submitted_state_401():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers = {"X-Auth-Token": auth_resp.json()["token"]}

    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json={
        "firstname": "Bob", "lastname": "Builder", "birthday": "1980-01-01T00:00:00Z",
        "city": "Constructville", "streetAddress": "1 Build St", "postalCode": "12345", "phoneNumber": "555-9876"
    }, headers=headers, timeout=10)
    customer_id = cust_resp.json()["customerId"]

    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json={
        "customerInfo": {
            "customerId": customer_id, "firstname": "Bob", "lastname": "Builder",
            "contactAddress": {"city": "Constructville", "postalCode": "12345", "streetAddress": "1 Build St"},
            "billingAddress": {"city": "Constructville", "postalCode": "12345", "streetAddress": "1 Build St"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z", "insuranceType": "HOME", "deductible": {"amount": 1000, "currency": "USD"}
        }
    }, headers=headers, timeout=10)
    qr_id = qr_resp.json()["id"]

    patch_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    patch_resp = requests.patch(patch_url, json={
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

def test_end_to_end_quote_workflow():
    email = f"e2e.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    ss_headers = {"X-Auth-Token": auth_resp.json()["token"]}

    cust_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json={
        "firstname": "Eve", "lastname": "End", "birthday": "1990-01-01T00:00:00Z",
        "city": "Endville", "streetAddress": "1 End St", "postalCode": "12345", "phoneNumber": "555-1111"
    }, headers=ss_headers, timeout=10)
    customer_id = cust_resp.json()["customerId"]

    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json={
        "customerInfo": {
            "customerId": customer_id, "firstname": "Eve", "lastname": "End",
            "contactAddress": {"city": "Endville", "postalCode": "12345", "streetAddress": "1 End St"},
            "billingAddress": {"city": "Endville", "postalCode": "12345", "streetAddress": "1 End St"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z", "insuranceType": "HOME", "deductible": {"amount": 1000, "currency": "USD"}
        }
    }, headers=ss_headers, timeout=10)
    qr_id = qr_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")
    
    found = False
    for _ in range(10):
        if requests.get(pm_qr_url, headers=pm_headers, timeout=10).status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management-backend"

    draft_resp = requests.patch(pm_qr_url, json={
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(10):
        resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                received = True
                break
        time.sleep(1)
    assert received, "QUOTE_RECEIVED status did not propagate to customer-self-service-backend"

    accept_resp = requests.patch(ss_qr_url, json={
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert final_resp.status_code == 200, f"Expected 200, got {final_resp.status_code}: {final_resp.text}"
    history = final_resp.json().get("statusHistory", [])
    assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)

def test_customer_management_acknowledge_empty_id_400():
    url = get_url("customer-management-backend", "/interaction-logs/any-customer-id")
    resp = requests.patch(url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

def test_customer_management_acknowledge_no_log_404():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cc_payload = {
        "firstname": "NoLog",
        "lastname": "User",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"nolog.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    cc_url = get_url("customer-core", "/customers")
    cc_resp = requests.post(cc_url, json=cc_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp = requests.patch(url, json={"lastAcknowledgedInteractionId": "some-id"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_policy_management_draft_quote_non_existent_404():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    fake_id = random.randint(1000000, 9999999)
    url = get_url("policy-management-backend", f"/insurance-quote-requests/{fake_id}")
    
    resp = requests.patch(url, json={
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-01-01T00:00:00Z",
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }, headers=pm_headers, timeout=10)
    
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_self_service_register_customer_unauthorized_401():
    cust_url = get_url("customer-self-service-backend", "/customers")
    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Constructville",
        "streetAddress": "1 Build St",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(cust_url, json=cust_payload, timeout=10)
    assert cust_resp.status_code == 401, f"Expected 401, got {cust_resp.status_code}: {cust_resp.text}"

def test_self_service_quote_request_wrong_customer_id_401():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    headers = {"X-Auth-Token": auth_resp.json()["token"]}

    requests.post(get_url("customer-self-service-backend", "/customers"), json={
        "firstname": "Bob", "lastname": "Builder", "birthday": "1980-01-01T00:00:00Z",
        "city": "Constructville", "streetAddress": "1 Build St", "postalCode": "12345", "phoneNumber": "555-9876"
    }, headers=headers, timeout=10)
    
    wrong_customer_id = f"wrong-id-{uuid.uuid4()}"
    qr_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    qr_payload = {
        "customerInfo": {
            "customerId": wrong_customer_id,
            "firstname": "Bob",
            "lastname": "Builder",
            "contactAddress": {"city": "Constructville", "postalCode": "12345", "streetAddress": "1 Build St"},
            "billingAddress": {"city": "Constructville", "postalCode": "12345", "streetAddress": "1 Build St"}
        },
        "insuranceOptions": {
            "startDate": "2023-05-01T00:00:00Z",
            "insuranceType": "HOME",
            "deductible": {"amount": 1000, "currency": "USD"}
        }
    }
    qr_resp = requests.post(qr_url, json=qr_payload, headers=headers, timeout=10)
    assert qr_resp.status_code == 401, f"Expected 401, got {qr_resp.status_code}: {qr_resp.text}"
