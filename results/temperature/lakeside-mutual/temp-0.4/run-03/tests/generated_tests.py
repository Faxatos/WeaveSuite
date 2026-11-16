# Tests generated in iteration 03
# Captured: 2026-07-08T10:46:40
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=764  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"john.doe.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]
    assert customer_id is not None

    self_link = data.get("_links", {}).get("self", {}).get("href")
    if self_link:
        get_url_id = self_link
    else:
        get_url_id = get_url("customer-core", f"/customers/{customer_id}")

    get_resp = requests.get(get_url_id, headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert "customers" in get_data
    assert len(get_data["customers"]) == 1
    assert get_data["customers"][0]["customerId"] == customer_id
    assert get_data["customers"][0]["firstname"] == "John"
    assert get_data["customers"][0]["lastname"] == "Doe"

# --- id=765  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"jane.doe.{uuid.uuid4().hex}@example.com"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=766  name='Customer Management Interaction Logs 400' ---
def test_customer_management_interaction_logs_patch_400():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jim",
        "lastname": "Beam",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"jim.beam.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    patch_payload = {"lastAcknowledgedInteractionId": ""}
    patch_resp = requests.patch(patch_url, json=patch_payload, timeout=10)
    assert patch_resp.status_code == 400, f"Expected 400, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=767  name='Customer Management Interaction Logs 404' ---
def test_customer_management_interaction_logs_patch_404():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jack",
        "lastname": "Daniels",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Testville",
        "email": f"jack.daniels.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    patch_payload = {"lastAcknowledgedInteractionId": "some-id"}
    patch_resp = requests.patch(patch_url, json=patch_payload, timeout=10)
    assert patch_resp.status_code == 404, f"Expected 404, got {patch_resp.status_code}: {patch_resp.text}"

# --- id=768  name='Customer Self Signup Login Register' ---
def test_customer_self_service_signup_login_register():
    email = f"user.{uuid.uuid4().hex}@example.com"
    password = "Password123!"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"
    assert signup_resp.json()["email"] == email
    assert "customerId" not in signup_resp.json()

    auth_url = get_url("customer-self-service-backend", "/auth")
    auth_resp = requests.post(auth_url, json={"email": email, "password": password}, timeout=10)
    assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
    token = auth_resp.json()["token"]

    headers = {"X-Auth-Token": token}

    reg_url = get_url("customer-self-service-backend", "/customers")
    reg_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Wonderland",
        "streetAddress": "1 Rabbit Hole",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(reg_url, json=reg_payload, headers=headers, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    customer_id = reg_resp.json()["customerId"]
    assert customer_id is not None

    user_url = get_url("customer-self-service-backend", "/user")
    user_resp = requests.get(user_url, headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["customerId"] == customer_id

# --- id=769  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_get_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildville",
        "email": f"bob.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1234"
    }
    core_url = get_url("customer-core", "/customers")
    core_resp = requests.post(core_url, json=core_payload, headers=core_headers, timeout=10)
    assert core_resp.status_code == 200, f"Expected 200, got {core_resp.status_code}: {core_resp.text}"
    customer_id = core_resp.json()["customerId"]

    pol_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    pol_resp = requests.post(pol_url, json=pol_payload, headers=pol_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    self_link = pol_resp.json().get("_links", {}).get("self", {}).get("href")
    if self_link:
        get_pol_url = self_link
    else:
        get_pol_url = get_url("policy-management-backend", f"/policies/{policy_id}")

    get_pol_resp = requests.get(get_pol_url, headers=pol_headers, timeout=10)
    assert get_pol_resp.status_code == 200, f"Expected 200, got {get_pol_resp.status_code}: {get_pol_resp.text}"
    assert get_pol_resp.json()["policyId"] == policy_id
    assert get_pol_resp.json()["customer"] == customer_id
    assert get_pol_resp.json()["policyType"] == "Auto"

# --- id=770  name='Policy Management Policy' ---
def test_policy_management_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    core_payload = {
        "firstname": "Delete",
        "lastname": "Me",
        "streetAddress": "123 Build St",
        "postalCode": "12345",
        "city": "Buildville",
        "email": f"delete.{uuid.uuid4().hex}@example.com",
        "phoneNumber": "555-1234"
    }
    core_url = get_url("customer-core", "/customers")
    core_resp = requests.post(core_url, json=core_payload, headers=core_headers, timeout=10)
    assert core_resp.status_code == 200, f"Expected 200, got {core_resp.status_code}: {core_resp.text}"
    customer_id = core_resp.json()["customerId"]

    pol_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pol_url = get_url("policy-management-backend", "/policies")
    pol_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Item 1", "description": "Description 1"}
            ]
        }
    }
    pol_resp = requests.post(pol_url, json=pol_payload, headers=pol_headers, timeout=10)
    assert pol_resp.status_code == 200, f"Expected 200, got {pol_resp.status_code}: {pol_resp.text}"
    policy_id = pol_resp.json()["policyId"]

    del_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    del_resp = requests.delete(del_url, headers=pol_headers, timeout=10)
    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    list_url = get_url("policy-management-backend", "/policies")
    list_resp = requests.get(list_url, headers=pol_headers, timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    policies = list_resp.json().get("policies", [])
    assert not any(p.get("policyId") == policy_id for p in policies)

# --- id=771  name='Insurance Quote Request Workflow' ---
def test_insurance_quote_request_workflow():
    email = f"user.{uuid.uuid4().hex}@example.com"
    password = "Password123!"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "London",
        "streetAddress": "1 Cinema Rd",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "1 Cinema Rd", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "1 Cinema Rd", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=qr_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    pm_qr_url = get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}")

    found = False
    for _ in range(15):
        resp = requests.get(pm_qr_url, headers=pm_headers, timeout=10)
        if resp.status_code == 200:
            found = True
            break
        time.sleep(1)
    assert found, "Quote request did not propagate to policy-management"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    draft_resp = requests.patch(pm_qr_url, json=draft_payload, headers=pm_headers, timeout=10)
    assert draft_resp.status_code == 200, f"Expected 200, got {draft_resp.status_code}: {draft_resp.text}"

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    received = False
    for _ in range(15):
        resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
        if resp.status_code == 200:
            status_history = resp.json().get("statusHistory", [])
            if any(s.get("status") == "QUOTE_RECEIVED" for s in status_history):
                received = True
                break
        time.sleep(1)
    assert received, "Quote request status QUOTE_RECEIVED did not propagate to self-service"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 200, f"Expected 200, got {accept_resp.status_code}: {accept_resp.text}"

    final_resp = requests.get(ss_qr_url, headers=ss_headers, timeout=10)
    assert final_resp.status_code == 200, f"Expected 200, got {final_resp.status_code}: {final_resp.text}"
    status_history = final_resp.json().get("statusHistory", [])
    assert any(s.get("status") == "QUOTE_ACCEPTED" for s in status_history)

# --- id=772  name='Customer Self Quote Request Illegal Transition 401' ---
def test_customer_self_service_quote_request_illegal_transition_401():
    email = f"user.{uuid.uuid4().hex}@example.com"
    password = "Password123!"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    auth_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = auth_resp.json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Dave",
        "lastname": "Mustaine",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "LA",
        "streetAddress": "1 Metal Rd",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    reg_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10)
    customer_id = reg_resp.json()["customerId"]

    qr_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Dave",
            "lastname": "Mustaine",
            "contactAddress": {"streetAddress": "1 Metal Rd", "postalCode": "12345", "city": "LA"},
            "billingAddress": {"streetAddress": "1 Metal Rd", "postalCode": "12345", "city": "LA"}
        },
        "insuranceOptions": {
            "startDate": "2024-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 100, "currency": "USD"}
        }
    }
    qr_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=qr_payload, headers=ss_headers, timeout=10)
    assert qr_resp.status_code == 200, f"Expected 200, got {qr_resp.status_code}: {qr_resp.text}"
    qr_id = qr_resp.json()["id"]

    ss_qr_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}")
    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2099-12-31T23:59:59Z",
        "insurancePremium": {"amount": 50, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    accept_resp = requests.patch(ss_qr_url, json=accept_payload, headers=ss_headers, timeout=10)
    assert accept_resp.status_code == 401, f"Expected 401, got {accept_resp.status_code}: {accept_resp.text}"
