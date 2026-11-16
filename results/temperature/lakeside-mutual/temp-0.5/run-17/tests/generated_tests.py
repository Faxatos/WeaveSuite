# Tests generated in iteration 17
# Captured: 2026-07-09T04:43:20
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1036  name='Self And Policy Management Workflow' ---
def test_self_service_and_policy_management_workflow():
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Signup
    signup_resp = requests.post(
        get_url("customer-self-service-backend", "/auth/signup"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    # 2. Login
    login_resp = requests.post(
        get_url("customer-self-service-backend", "/auth"),
        json={"email": email, "password": password},
        timeout=10
    )
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    # 3. Register Customer
    reg_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Zurich",
        "streetAddress": "Main St 1",
        "postalCode": "8000",
        "phoneNumber": "0791234567"
    }
    reg_resp = requests.post(
        get_url("customer-self-service-backend", "/customers"),
        json=reg_payload,
        headers=headers,
        timeout=10
    )
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]

    # 4. Get User
    user_resp = requests.get(
        get_url("customer-self-service-backend", "/user"),
        headers=headers,
        timeout=10
    )
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

    # 5. Create Quote Request
    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "John",
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
    quote_resp = requests.post(
        get_url("customer-self-service-backend", "/insurance-quote-requests"),
        json=quote_req_payload,
        headers=headers,
        timeout=10
    )
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    # 6. Negative test: Accept quote before drafted (401)
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"}
    }
    accept_early_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        json=accept_payload,
        headers=headers,
        timeout=10
    )
    assert accept_early_resp.status_code == 401, f"Expected 401, got {accept_early_resp.status_code}: {accept_early_resp.text}"

    # 7. Draft Quote on Policy Management
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        pm_get_resp = requests.get(
            get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"),
            headers=pm_headers,
            timeout=10
        )
        if pm_get_resp.status_code == 200:
            break
        time.sleep(1)
    assert pm_get_resp.status_code == 200, f"Expected 200, got {pm_get_resp.status_code}: {pm_get_resp.text}"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"}
    }
    draft_resp = requests.patch(
        get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}"),
        json=draft_payload,
        headers=pm_headers,
        timeout=10
    )
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    # Poll until quote is QUOTE_RECEIVED on self-service
    for _ in range(15):
        ss_get_resp = requests.get(
            get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
            headers=headers,
            timeout=10
        )
        if ss_get_resp.status_code == 200:
            history = [h["status"] for h in ss_get_resp.json().get("statusHistory", [])]
            if "QUOTE_RECEIVED" in history:
                break
        time.sleep(1)

    # 8. Accept quote on self-service
    accept_resp = requests.patch(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        json=accept_payload,
        headers=headers,
        timeout=10
    )
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    # 9. Verify quote status
    final_ss_get = requests.get(
        get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}"),
        headers=headers,
        timeout=10
    )
    assert final_ss_get.status_code == 200, f"Expected 200, got {final_ss_get.status_code}: {final_ss_get.text}"
    final_history = [h["status"] for h in final_ss_get.json().get("statusHistory", [])]
    assert "QUOTE_ACCEPTED" in final_history

# --- id=1037  name='Policy Management Workflow' ---
def test_policy_management_workflow():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00Z",
        "streetAddress": "Oak St 2",
        "postalCode": "1234",
        "city": "Geneva",
        "email": f"alice_{uuid.uuid4()}@example.com",
        "phoneNumber": "0791112233"
    }
    cc_post_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=customer_payload,
        headers=cc_headers,
        timeout=10
    )
    assert cc_post_resp.status_code == 200, f"Expected 200, got {cc_post_resp.status_code}: {cc_post_resp.text}"
    customer_id = cc_post_resp.json()["customerId"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    risk_payload = {
        "birthday": "1985-05-05T00:00:00Z",
        "postalCode": "1234"
    }
    risk_resp = requests.post(
        get_url("policy-management-backend", "/riskfactor/compute"),
        json=risk_payload,
        headers=pm_headers,
        timeout=10
    )
    assert risk_resp.status_code == 200, f"Expected 200, got {risk_resp.status_code}: {risk_resp.text}"
    assert "riskFactor" in risk_resp.json()

    policy_payload = {
        "customerId": customer_id,
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    policy_post_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_payload,
        headers=pm_headers,
        timeout=10
    )
    assert policy_post_resp.status_code == 200, f"Expected 200, got {policy_post_resp.status_code}: {policy_post_resp.text}"
    policy_id = policy_post_resp.json()["policyId"]

    policy_get_resp = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=pm_headers,
        timeout=10
    )
    assert policy_get_resp.status_code == 200, f"Expected 200, got {policy_get_resp.status_code}: {policy_get_resp.text}"
    assert policy_get_resp.json()["policyId"] == policy_id
    assert policy_get_resp.json()["customer"] == customer_id

    policy_payload["policyType"] = "Home"
    policy_put_resp = requests.put(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        json=policy_payload,
        headers=pm_headers,
        timeout=10
    )
    assert policy_put_resp.status_code == 200, f"Expected 200, got {policy_put_resp.status_code}: {policy_put_resp.text}"

    policy_get_resp2 = requests.get(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=pm_headers,
        timeout=10
    )
    assert policy_get_resp2.status_code == 200, f"Expected 200, got {policy_get_resp2.status_code}: {policy_get_resp2.text}"
    assert policy_get_resp2.json()["policyType"] == "Home"

    policy_del_resp = requests.delete(
        get_url("policy-management-backend", f"/policies/{policy_id}"),
        headers=pm_headers,
        timeout=10
    )
    assert policy_del_resp.status_code == 204, f"Expected 204, got {policy_del_resp.status_code}: {policy_del_resp.text}"

# --- id=1038  name='Customer Core And Management Workflow' ---
def test_customer_core_and_management_workflow():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}

    customer_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "Construction St 1",
        "postalCode": "9000",
        "city": "St. Gallen",
        "email": f"bob_{uuid.uuid4()}@example.com",
        "phoneNumber": "0793334455"
    }
    cc_post_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=customer_payload,
        headers=cc_headers,
        timeout=10
    )
    assert cc_post_resp.status_code == 200, f"Expected 200, got {cc_post_resp.status_code}: {cc_post_resp.text}"
    customer_id = cc_post_resp.json()["customerId"]

    cc_get_resp = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=cc_headers,
        timeout=10
    )
    assert cc_get_resp.status_code == 200, f"Expected 200, got {cc_get_resp.status_code}: {cc_get_resp.text}"
    assert cc_get_resp.json()["customers"][0]["firstname"] == "Bob"

    customer_payload["firstname"] = "Bobby"
    cc_put_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}"),
        json=customer_payload,
        headers=cc_headers,
        timeout=10
    )
    assert cc_put_resp.status_code == 200, f"Expected 200, got {cc_put_resp.status_code}: {cc_put_resp.text}"

    address_payload = {
        "streetAddress": "New Construction St 2",
        "postalCode": "9001",
        "city": "St. Gallen"
    }
    cc_addr_resp = requests.put(
        get_url("customer-core", f"/customers/{customer_id}/address"),
        json=address_payload,
        headers=cc_headers,
        timeout=10
    )
    assert cc_addr_resp.status_code == 200, f"Expected 200, got {cc_addr_resp.status_code}: {cc_addr_resp.text}"

    cc_get_resp2 = requests.get(
        get_url("customer-core", f"/customers/{customer_id}"),
        headers=cc_headers,
        timeout=10
    )
    assert cc_get_resp2.status_code == 200, f"Expected 200, got {cc_get_resp2.status_code}: {cc_get_resp2.text}"
    assert cc_get_resp2.json()["customers"][0]["streetAddress"] == "New Construction St 2"

    cm_get_resp = requests.get(
        get_url("customer-management-backend", f"/customers/{customer_id}"),
        timeout=10
    )
    if cm_get_resp.status_code == 200:
        cm_put_payload = {
            "firstname": "Bobby",
            "lastname": "Builder",
            "birthday": "1980-02-02T00:00:00Z",
            "email": customer_payload["email"],
            "phoneNumber": "0793334455",
            "moveHistory": [address_payload]
        }
        cm_put_resp = requests.put(
            get_url("customer-management-backend", f"/customers/{customer_id}"),
            json=cm_put_payload,
            timeout=10
        )
        assert cm_put_resp.status_code == 200, f"Expected 200, got {cm_put_resp.status_code}: {cm_put_resp.text}"

    cm_ack_bad_resp = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": ""},
        timeout=10
    )
    assert cm_ack_bad_resp.status_code == 400, f"Expected 400, got {cm_ack_bad_resp.status_code}: {cm_ack_bad_resp.text}"

    cm_ack_404_resp = requests.patch(
        get_url("customer-management-backend", f"/interaction-logs/{customer_id}"),
        json={"lastAcknowledgedInteractionId": "some-id"},
        timeout=10
    )
    assert cm_ack_404_resp.status_code == 404, f"Expected 404, got {cm_ack_404_resp.status_code}: {cm_ack_404_resp.text}"

# --- id=1039  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    cc_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "No",
        "lastname": "Phone",
        "birthday": "1980-02-02T00:00:00Z",
        "streetAddress": "Street 1",
        "postalCode": "9000",
        "city": "City",
        "email": f"nophone_{uuid.uuid4()}@example.com"
    }
    cc_post_resp = requests.post(
        get_url("customer-core", "/customers"),
        json=customer_payload,
        headers=cc_headers,
        timeout=10
    )
    assert cc_post_resp.status_code == 500, f"Expected 500, got {cc_post_resp.status_code}: {cc_post_resp.text}"

# --- id=1040  name='Policy Management Create Policy Non Existent Customer' ---
def test_policy_management_create_policy_non_existent_customer():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": "non-existent-customer-id",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "policyType": "Auto",
        "deductible": {"amount": 1000, "currency": "CHF"},
        "policyLimit": {"amount": 50000, "currency": "CHF"},
        "insurancePremium": {"amount": 500, "currency": "CHF"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage", "description": "Full coverage"}]
        }
    }
    policy_post_resp = requests.post(
        get_url("policy-management-backend", "/policies"),
        json=policy_payload,
        headers=pm_headers,
        timeout=10
    )
    assert policy_post_resp.status_code == 424, f"Expected 424, got {policy_post_resp.status_code}: {policy_post_resp.text}"

# --- id=1041  name='Policy Management Draft Quote Non Existent' ---
def test_policy_management_draft_quote_non_existent():
    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2025-12-31T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "CHF"},
        "policyLimit": {"amount": 10000, "currency": "CHF"}
    }
    draft_resp = requests.patch(
        get_url("policy-management-backend", "/insurance-quote-requests/999999999"),
        json=draft_payload,
        headers=pm_headers,
        timeout=10
    )
    assert draft_resp.status_code == 404, f"Expected 404, got {draft_resp.status_code}: {draft_resp.text}"
