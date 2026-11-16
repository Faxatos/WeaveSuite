# Tests generated in iteration 03
# Captured: 2026-07-09T19:49:07
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1229  name='Customer Core Crud And Errors' ---
def test_customer_core_crud_and_errors():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    bad_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

    payload = bad_payload.copy()
    payload["phoneNumber"] = "555-1234"
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert len(data["customers"]) == 1
    assert data["customers"][0]["customerId"] == customer_id

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200
    assert resp.json()["customers"][0]["firstname"] == "Johnny"

# --- id=1230  name='Cross Insurance Quote Workflow' ---
def test_cross_service_insurance_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]
    headers_self_service = {"X-Auth-Token": token}

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers_self_service, timeout=10)
    assert resp.status_code == 200
    assert "customerId" not in resp.json()

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "98765",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers_self_service, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    quote_req_payload = {
      "customerInfo": {
        "customerId": customer_id,
        "firstname": "Alice",
        "lastname": "Smith",
        "contactAddress": {
          "streetAddress": "456 Rabbit Hole",
          "postalCode": "98765",
          "city": "Wonderland"
        },
        "billingAddress": {
          "streetAddress": "456 Rabbit Hole",
          "postalCode": "98765",
          "city": "Wonderland"
        }
      },
      "insuranceOptions": {
        "startDate": "2025-01-01T00:00:00Z",
        "insuranceType": "Life",
        "deductible": {
          "amount": 100,
          "currency": "USD"
        }
      }
    }
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers_self_service, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    accept_payload = {
      "status": "QUOTE_ACCEPTED",
      "expirationDate": "2026-01-01T00:00:00Z",
      "insurancePremium": {"amount": 500, "currency": "USD"},
      "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=headers_self_service, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}
    synced = False
    for _ in range(30):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_policy, timeout=10)
        if resp.status_code == 200:
            synced = True
            break
        time.sleep(1)
    assert synced, "Quote request did not sync to policy-management"

    draft_payload = {
      "status": "QUOTE_RECEIVED",
      "expirationDate": "2026-01-01T00:00:00Z",
      "insurancePremium": {"amount": 500, "currency": "USD"},
      "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    synced_back = False
    for _ in range(30):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_self_service, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            statuses = [h.get("status") for h in history]
            if "QUOTE_RECEIVED" in statuses:
                synced_back = True
                break
        time.sleep(1)
    assert synced_back, "QUOTE_RECEIVED did not sync back to self-service"

    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=headers_self_service, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers_self_service, timeout=10)
    assert resp.status_code == 200
    history = resp.json().get("statusHistory", [])
    statuses = [h.get("status") for h in history]
    assert "QUOTE_ACCEPTED" in statuses

# --- id=1231  name='Policy Management Crud And Errors' ---
def test_policy_management_crud_and_errors():
    headers_core = {"Authorization": "Bearer b318ad736c6c844b"}
    headers_policy = {"Authorization": "Bearer b318ad736c6c844b"}

    fake_customer_id = uuid.uuid4().hex
    policy_payload = {
        "customerId": fake_customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

    cust_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "streetAddress": "123 Brick Ln",
        "postalCode": "12345",
        "city": "Construction City",
        "email": "bob@example.com",
        "phoneNumber": "555-0000"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers_core, timeout=10)
    assert resp.status_code == 200
    real_customer_id = resp.json()["customerId"]

    policy_payload["customerId"] = real_customer_id
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy_id = resp.json()["policyId"]

    resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_policy, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id
    assert resp.json()["customer"] == real_customer_id

    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers_policy, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

# --- id=1232  name='Customer Management Interaction Errors' ---
def test_customer_management_interaction_errors():
    customer_id = uuid.uuid4().hex

    payload_400 = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload_400, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    payload_404 = {"lastAcknowledgedInteractionId": "12345"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload_404, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
