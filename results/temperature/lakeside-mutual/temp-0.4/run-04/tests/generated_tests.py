# Tests generated in iteration 04
# Captured: 2026-07-08T11:19:59
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=773  name='Customer Core Workflow' ---
def test_customer_core_workflow():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    create_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": "john.doe@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == "John"

    customer_url = get_url("customer-core", f"/customers/{customer_id}")
    if "_links" in customer and "self" in customer["_links"]:
        href = customer["_links"]["self"]["href"]
        customer_url = href if href.startswith("http") else get_url("customer-core", href)

    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customers_data = resp.json()
    assert len(customers_data["customers"]) == 1
    assert customers_data["customers"][0]["customerId"] == customer_id

    update_payload = create_payload.copy()
    update_payload["lastname"] = "Smith"
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customers"][0]["lastname"] == "Smith"

    address_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_customer = resp.json()["customers"][0]
    assert updated_customer["streetAddress"] == "456 New St"
    assert updated_customer["postalCode"] == "54321"
    assert updated_customer["city"] == "Newtown"

    bad_payload = create_payload.copy()
    del bad_payload["phoneNumber"]
    resp = requests.post(get_url("customer-core", "/customers"), json=bad_payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=774  name='Customer Self Quote Workflow' ---
def test_customer_self_service_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["email"] == email
    assert "customerId" not in resp.json()

    login_payload = {"email": email, "password": password}
    resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    token = resp.json()["token"]

    headers = {"X-Auth-Token": token}

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "customerId" not in resp.json()

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonder City",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-9876"
    }
    resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    customer_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    if "_links" in customer and "self" in customer["_links"]:
        href = customer["_links"]["self"]["href"]
        customer_url = href if href.startswith("http") else get_url("customer-self-service-backend", href)

    resp = requests.get(customer_url, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == customer_id

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonderland",
            "contactAddress": {
                "streetAddress": "1 Rabbit Hole",
                "postalCode": "12345",
                "city": "Wonder City"
            },
            "billingAddress": {
                "streetAddress": "1 Rabbit Hole",
                "postalCode": "12345",
                "city": "Wonder City"
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
    resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    quote_id = resp.json()["id"]

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    status_history = resp.json().get("statusHistory", [])
    assert len(status_history) > 0
    assert status_history[-1]["status"] == "REQUEST_SUBMITTED"

    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json={"status": "QUOTE_ACCEPTED"}, headers=headers, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    for _ in range(15):
        resp = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management-backend")

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {
            "amount": 50,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 100000,
            "currency": "USD"
        }
    }
    resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    for _ in range(15):
        resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("statusHistory", [])
            if any(s["status"] == "QUOTE_RECEIVED" for s in history):
                break
        time.sleep(1)
    else:
        pytest.fail("QUOTE_RECEIVED status did not propagate to customer-self-service-backend")

    resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json={"status": "QUOTE_ACCEPTED"}, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    history = resp.json().get("statusHistory", [])
    assert history[-1]["status"] == "QUOTE_ACCEPTED"

# --- id=775  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    create_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildtown",
        "email": "bob@example.com",
        "phoneNumber": "555-1111"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=create_payload, headers=core_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "policyType": "Home",
        "deductible": {
            "amount": 500,
            "currency": "USD"
        },
        "policyLimit": {
            "amount": 500000,
            "currency": "USD"
        },
        "insurancePremium": {
            "amount": 1000,
            "currency": "USD"
        },
        "insuringAgreement": {
            "agreementItems": [
                {
                    "title": "Fire",
                    "description": "Fire coverage"
                }
            ]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    policy = resp.json()
    policy_id = policy["policyId"]
    assert policy["policyType"] == "Home"
    assert policy["deductible"]["amount"] == 500

    policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    if "_links" in policy and "self" in policy["_links"]:
        href = policy["_links"]["self"]["href"]
        policy_url = href if href.startswith("http") else get_url("policy-management-backend", href)

    resp = requests.get(policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["policyId"] == policy_id

    update_payload = policy_payload.copy()
    update_payload["deductible"] = {
        "amount": 1000,
        "currency": "USD"
    }
    resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=update_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(policy_url, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["deductible"]["amount"] == 1000

    resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"

    bad_policy_payload = policy_payload.copy()
    bad_policy_payload["customerId"] = "non-existent-id"
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=bad_policy_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=776  name='Customer Management Interaction Logs' ---
def test_customer_management_interaction_logs():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={}, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json={"lastAcknowledgedInteractionId": "123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
