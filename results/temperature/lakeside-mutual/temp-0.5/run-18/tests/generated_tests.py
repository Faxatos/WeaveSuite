# Tests generated in iteration 18
# Captured: 2026-07-09T05:14:18
# Count:    17
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1042  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]
    assert data["firstname"] == payload["firstname"]
    assert data["lastname"] == payload["lastname"]
    assert data["streetAddress"] == payload["streetAddress"]
    assert data["postalCode"] == payload["postalCode"]
    assert data["city"] == payload["city"]
    assert data["email"] == payload["email"]

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    customers = get_data.get("customers", [])
    assert len(customers) == 1
    assert customers[0]["customerId"] == customer_id
    assert customers[0]["firstname"] == payload["firstname"]
    assert customers[0]["lastname"] == payload["lastname"]
    assert customers[0]["streetAddress"] == payload["streetAddress"]
    assert customers[0]["postalCode"] == payload["postalCode"]
    assert customers[0]["city"] == payload["city"]
    assert customers[0]["email"] == payload["email"]

# --- id=1043  name='Customer Core Create Customer Missing Phone Number 500' ---
def test_customer_core_create_customer_missing_phone_number_500():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=1044  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "George",
        "lastname": "Washington",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"george.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    address_payload = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
    put_data = put_resp.json()
    assert put_data["streetAddress"] == address_payload["streetAddress"]
    assert put_data["postalCode"] == address_payload["postalCode"]
    assert put_data["city"] == address_payload["city"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json().get("customers", [])[0]
    assert customer["streetAddress"] == address_payload["streetAddress"]
    assert customer["postalCode"] == address_payload["postalCode"]
    assert customer["city"] == address_payload["city"]

# --- id=1045  name='Policy Management Create Policy 424 Missing Customer' ---
def test_policy_management_create_policy_424_missing_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "customerId": str(uuid.uuid4()),
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=1046  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_get_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-01-01T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": f"alice.smith.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    pm_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    policy_data = pm_resp.json()
    policy_id = policy_data["policyId"]
    assert policy_data["customer"] == customer_id
    assert policy_data["policyType"] == policy_payload["policyType"]
    assert policy_data["deductible"]["amount"] == policy_payload["deductible"]["amount"]
    assert policy_data["policyLimit"]["amount"] == policy_payload["policyLimit"]["amount"]
    assert policy_data["insurancePremium"]["amount"] == policy_payload["insurancePremium"]["amount"]

    get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data["policyId"] == policy_id
    assert get_data["customer"] == customer_id
    assert get_data["policyType"] == policy_payload["policyType"]
    assert get_data["deductible"]["amount"] == policy_payload["deductible"]["amount"]
    assert get_data["policyLimit"]["amount"] == policy_payload["policyLimit"]["amount"]
    assert get_data["insurancePremium"]["amount"] == policy_payload["insurancePremium"]["amount"]

# --- id=1047  name='Policy Management Update Policy' ---
def test_policy_management_update_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Helen",
        "lastname": "Troy",
        "birthday": "1985-01-01T00:00:00Z",
        "streetAddress": "456 Oak St",
        "postalCode": "54321",
        "city": "Othertown",
        "email": f"helen.troy.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    pm_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    policy_id = pm_resp.json()["policyId"]

    update_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2025-01-01T00:00:00Z"
        },
        "policyType": "HOME",
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 20000, "currency": "USD"},
        "insurancePremium": {"amount": 200, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage B", "description": "Property"}]
        }
    }
    put_resp = requests.put(get_url("policy-management-backend", f"/policies/{policy_id}"), json=update_payload, headers=pm_headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
    put_data = put_resp.json()
    assert put_data["policyType"] == "HOME"
    assert put_data["deductible"]["amount"] == 1000

    get_resp = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data["policyType"] == "HOME"
    assert get_data["deductible"]["amount"] == 1000
    assert get_data["policyLimit"]["amount"] == 20000

# --- id=1048  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Jack",
        "lastname": "Sparrow",
        "birthday": "1980-01-01T00:00:00Z",
        "streetAddress": "123 Ocean St",
        "postalCode": "12345",
        "city": "Port Royal",
        "email": f"jack.sparrow.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "policyType": "AUTO",
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    pm_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=pm_headers, timeout=10)
    assert pm_resp.status_code == 200, f"Expected 200, got {pm_resp.status_code}: {pm_resp.text}"
    policy_id = pm_resp.json()["policyId"]

    del_resp = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=pm_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    list_resp = requests.get(get_url("policy-management-backend", "/policies?limit=100"), headers=pm_headers, timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policies = list_resp.json().get("policies", [])
    assert all(p["policyId"] != policy_id for p in policies)

# --- id=1049  name='Customer Self Signup Login Register' ---
def test_customer_self_service_signup_login_register():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email
    assert "customerId" not in signup_resp.json()

    login_payload = {"email": email, "password": password}
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]

    ss_headers = {"X-Auth-Token": token}
    register_payload = {
        "firstname": "Bob",
        "lastname": "Jones",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Sometown",
        "streetAddress": "789 Pine St",
        "postalCode": "67890",
        "phoneNumber": "555-5555"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=register_payload, headers=ss_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    user_resp = requests.get(get_url("customer-self-service-backend", "/user"), headers=ss_headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["email"] == email
    assert user_resp.json()["customerId"] == customer_id

# --- id=1050  name='Customer Self Quote Request Workflow' ---
def test_customer_self_service_quote_request_workflow():
    email = f"quote.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json={
        "firstname": "Charlie", "lastname": "Brown", "birthday": "1980-01-01T00:00:00Z",
        "city": "Town", "streetAddress": "1 St", "postalCode": "123", "phoneNumber": "123"
    }, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Brown",
            "contactAddress": {"streetAddress": "1 St", "postalCode": "123", "city": "Town"},
            "billingAddress": {"streetAddress": "1 St", "postalCode": "123", "city": "Town"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        pm_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), headers=pm_headers, timeout=10)
        if pm_get.status_code == 200:
            break
        time.sleep(1)
    else:
        pytest.fail("Quote request did not propagate to policy-management-backend")

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    draft_resp = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    for _ in range(15):
        ss_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
        if ss_get.status_code == 200:
            statuses = [s.get("status") for s in ss_get.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in statuses:
                break
        time.sleep(1)
    else:
        pytest.fail("Quote response did not propagate to customer-self-service-backend")

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), headers=ss_headers, timeout=10)
    assert final_get.status_code == 200, f"Expected 200, got {final_get.status_code}: {final_get.text}"
    final_statuses = [s.get("status") for s in final_get.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_statuses

# --- id=1051  name='Customer Self Quote Request Illegal Transition 401' ---
def test_customer_self_service_quote_request_illegal_transition_401():
    email = f"illegal.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json={
        "firstname": "Dave", "lastname": "Smith", "birthday": "1980-01-01T00:00:00Z",
        "city": "Town", "streetAddress": "1 St", "postalCode": "123", "phoneNumber": "123"
    }, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "1 St", "postalCode": "123", "city": "Town"},
            "billingAddress": {"streetAddress": "1 St", "postalCode": "123", "city": "Town"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    accept_resp = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"

# --- id=1052  name='Customer Self Quote Request Wrong Customer 401' ---
def test_customer_self_service_quote_request_wrong_customer_401():
    email = f"wrong.{uuid.uuid4()}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json={
        "firstname": "Frank", "lastname": "Wright", "birthday": "1980-01-01T00:00:00Z",
        "city": "Town", "streetAddress": "1 St", "postalCode": "123", "phoneNumber": "123"
    }, headers=ss_headers, timeout=10)
    real_customer_id = reg_resp.json()["customerId"]

    wrong_customer_id = "wrong-id"
    quote_payload = {
        "customerInfo": {
            "customerId": wrong_customer_id,
            "firstname": "Frank",
            "lastname": "Wright",
            "contactAddress": {"streetAddress": "1 St", "postalCode": "123", "city": "Town"},
            "billingAddress": {"streetAddress": "1 St", "postalCode": "123", "city": "Town"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "AUTO",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=ss_headers, timeout=10)
    assert quote_resp.status_code == 401, f"Expected 401, got {quote_resp.status_code}: {quote_resp.text}"

# --- id=1053  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Ian",
        "lastname": "Malcolm",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"ian.malcolm.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    update_payload = {
        "firstname": "Ian",
        "lastname": "Malcolm",
        "birthday": "1990-01-01T00:00:00Z",
        "email": f"ian.malcolm.updated.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9999",
        "moveHistory": []
    }
    put_resp = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    cc_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=cc_headers, timeout=10)
    assert cc_get.status_code == 200, f"Expected 200, got {cc_get.status_code}: {cc_get.text}"
    cc_data = cc_get.json().get("customers", [])[0]
    assert cc_data["email"] == update_payload["email"]
    assert cc_data["firstname"] == update_payload["firstname"]

# --- id=1054  name='Customer Management Acknowledge Interactions 400' ---
def test_customer_management_acknowledge_interactions_400():
    payload = {"lastAcknowledgedInteractionId": ""}
    resp = requests.patch(get_url("customer-management-backend", "/interaction-logs/any-id"), json=payload, timeout=10)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

# --- id=1055  name='Customer Management Acknowledge Interactions 404' ---
def test_customer_management_acknowledge_interactions_404():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"eve.adams.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    cc_resp = requests.post(get_url("customer-core", "/customers"), json=customer_payload, headers=cc_headers, timeout=10)
    assert cc_resp.status_code == 200, f"Expected 200, got {cc_resp.status_code}: {cc_resp.text}"
    customer_id = cc_resp.json()["customerId"]

    payload = {"lastAcknowledgedInteractionId": "interaction-1"}
    resp = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1056  name='Policy Management Quote Request 404' ---
def test_policy_management_get_quote_request_404():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    resp = requests.get(get_url("policy-management-backend", "/insurance-quote-requests/999999999"), headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1057  name='Policy Management Draft Quote 404' ---
def test_policy_management_draft_quote_404():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    resp = requests.patch(get_url("policy-management-backend", "/insurance-quote-requests/999999999"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1058  name='Policy Management Compute Risk Factor' ---
def test_policy_management_compute_risk_factor():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=pm_headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()
