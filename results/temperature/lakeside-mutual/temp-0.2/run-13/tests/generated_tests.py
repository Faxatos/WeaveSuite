# Tests generated in iteration 13
# Captured: 2026-07-07T10:02:46
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=456  name='Customer Core Create And Customer' ---
def test_customer_core_create_and_get_customer():
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
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    customer_id = data["customerId"]

    get_url_path = f"/customers/{customer_id}"
    resp_get = requests.get(get_url("customer-core", get_url_path), headers=headers, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    customer = get_data["customers"][0]
    assert customer["customerId"] == customer_id
    assert customer["firstname"] == payload["firstname"]
    assert customer["email"] == payload["email"]

# --- id=457  name='Customer Core Create Customer Missing Phone Number' ---
def test_customer_core_create_customer_missing_phone_number():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "streetAddress": "123 Main St",
        "postalCode": "12345",
        "city": "Anytown",
        "email": f"jane.doe.{uuid.uuid4()}@example.com"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 500, f"Expected 500, got {resp.status_code}: {resp.text}"

# --- id=458  name='Customer Core Update Customer' ---
def test_customer_core_update_customer():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Eve",
        "lastname": "Adams",
        "streetAddress": "123 Apple St",
        "postalCode": "10001",
        "city": "Eden",
        "email": f"eve.adams.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-2222"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    update_payload = payload.copy()
    update_payload["firstname"] = "Evelyn"
    update_url = get_url("customer-core", f"/customers/{customer_id}")
    update_resp = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    get_url_path = f"/customers/{customer_id}"
    get_resp = requests.get(get_url("customer-core", get_url_path), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()["customers"][0]
    assert customer["firstname"] == "Evelyn"

# --- id=459  name='Customer Core Change Address' ---
def test_customer_core_change_address():
    headers = {"Authorization": "Bearer b318ad736c6c844b"}
    payload = {
        "firstname": "Frank",
        "lastname": "Castle",
        "streetAddress": "123 Punish St",
        "postalCode": "10002",
        "city": "New York",
        "email": f"frank.castle.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-3333"
    }
    url = get_url("customer-core", "/customers")
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_id = resp.json()["customerId"]

    address_payload = {
        "streetAddress": "456 Justice Ave",
        "postalCode": "10003",
        "city": "New York"
    }
    addr_url = get_url("customer-core", f"/customers/{customer_id}/address")
    addr_resp = requests.put(addr_url, json=address_payload, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    get_url_path = f"/customers/{customer_id}"
    get_resp = requests.get(get_url("customer-core", get_url_path), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()["customers"][0]
    assert customer["streetAddress"] == "456 Justice Ave"
    assert customer["postalCode"] == "10003"

# --- id=460  name='Policy Management Create And Policy' ---
def test_policy_management_create_and_delete_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "streetAddress": "456 Oak St",
        "postalCode": "67890",
        "city": "Othertown",
        "email": f"alice.smith.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-9876"
    }
    core_url = get_url("customer-core", "/customers")
    core_resp = requests.post(core_url, json=customer_payload, headers=core_headers, timeout=10)
    assert core_resp.status_code == 200, f"Expected 200, got {core_resp.status_code}: {core_resp.text}"
    customer_id = core_resp.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Home",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 1000, "currency": "USD"},
        "policyLimit": {"amount": 500000, "currency": "USD"},
        "insurancePremium": {"amount": 500, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Fire", "description": "Fire coverage"}
            ]
        }
    }
    policy_url = get_url("policy-management-backend", "/policies")
    policy_resp = requests.post(policy_url, json=policy_payload, headers=policy_headers, timeout=10)
    assert policy_resp.status_code == 200, f"Expected 200, got {policy_resp.status_code}: {policy_resp.text}"
    policy_id = policy_resp.json()["policyId"]

    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    get_policy_resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert get_policy_resp.status_code == 200, f"Expected 200, got {get_policy_resp.status_code}: {get_policy_resp.text}"
    assert get_policy_resp.json()["policyId"] == policy_id
    assert get_policy_resp.json()["customer"] == customer_id

    delete_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    delete_policy_resp = requests.delete(delete_policy_url, headers=policy_headers, timeout=10)
    assert delete_policy_resp.status_code == 204, f"Expected 204, got {delete_policy_resp.status_code}: {delete_policy_resp.text}"

    get_policy_resp2 = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert get_policy_resp2.status_code != 200

# --- id=461  name='Policy Management Update Policy' ---
def test_policy_management_update_policy():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Grace",
        "lastname": "Hopper",
        "streetAddress": "123 Code St",
        "postalCode": "10004",
        "city": "Techville",
        "email": f"grace.hopper.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-4444"
    }
    core_url = get_url("customer-core", "/customers")
    core_resp = requests.post(core_url, json=customer_payload, headers=core_headers, timeout=10)
    assert core_resp.status_code == 200, f"Expected 200, got {core_resp.status_code}: {core_resp.text}"
    customer_id = core_resp.json()["customerId"]

    policy_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    policy_payload = {
        "customerId": customer_id,
        "policyType": "Life",
        "policyPeriod": {
            "startDate": "2023-01-01T00:00:00Z",
            "endDate": "2024-01-01T00:00:00Z"
        },
        "deductible": {"amount": 0, "currency": "USD"},
        "policyLimit": {"amount": 1000000, "currency": "USD"},
        "insurancePremium": {"amount": 1000, "currency": "USD"},
        "insuringAgreement": {
            "agreementItems": [
                {"title": "Life", "description": "Life coverage"}
            ]
        }
    }
    policy_url = get_url("policy-management-backend", "/policies")
    policy_resp = requests.post(policy_url, json=policy_payload, headers=policy_headers, timeout=10)
    assert policy_resp.status_code == 200, f"Expected 200, got {policy_resp.status_code}: {policy_resp.text}"
    policy_id = policy_resp.json()["policyId"]

    update_payload = policy_payload.copy()
    update_payload["insurancePremium"] = {"amount": 1200, "currency": "USD"}
    update_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    update_resp = requests.put(update_url, json=update_payload, headers=policy_headers, timeout=10)
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"

    get_policy_url = get_url("policy-management-backend", f"/policies/{policy_id}")
    get_policy_resp = requests.get(get_policy_url, headers=policy_headers, timeout=10)
    assert get_policy_resp.status_code == 200, f"Expected 200, got {get_policy_resp.status_code}: {get_policy_resp.text}"
    assert get_policy_resp.json()["insurancePremium"]["amount"] == 1200

# --- id=462  name='Customer Management Update Customer' ---
def test_customer_management_update_customer():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Hank",
        "lastname": "Pym",
        "streetAddress": "123 Ant St",
        "postalCode": "10005",
        "city": "San Francisco",
        "email": f"hank.pym.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-5555"
    }
    core_url = get_url("customer-core", "/customers")
    core_resp = requests.post(core_url, json=customer_payload, headers=core_headers, timeout=10)
    assert core_resp.status_code == 200, f"Expected 200, got {core_resp.status_code}: {core_resp.text}"
    customer_id = core_resp.json()["customerId"]

    mgmt_payload = {
        "firstname": "Henry",
        "lastname": "Pym",
        "birthday": "1960-01-01T00:00:00Z",
        "email": customer_payload["email"],
        "phoneNumber": "555-5555",
        "moveHistory": []
    }
    mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    mgmt_resp = requests.put(mgmt_url, json=mgmt_payload, timeout=10)
    assert mgmt_resp.status_code == 200, f"Expected 200, got {mgmt_resp.status_code}: {mgmt_resp.text}"

    get_mgmt_url = get_url("customer-management-backend", f"/customers/{customer_id}")
    get_mgmt_resp = requests.get(get_mgmt_url, timeout=10)
    assert get_mgmt_resp.status_code == 200, f"Expected 200, got {get_mgmt_resp.status_code}: {get_mgmt_resp.text}"
    assert get_mgmt_resp.json()["customerId"] == customer_id

# --- id=463  name='Customer Management Acknowledge Interactions Not Found' ---
def test_customer_management_acknowledge_interactions_not_found():
    core_headers = {"Authorization": "Bearer b318ad736c6c844b"}
    customer_payload = {
        "firstname": "Dave",
        "lastname": "Grohl",
        "streetAddress": "123 Rock St",
        "postalCode": "90210",
        "city": "Los Angeles",
        "email": f"dave.grohl.{uuid.uuid4()}@example.com",
        "phoneNumber": "555-1111"
    }
    core_url = get_url("customer-core", "/customers")
    core_resp = requests.post(core_url, json=customer_payload, headers=core_headers, timeout=10)
    assert core_resp.status_code == 200, f"Expected 200, got {core_resp.status_code}: {core_resp.text}"
    customer_id = core_resp.json()["customerId"]

    ack_payload = {
        "lastAcknowledgedInteractionId": "interaction-123"
    }
    ack_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    ack_resp = requests.patch(ack_url, json=ack_payload, timeout=10)
    assert ack_resp.status_code == 404, f"Expected 404, got {ack_resp.status_code}: {ack_resp.text}"

    get_log_url = get_url("customer-management-backend", f"/interaction-logs/{customer_id}")
    get_log_resp = requests.get(get_log_url, timeout=10)
    assert get_log_resp.status_code == 200, f"Expected 200, got {get_log_resp.status_code}: {get_log_resp.text}"
    assert get_log_resp.json()["interactions"] == []

# --- id=464  name='Customer Self Signup And Register' ---
def test_customer_self_service_signup_and_register():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    signup_url = get_url("customer-self-service-backend", "/auth/signup")
    signup_resp = requests.post(signup_url, json={"email": email, "password": password}, timeout=10)
    assert signup_resp.status_code == 200, f"Expected 200, got {signup_resp.status_code}: {signup_resp.text}"

    login_url = get_url("customer-self-service-backend", "/auth")
    login_resp = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    token = login_resp.json()["token"]

    headers = {"X-Auth-Token": token}

    user_url = get_url("customer-self-service-backend", "/user")
    user_resp = requests.get(user_url, headers=headers, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    assert user_resp.json()["email"] == email

    register_url = get_url("customer-self-service-backend", "/customers")
    register_payload = {
        "firstname": "Bob",
        "lastname": "Builder",
        "birthday": "1980-01-01T00:00:00Z",
        "city": "Constructville",
        "streetAddress": "123 Brick Ln",
        "postalCode": "98765",
        "phoneNumber": "555-4321"
    }
    register_resp = requests.post(register_url, json=register_payload, headers=headers, timeout=10)
    assert register_resp.status_code == 200, f"Expected 200, got {register_resp.status_code}: {register_resp.text}"
    customer_id = register_resp.json()["customerId"]

    get_customer_url = get_url("customer-self-service-backend", f"/customers/{customer_id}")
    get_customer_resp = requests.get(get_customer_url, headers=headers, timeout=10)
    assert get_customer_resp.status_code == 200, f"Expected 200, got {get_customer_resp.status_code}: {get_customer_resp.text}"
    assert get_customer_resp.json()["customerId"] == customer_id

# --- id=465  name='Customer Self Change Address' ---
def test_customer_self_service_change_address():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    register_payload = {
        "firstname": "Ivy",
        "lastname": "Poison",
        "birthday": "1990-01-01T00:00:00Z",
        "city": "Gotham",
        "streetAddress": "123 Plant St",
        "postalCode": "10006",
        "phoneNumber": "555-6666"
    }
    register_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=register_payload, headers=headers, timeout=10)
    customer_id = register_resp.json()["customerId"]

    address_payload = {
        "streetAddress": "456 Vine Ave",
        "postalCode": "10007",
        "city": "Gotham"
    }
    addr_url = get_url("customer-self-service-backend", f"/customers/{customer_id}/address")
    addr_resp = requests.put(addr_url, json=address_payload, headers=headers, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"

    get_url_path = f"/customers/{customer_id}"
    get_resp = requests.get(get_url("customer-self-service-backend", get_url_path), headers=headers, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["customerId"] == customer_id

# --- id=466  name='Customer Self Quote Request Illegal Transition' ---
def test_customer_self_service_quote_request_illegal_transition():
    email = f"user.{uuid.uuid4()}@example.com"
    password = "password123"

    requests.post(get_url("customer-self-service-backend", "/auth/signup"), json={"email": email, "password": password}, timeout=10)
    login_resp = requests.post(get_url("customer-self-service-backend", "/auth"), json={"email": email, "password": password}, timeout=10)
    token = login_resp.json()["token"]
    headers = {"X-Auth-Token": token}

    register_payload = {
        "firstname": "Charlie",
        "lastname": "Chaplin",
        "birthday": "1889-04-16T00:00:00Z",
        "city": "London",
        "streetAddress": "123 Cinema St",
        "postalCode": "12345",
        "phoneNumber": "555-0000"
    }
    register_resp = requests.post(get_url("customer-self-service-backend", "/customers"), json=register_payload, headers=headers, timeout=10)
    customer_id = register_resp.json()["customerId"]

    quote_payload = {
        "customerInfo": {
            "customerId": customer_id,
            "firstname": "Charlie",
            "lastname": "Chaplin",
            "contactAddress": {"streetAddress": "123 Cinema St", "postalCode": "12345", "city": "London"},
            "billingAddress": {"streetAddress": "123 Cinema St", "postalCode": "12345", "city": "London"}
        },
        "insuranceOptions": {
            "startDate": "2023-01-01T00:00:00Z",
            "insuranceType": "Life",
            "deductible": {"amount": 0, "currency": "USD"}
        }
    }
    quote_resp = requests.post(get_url("customer-self-service-backend", "/insurance-quote-requests"), json=quote_payload, headers=headers, timeout=10)
    assert quote_resp.status_code == 200, f"Expected 200, got {quote_resp.status_code}: {quote_resp.text}"
    quote_id = quote_resp.json()["id"]

    get_quote_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    get_quote_resp = requests.get(get_quote_url, headers=headers, timeout=10)
    assert get_quote_resp.status_code == 200, f"Expected 200, got {get_quote_resp.status_code}: {get_quote_resp.text}"

    patch_payload = {
        "status": "QUOTE_ACCEPTED",
        "expirationDate": "2024-01-01T00:00:00Z",
        "insurancePremium": {"amount": 100, "currency": "USD"},
        "policyLimit": {"amount": 10000, "currency": "USD"}
    }
    patch_url = get_url("customer-self-service-backend", f"/insurance-quote-requests/{quote_id}")
    patch_resp = requests.patch(patch_url, json=patch_payload, headers=headers, timeout=10)
    assert patch_resp.status_code == 401, f"Expected 401, got {patch_resp.status_code}: {patch_resp.text}"

    get_quote_resp2 = requests.get(get_quote_url, headers=headers, timeout=10)
    assert get_quote_resp2.status_code == 200
