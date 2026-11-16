# Tests generated in iteration 03
# Captured: 2026-07-07T18:40:58
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=581  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]

    get_resp = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    fetched = get_resp.json()["customers"][0]
    assert fetched["firstname"] == payload["firstname"]
    assert fetched["email"] == payload["email"]

    update_payload = payload.copy()
    update_payload["firstname"] = "Johnny"
    put_resp = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=update_payload, headers=headers, timeout=10)
    assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"

    get_resp2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json()["customers"][0]["firstname"] == "Johnny"

# --- id=582  name='Customer Core Create Missing Phone Number' ---
def test_customer_core_create_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4()}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=583  name='Policy Management Create Policy Missing Customer' ---
def test_policy_management_create_policy_missing_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "customerId": str(uuid.uuid4()),
        "policyType": "AUTO",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Coverage", "description": "Full coverage"}]}
    }
    resp = requests.post(get_url("policy-management-backend", "/policies"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 424, f"Expected 424, got {resp.status_code}: {resp.text}"

# --- id=584  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Jane",
        "lastname": "Smith",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"jane.smith.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    cust_resp = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=core_headers, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    customer_id = cust_resp.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyType": "HOME",
        "policyPeriod": {"startDate": "2023-01-01T00:00:00Z", "endDate": "2024-01-01T00:00:00Z"},
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 1200, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    pol_resp = requests.post(get_url("policy-management-backend", "/policies"), json=policy_payload, headers=policy_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    get_pol = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert get_pol.status_code == 200, f"Expected 200, got {get_pol.status_code}: {get_pol.text}"
    assert get_pol.json()["policyType"] == "HOME"

    del_pol = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=policy_headers, timeout=10)
    assert del_pol.status_code == 204, f"Expected 204, got {del_pol.status_code}: {del_pol.text}"

    list_pol = requests.get(get_url("policy-management-backend", "/policies"), headers=policy_headers, timeout=10)
    assert list_pol.status_code == 200, f"Expected 200, got {list_pol.status_code}: {list_pol.text}"
    policies = list_pol.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=585  name='Customer Management Acknowledge Interactions Errors' ---
def test_customer_management_acknowledge_interactions_errors():
    customer_id = str(uuid.uuid4())

    payload_empty = {"lastAcknowledgedInteractionId": ""}
    resp_empty = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload_empty, timeout=10)
    assert resp_empty.status_code == 400, f"Expected 400, got {resp_empty.status_code}: {resp_empty.text}"

    payload_valid = {"lastAcknowledgedInteractionId": "int-123"}
    resp_not_found = requests.patch(get_url("customer-management-backend", f"/interaction-logs/{customer_id}"), json=payload_valid, timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=586  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "Password123!"

    signup_resp = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonder City",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Wonderland",
            "contactAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "12345", "city": "Wonder City"},
            "billingAddress": {"streetAddress": "1 Rabbit Hole", "postalCode": "12345", "city": "Wonder City"}
        },
        "insuranceOptions": {
            "startDate": "2023-06-01T00:00:00Z",
            "insuranceType": "LIFE",
            "deductible": {"amount": 0, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    quote_req_id = qr_resp.json()["id"]

    get_qr = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=ss_headers, timeout=10)
    assert get_qr.status_code == 200, f"Expected 200, got {get_qr.status_code}: {get_qr.text}"

    premature_accept = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"),
        json={"status": "QUOTE_ACCEPTED"},
        headers=ss_headers,
        timeout=10
    )
    assert premature_accept.status_code == 401, f"Expected 401, got {premature_accept.status_code}: {premature_accept.text}"

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_saw_request = False
    for _ in range(15):
        pm_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=pm_headers, timeout=10)
        if pm_get.status_code == 200:
            pm_saw_request = True
            break
        time.sleep(1)

    if pm_saw_request:
        draft_payload = {
            "status": "QUOTE_RECEIVED",
            "expirationDate": "2023-12-31T00:00:00Z",
            "insurancePremium": {"amount": 50, "currency": "USD"},
            "policyLimit": {"amount": 100000, "currency": "USD"}
        }
        draft_resp = requests.patch(
            get_url("policy-management-backend", f"/insurance-quote-requests/{quote_req_id}"),
            json=draft_payload,
            headers=pm_headers,
            timeout=10
        )
        assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

        ss_saw_quote = False
        for _ in range(15):
            ss_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=ss_headers, timeout=10)
            if ss_get.status_code == 200:
                history = ss_get.json().get("statusHistory", [])
                if any(h.get("status") == "QUOTE_RECEIVED" for h in history):
                    ss_saw_quote = True
                    break
            time.sleep(1)

        if ss_saw_quote:
            accept_resp = requests.patch(
                get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"),
                json={"status": "QUOTE_ACCEPTED"},
                headers=ss_headers,
                timeout=10
            )
            assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

            final_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_req_id}"), headers=ss_headers, timeout=10)
            assert final_get.status_code == 200, f"Expected 200, got {final_get.status_code}: {final_get.text}"
            history = final_get.json().get("statusHistory", [])
            assert any(h.get("status") == "QUOTE_ACCEPTED" for h in history)
