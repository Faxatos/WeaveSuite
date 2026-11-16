# Tests generated in iteration 07
# Captured: 2026-06-21T06:16:36
# Count:    17
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1166  name='User Registration And Retrieval' ---
def test_user_registration_and_retrieval():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("username") == username

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=1167  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=1168  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1169  name='User Address Lifecycle' ---
def test_user_address_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    created_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/addresses/{created_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("city") == "London"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == created_id for a in addresses)

    resp = requests.delete(get_url("user", f"/addresses/{created_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == created_id for a in addresses)

# --- id=1170  name='User Card Lifecycle' ---
def test_user_card_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    created_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/cards/{created_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("expires") == "12/25"
    assert resp.json().get("longNum") == "************3456"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == created_id for c in cards)

    resp = requests.delete(get_url("user", f"/cards/{created_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == created_id for c in cards)

# --- id=1171  name='Catalogue Queries' ---
def test_catalogue_queries():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags = resp.json().get("tags", [])
    if not tags:
        pytest.skip("No tags found")
    tag = tags[0]

    resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()

    resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("size") == len(items)

    if items:
        item_id = items[0].get("id")
        resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json().get("id") == item_id

        image_urls = items[0].get("imageUrl", [])
        if image_urls:
            image_name = image_urls[0].split("/")[-1]
            resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=1172  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    invalid_id = f"invalid_{uuid.uuid4().hex}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", f"/catalogue/images/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1173  name='Carts Item Lifecycle' ---
def test_carts_item_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_data = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert any(i.get("itemId") == item_id and i.get("quantity") == 2 for i in resp.json())

    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 4

    patch_data = {"itemId": item_id, "quantity": 10, "unitPrice": unit_price}
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 10

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert not any(i.get("itemId") == item_id for i in resp.json())

# --- id=1174  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_data = {"itemId": item_id, "quantity": 3, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert any(i.get("itemId") == item_id and i.get("quantity") == 3 for i in resp.json())

# --- id=1175  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    invalid_session = f"sess_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={invalid_session}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1176  name='Carts' ---
def test_carts_delete():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=1177  name='Orders End To End' ---
def test_orders_end_to_end():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "John", "lastName": "Doe", "email": "john@example.com"}, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json().get("id")

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": unit_price}, timeout=10)

    order_req = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    retrieved_order = resp.json()
    assert retrieved_order.get("id") == order_id
    assert retrieved_order.get("customer", {}).get("username") == username
    assert retrieved_order.get("total") == 2 * unit_price

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=1178  name='Orders Missing Cart 406' ---
def test_orders_missing_cart_406():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json().get("id")

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json().get("id")

    order_req = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1179  name='Orders Invalid Uri 404' ---
def test_orders_invalid_uri_404():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "address": "/addresses/invalid_format",
        "card": "/cards/invalid_format",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1180  name='Payment Authorization' ---
def test_payment_authorization():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json().get("id")

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)

    order_req = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")

    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    initial_auths_count = len(resp.json())

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True
    assert auth.get("orderId") == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    new_auths = resp.json()
    assert len(new_auths) == initial_auths_count + 1
    assert new_auths[-1].get("authorised") is True
    assert new_auths[-1].get("orderId") == order_id

# --- id=1181  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json().get("id")

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)

    order_req = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")

    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    initial_auths_count = len(resp.json())

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    new_auths = resp.json()
    assert len(new_auths) == initial_auths_count + 1
    assert new_auths[-1].get("authorised") is False

# --- id=1182  name='Shipping Lifecycle' ---
def test_shipping_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json().get("id")

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)

    order_req = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")

    shipping_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"},
        "itemCount": 1,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id
    assert shipment.get("carrier") is not None
    assert shipment.get("trackingNumber") is not None

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    retrieved = resp.json()
    assert retrieved.get("orderId") == order_id
    assert retrieved.get("carrier") == shipment.get("carrier")
    assert retrieved.get("trackingNumber") == shipment.get("trackingNumber")
