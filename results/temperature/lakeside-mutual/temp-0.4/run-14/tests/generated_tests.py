# Tests generated in iteration 14
# Captured: 2026-07-08T16:28:02
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=850  name='Customer Core Crud' ---
def test_customer_core_crud():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    customer_id = customer["customerId"]
    assert customer["firstname"] == payload["firstname"]

    resp_get = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched = resp_get.json()["customers"][0]
    assert fetched["customerId"] == customer_id
    assert fetched["firstname"] == payload["firstname"]

    payload["firstname"] = "Johnny"
    resp_put = requests.put(get_url("customer-core", f"/customers/{customer_id}"), json=payload, headers=headers, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get2 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["customers"][0]["firstname"] == "Johnny"

    address_payload = {
        "streetAddress": "789 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    resp_addr = requests.put(get_url("customer-core", f"/customers/{customer_id}/address"), json=address_payload, headers=headers, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    resp_get3 = requests.get(get_url("customer-core", f"/customers/{customer_id}"), headers=headers, timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert resp_get3.json()["customers"][0]["streetAddress"] == "789 New St"

# --- id=851  name='Customer Core Missing Phone Number' ---
def test_customer_core_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "No",
        "lastname": "Phone",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"nophone.{uuid.uuid4().hex[:8]}@example.com"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=852  name='Customer Self Signup Login Register' ---
def test_customer_self_service_signup_login_register():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    signup_payload = {"email": email, "password": password}
    resp_signup = requests.post(get_url("customer-self-service-backend", "/auth/signup"), json=signup_payload, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"
    assert resp_signup.json()["email"] == email
    assert "customerId" not in resp_signup.json()

    login_payload = {"email": email, "password": password}
    resp_login = requests.post(get_url("customer-self-service-backend", "/auth"), json=login_payload, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    token = resp_login.json()["token"]
    headers = {"X-Auth-Token": token}

    resp_user = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert "customerId" not in resp_user.json()

    reg_payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "phoneNumber": "555-5678"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json()["customerId"]

    resp_user2 = requests.get(get_url("customer-self-service-backend", "/user"), headers=headers, timeout=10)
    assert resp_user2.status_code == 200, f"Expected 200, got {resp_user2.status_code}: {resp_user2.text}"
    assert resp_user2.json()["customerId"] == customer_id

# --- id=853  name='Customer Self Insurance Quote Workflow' ---
def test_customer_self_service_insurance_quote_workflow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    token = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10).json()["token"]
    ss_headers = {"X-Auth-Token": token}

    reg_payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00Z",
        "streetAddress": "456 Elm St",
        "postalCode": "67890",
        "city": "Othertown",
        "phoneNumber": "555-5678"
    }
    customer_id = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_payload, headers=ss_headers, timeout=10).json()["customerId"]

    quote_req_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Jane",
            "lastname": "Doe",
            "contactAddress": {"streetAddress": "456 Elm St", "postalCode": "67890", "city": "Othertown"},
            "billingAddress": {"streetAddress": "456 Elm St", "postalCode": "67890", "city": "Othertown"}
        },
        "insuranceOptions": {
            "startDate": "2025-01-01T00:00:00Z",
            "insuranceType": "Auto",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_qr = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_payload, headers=ss_headers, timeout=10)
    assert resp_qr.status_code == 200, f"Expected 200, got {resp_qr.status_code}: {resp_qr.text}"
    qr_id = resp_qr.json()["id"]

    resp_qr_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    assert resp_qr_get.status_code == 200, f"Expected 200, got {resp_qr_get.status_code}: {resp_qr_get.text}"
    assert resp_qr_get.json()["statusHistory"][-1]["status"] == "REQUEST_SUBMITTED"

    accept_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_bad_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_bad_accept.status_code == 401, f"Expected 401, got {resp_bad_accept.status_code}: {resp_bad_accept.text}"

    pm_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    for _ in range(15):
        resp_pm_get = requests.get(get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}"), headers=pm_headers, timeout=10)
        if resp_pm_get.status_code == 200:
            break
        time.sleep(1)
    assert resp_pm_get.status_code == 200, f"Policy management did not receive quote request: {resp_pm_get.text}"

    draft_payload = {
        "status": "QUOTE_RECEIVED",
        "expirationDate": "2030-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"}
    }
    resp_draft = requests.patch(get_url("policy-management-backend", f"/insurance-quote-requests/{qr_id}"), json=draft_payload, headers=pm_headers, timeout=10)
    assert resp_draft.status_code == 200, f"Expected 200, got {resp_draft.status_code}: {resp_draft.text}"

    for _ in range(15):
        resp_ss_get = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
        if resp_ss_get.status_code == 200 and resp_ss_get.json().get("statusHistory", [{}])[-1].get("status") == "QUOTE_RECEIVED":
            break
        time.sleep(1)
    assert resp_ss_get.json()["statusHistory"][-1]["status"] == "QUOTE_RECEIVED", f"Self-service did not receive QUOTE_RECEIVED: {resp_ss_get.text}"

    resp_accept = requests.patch(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), json=accept_payload, headers=ss_headers, timeout=10)
    assert resp_accept.status_code == 200, f"Expected 200, got {resp_accept.status_code}: {resp_accept.text}"

    resp_final = requests.get(get_url("customer-self-service-backend", f"/insurance-quote-requests/{qr_id}"), headers=ss_headers, timeout=10)
    assert resp_final.status_code == 200, f"Expected 200, got {resp_final.status_code}: {resp_final.text}"
    assert resp_final.json()["statusHistory"][-1]["status"] == "QUOTE_ACCEPTED"

# --- id=854  name='Customer Management Interaction Logs Errors' ---
def test_customer_management_interaction_logs_patch_errors():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Log",
        "lastname": "Test",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"log.test.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    patch_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")

    resp_get = requests.get(patch_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_400 = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": ""}, timeout=10)
    assert resp_400.status_code == 400, f"Expected 400, got {resp_400.status_code}: {resp_400.text}"

    resp_404 = requests.patch(patch_url, json={"lastAcknowledgedInteractionId": customer_id}, timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=855  name='Policy Management Crud' ---
def test_policy_management_crud():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}

    cust_payload = {
        "firstname": "Policy",
        "lastname": "Owner",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"policy.owner.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    pol_payload = {
        "customerId": customer_id,
        "policyType": "Auto",
        "policyPeriod": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2026-01-01T00:00:00Z"
        },
        "deductible": {"amount": 500, "currency": "USD"},
        "policyLimit": {"amount": 50000, "currency": "USD"},
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [{"title": "Coverage A", "description": "Liability"}]
        }
    }
    resp_pol = requests.post(get_url("policy-management-backend", "/policies"), json=pol_payload, headers=headers, timeout=10)
    assert resp_pol.status_code == 200, f"Expected 200, got {resp_pol.status_code}: {resp_pol.text}"
    policy = resp_pol.json()
    policy_id = policy["policyId"]
    assert policy["customer"] == customer_id
    assert policy["policyType"] == "Auto"

    resp_get = requests.get(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["policyId"] == policy_id

    resp_del = requests.delete(get_url("policy-management-backend", f"/policies/{policy_id}"), headers=headers, timeout=10)
    assert resp_del.status_code == 204, f"Expected 204, got {resp_del.status_code}: {resp_del.text}"

# --- id=856  name='Customer Management Update' ---
def test_customer_management_update():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    cust_payload = {
        "firstname": "Manage",
        "lastname": "Me",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"manage.me.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=cust_payload, headers=headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    customer_id = resp_cust.json()["customerId"]

    update_payload = {
        "firstname": "Managed",
        "lastname": "Me",
        "birthday": "1980-01-01T00:00:00Z",
        "email": cust_payload["email"],
        "phoneNumber": "555-9999",
        "moveHistory": []
    }
    resp_upd = requests.put(get_url("customer-management-backend", f"/customers/{customer_id}"), json=update_payload, timeout=10)
    assert resp_upd.status_code == 200, f"Expected 200, got {resp_upd.status_code}: {resp_upd.text}"

    resp_get = requests.get(get_url("customer-management-backend", f"/customers/{customer_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["customerId"] == customer_id

# --- id=857  name='Policy Management Riskfactor Compute' ---
def test_policy_management_riskfactor_compute():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "birthday": "1990-01-01T00:00:00Z",
        "postalCode": "12345"
    }
    resp = requests.post(get_url("policy-management-backend", "/riskfactor/compute"), json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=858  name='Customer Core Cities' ---
def test_customer_core_get_cities():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    postal_code = "12345"
    payload = {
        "firstname": "City",
        "lastname": "Search",
        "streetAddress": "123 Main St",
        "postalCode": postal_code,
        "city": "Anytown",
        "email": f"city.search.{uuid.uuid4().hex[:8]}@example.com",
        "phoneNumber": "555-1234"
    }
    resp_cust = requests.post(get_url("customer-core", "/customers"), json=payload, headers=headers, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"

    resp = requests.get(get_url("customer-core", f"/cities/{postal_code}"), headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()

# --- id=859  name='Customer Management Notifications' ---
def test_customer_management_notifications():
    resp = requests.get(get_url("customer-management-backend", "/notifications"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)
