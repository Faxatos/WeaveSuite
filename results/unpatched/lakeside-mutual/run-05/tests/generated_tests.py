# Tests generated in iteration 05
# Captured: 2026-07-11T22:55:03
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=39  name='Customer Core Create And Update Customer' ---
def test_customer_core_create_and_update_customer():
    customer_data = {
        "firstname": "John",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00.000Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"john.doe.{random_string()}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")
    assert customer_id is not None

    get_url_customer = get_url("customer-core", f"/customers/{customer_id}")
    resp_get = requests.get(get_url_customer, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    customer_data["firstname"] = "Johnny"
    resp_put = requests.put(get_url_customer, json=customer_data, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get_updated = requests.get(get_url_customer, timeout=10)
    assert resp_get_updated.status_code == 200, f"Expected 200, got {resp_get_updated.status_code}: {resp_get_updated.text}"
    customers_list = resp_get_updated.json().get("customers", [])
    assert len(customers_list) > 0
    assert customers_list[0].get("firstname") == "Johnny"

# --- id=40  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    customer_data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "birthday": "1990-01-01T00:00:00.000Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{random_string()}@example.com",
        "phoneNumber": "555-1234"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=customer_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json().get("customerId")

    address_data = {
        "streetAddress": "456 New St",
        "postalCode": "54321",
        "city": "Newtown"
    }
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    resp_addr = requests.put(addr_url, json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    get_url_customer = get_url("customer-core", f"/customers/{customer_id}")
    resp_get = requests.get(get_url_customer, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customers_list = resp_get.json().get("customers", [])
    assert len(customers_list) > 0
    assert customers_list[0].get("streetAddress") == "456 New St"
    assert customers_list[0].get("city") == "Newtown"

# --- id=41  name='Customer Self Backend Workflow' ---
def test_customer_self_service_backend_workflow():
    email = f"user_{random_string()}@example.com"
    password = "Password123!"
    signup_data = {"email": email, "password": password}
    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    resp_signup = requests.post(signup_url, json=signup_data, timeout=10)
    assert resp_signup.status_code == 200, f"Expected 200, got {resp_signup.status_code}: {resp_signup.text}"

    auth_url = get_url("customer-self-service-backend", "/auth")
    resp_auth = requests.post(auth_url, json=signup_data, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    token = resp_auth.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    reg_data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "birthday": "1985-05-05T00:00:00.000Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "98765",
        "phoneNumber": "555-9876"
    }
    reg_url = get_url("customer-self-service-backend", "/customers")
    resp_reg = requests.post(reg_url, json=reg_data, headers=headers, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    customer_id = resp_reg.json().get("customerId")

    get_cust_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    resp_get_cust = requests.get(get_cust_url, headers=headers, timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"
    assert resp_get_cust.json().get("customerId") == customer_id

    user_url = get_url("customer-self-service-backend", "/user")
    resp_user = requests.get(user_url, headers=headers, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    assert resp_user.json().get("customerId") == customer_id

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Alice",
            "lastname": "Smith",
            "contactAddress": {"streetAddress": "456 Rabbit Hole", "postalCode": "98765", "city": "Wonderland"},
            "billingAddress": {"streetAddress": "456 Rabbit Hole", "postalCode": "98765", "city": "Wonderland"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00.000Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    quote_url = get_url("customer-self-service-backend", "/insurance-quote-requests")
    resp_quote = requests.post(quote_url, json=quote_req_data, headers=headers, timeout=10)
    assert resp_quote.status_code == 200, f"Expected 200, got {resp_quote.status_code}: {resp_quote.text}"
    quote_id = resp_quote.json().get("id")

    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    resp_get_quote = requests.get(get_quote_url, headers=headers, timeout=10)
    assert resp_get_quote.status_code == 200, f"Expected 200, got {resp_get_quote.status_code}: {resp_get_quote.text}"
    assert resp_get_quote.json().get("id") == quote_id

    cust_quotes_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/insurance-quote-requests")
    resp_cust_quotes = requests.get(cust_quotes_url, headers=headers, timeout=10)
    assert resp_cust_quotes.status_code == 200, f"Expected 200, got {resp_cust_quotes.status_code}: {resp_cust_quotes.text}"
    assert any(q.get("id") == quote_id for q in resp_cust_quotes.json())

# --- id=42  name='Policy Management Backend Workflow' ---
def test_policy_management_backend_workflow():
    customer_data = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-02-02T00:00:00.000Z",
        "streetAddress": "789 Construction Way",
        "postalCode": "11223",
        "city": "Buildtown",
        "email": f"bob.{random_string()}@example.com",
        "phoneNumber": "555-4321"
    }
    core_url = get_url("customer-core", "/customers")
    resp_core = requests.post(core_url, json=customer_data, timeout=10)
    assert resp_core.status_code == 200, f"Expected 200, got {resp_core.status_code}: {resp_core.text}"
    customer_id = resp_core.json().get("customerId")

    policy_data = {
        "customerId": customer_id,
        "policyPeriod": {"startDate": "2023-01-01T00:00:00.000Z", "endDate": "2024-01-01T00:00:00.000Z"},
        "policyType": "Home",
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {"agreementItems": [{"title": "Fire", "description": "Fire coverage"}]}
    }
    policy_url = get_url("policy-management-backend", "/policies")
    resp_policy = requests.post(policy_url, json=policy_data, timeout=10)
    assert resp_policy.status_code == 200, f"Expected 200, got {resp_policy.status_code}: {resp_policy.text}"
    policy_id = resp_policy.json().get("policyId")

    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    resp_get_policy = requests.get(get_policy_url, timeout=10)
    assert resp_get_policy.status_code == 200, f"Expected 200, got {resp_get_policy.status_code}: {resp_get_policy.text}"
    assert resp_get_policy.json().get("policyId") == policy_id

    policy_data["policyType"] = "Auto"
    resp_put_policy = requests.put(get_policy_url, json=policy_data, timeout=10)
    assert resp_put_policy.status_code == 200, f"Expected 200, got {resp_put_policy.status_code}: {resp_put_policy.text}"

    resp_get_updated_policy = requests.get(get_policy_url, timeout=10)
    assert resp_get_updated_policy.status_code == 200, f"Expected 200, got {resp_get_updated_policy.status_code}: {resp_get_updated_policy.text}"
    assert resp_get_updated_policy.json().get("policyType") == "Auto"

    cust_policies_url = get_url("policy-management-backend", f"/customers/{customer_id}/policies")
    resp_cust_policies = requests.get(cust_policies_url, timeout=10)
    assert resp_cust_policies.status_code == 200, f"Expected 200, got {resp_cust_policies.status_code}: {resp_cust_policies.text}"
    assert any(p.get("policyId") == policy_id for p in resp_cust_policies.json())

    resp_del_policy = requests.delete(get_policy_url, timeout=10)
    assert resp_del_policy.status_code == 200, f"Expected 200, got {resp_del_policy.status_code}: {resp_del_policy.text}"

    list_policies_url = get_url("policy-management-backend", "/policies")
    resp_list = requests.get(list_policies_url, timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    assert not any(p.get("policyId") == policy_id for p in resp_list.json().get("policies", []))

# --- id=43  name='Policy Management Backend Risk Factor Computation' ---
def test_policy_management_backend_risk_factor_computation():
    risk_data = {"birthday": "1990-01-01T00:00:00.000Z", "postalCode": "12345"}
    url = get_url("policy-management-backend", "/riskfactor/compute")
    resp = requests.post(url, json=risk_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "riskFactor" in resp.json()

# --- id=44  name='Customer Management Backend Interaction Logs' ---
def test_customer_management_backend_interaction_logs():
    customer_data = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00.000Z",
        "streetAddress": "1 Hollywood Blvd",
        "postalCode": "90028",
        "city": "Los Angeles",
        "email": f"charlie.{random_string()}@example.com",
        "phoneNumber": "555-0000"
    }
    core_url = get_url("customer-core", "/customers")
    resp_core = requests.post(core_url, json=customer_data, timeout=10)
    assert resp_core.status_code == 200, f"Expected 200, got {resp_core.status_code}: {resp_core.text}"
    customer_id = resp_core.json().get("customerId")

    logs_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    resp_logs = requests.get(logs_url, timeout=10)
    assert resp_logs.status_code == 200, f"Expected 200, got {resp_logs.status_code}: {resp_logs.text}"

    ack_data = {"lastAcknowledgedInteractionId": "0"}
    resp_ack = requests.patch(logs_url, json=ack_data, timeout=10)
    assert resp_ack.status_code == 200, f"Expected 200, got {resp_ack.status_code}: {resp_ack.text}"

    resp_logs_after = requests.get(logs_url, timeout=10)
    assert resp_logs_after.status_code == 200, f"Expected 200, got {resp_logs_after.status_code}: {resp_logs_after.text}"
    assert resp_logs_after.json().get("lastAcknowledgedInteractionId") == "0"

# --- id=45  name='Customer Management Backend Update Customer' ---
def test_customer_management_backend_update_customer():
    customer_data = {
        "firstname": "Eve",
        "lastname": "Smith",
        "birthday": "1990-01-01T00:00:00.000Z",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"eve.{random_string()}@example.com",
        "phoneNumber": "555-1234"
    }
    core_url = get_url("customer-core", "/customers")
    resp_core = requests.post(core_url, json=customer_data, timeout=10)
    assert resp_core.status_code == 200, f"Expected 200, got {resp_core.status_code}: {resp_core.text}"
    customer_id = resp_core.json().get("customerId")

    update_data = {
        "firstname": "Eve",
        "lastname": "Johnson",
        "birthday": "1990-01-01T00:00:00.000Z",
        "email": f"eve.johnson.{random_string()}@example.com",
        "phoneNumber": "555-9999",
        "moveHistory": []
    }
    mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    resp_put = requests.put(mgmt_url, json=update_data, timeout=10)
    assert resp_put.status_code == 200, f"Expected 200, got {resp_put.status_code}: {resp_put.text}"

    resp_get = requests.get(mgmt_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("customerId") == customer_id

# --- id=46  name='Policy Management Backend Respond To Quote Request' ---
def test_policy_management_backend_respond_to_quote_request():
    email = f"user_{random_string()}@example.com"
    password = "Password123!"
    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    resp_auth = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = resp_auth.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    reg_data = {
        "firstname": "David",
        "lastname": "Jones",
        "birthday": "1985-05-05T00:00:00.000Z",
        "city": "Wonderland",
        "streetAddress": "456 Rabbit Hole",
        "postalCode": "98765",
        "phoneNumber": "555-9876"
    }
    resp_reg = requests.post(get_url("customer-self-service-backend", "/customers"), json=reg_data, headers=headers, timeout=10)
    customer_id = resp_reg.json().get("customerId")

    quote_req_data = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "David",
            "lastname": "Jones",
            "contactAddress": {"streetAddress": "456 Rabbit Hole", "postalCode": "98765", "city": "Wonderland"},
            "billingAddress": {"streetAddress": "456 Rabbit Hole", "postalCode": "98765", "city": "Wonderland"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00.000Z",
            "insuranceType": "Life",
            "deductible": {"amount": 500, "currency": "USD"}
        }
    }
    resp_quote = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_req_data, headers=headers, timeout=10)
    quote_id = resp_quote.json().get("id")

    respond_data = {
        "status": "ACCEPTED",
        "expirationDate": "2023-12-31T00:00:00.000Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 100000, "currency": "USD"}
    }
    patch_url = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    resp_patch = requests.patch(patch_url, json=respond_data, timeout=10)
    assert resp_patch.status_code == 200, f"Expected 200, got {resp_patch.status_code}: {resp_patch.text}"

    get_url_quote = get_url("policy-management-backend", f"/insurance-quote-requests/{quote_id}")
    resp_get = requests.get(get_url_quote, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    status_history = resp_get.json().get("statusHistory", [])
    assert any(s.get("status") == "ACCEPTED" for s in status_history)

# --- id=47  name='Customer Core Cities Reference Data' ---
def test_customer_core_cities_reference_data():
    postal_code = "12345"
    url = get_url("customer-core", f"/cities/{postal_code}")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "cities" in resp.json()
