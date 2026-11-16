# Tests generated in iteration 04
# Captured: 2026-06-20T13:03:07
# Count:    22
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=846  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    item_data = {"itemId": "item1", "quantity": 2, "unitPrice": 10.5}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_data, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0].get("itemId") == "item1"
    assert items[0].get("quantity") == 2

# --- id=847  name='Carts Merge Not Found Negative' ---
def test_carts_merge_not_found_negative():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=848  name='Orders End To End' ---
def test_orders_end_to_end():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json().get("id")

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    cat_item = items[0]

    item_data = {"itemId": cat_item.get("id"), "quantity": 1, "unitPrice": cat_item.get("price")}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    order_req = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer").get("username") == username

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order.get("id") == order_id

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in cust_orders)

# --- id=849  name='Orders Missing Cart Negative' ---
def test_orders_missing_cart_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street", "userID": username}
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

# --- id=850  name='Orders Invalid Address Format Negative' ---
def test_orders_invalid_address_format_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json().get("id")

    item_data = {"itemId": "item1", "quantity": 1, "unitPrice": 15.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    order_req = {
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=851  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True
    assert auth.get("orderId") == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id
    assert auths[-1].get("authorised") is True

# --- id=852  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert auths[-1].get("authorised") is False

# --- id=853  name='Shipping Request' ---
def test_shipping_request():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street"},
        "itemCount": 3,
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
    fetched_shipment = resp.json()
    assert fetched_shipment.get("orderId") == order_id
    assert fetched_shipment.get("trackingNumber") == shipment.get("trackingNumber")

# --- id=832  name='User Registration And Login' ---
def test_user_registration_and_login():
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
    customer = resp.json()
    assert customer.get("username") == username

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=833  name='User Registration Conflict Negative' ---
def test_user_registration_conflict_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=834  name='User Login Unauthorized Negative' ---
def test_user_login_unauthorized_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=835  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address = resp.json()
    assert address.get("city") == "London"
    assert address.get("id") == address_id

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card = resp.json()
    assert card.get("id") == card_id
    assert card.get("longNum", "").endswith("3456")

# --- id=836  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=837  name='User Address And Card' ---
def test_user_delete_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json().get("id")

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=838  name='User Customer Addresses And Cards' ---
def test_user_get_customer_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street", "userID": username}
    requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    requests.post(get_url("user", "/cards"), json=card_data, timeout=10)

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert len(addresses) > 0

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) > 0

# --- id=839  name='User All Addresses And Cards Empty' ---
def test_user_get_all_addresses_and_cards_empty():
    resp = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("address", [])) == 0

    resp = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("card", [])) == 0

# --- id=840  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0].get("id")
        resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        item = resp.json()
        assert item.get("id") == item_id

        resp = requests.get(get_url("catalogue", f"/catalogue/nonexistent_{uuid.uuid4().hex}"), timeout=10)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=841  name='Catalogue Image Not Found Negative' ---
def test_catalogue_image_not_found_negative():
    resp = requests.get(get_url("catalogue", f"/catalogue/images/nonexistent_{uuid.uuid4().hex}.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=842  name='Catalogue Tags' ---
def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data
    assert isinstance(tags_data["tags"], list)

# --- id=843  name='Catalogue Size' ---
def test_catalogue_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size_data = resp.json()
    assert "size" in size_data
    assert isinstance(size_data["size"], int)

# --- id=844  name='Carts Operations' ---
def test_carts_operations():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    item_data = {"itemId": "item1", "quantity": 2, "unitPrice": 10.5}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0].get("itemId") == "item1"
    assert items[0].get("quantity") == 2

    update_data = {"itemId": "item1", "quantity": 5, "unitPrice": 10.5}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/item1"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item = resp.json()
    assert item.get("quantity") == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/item1"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/item1"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=845  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {"itemId": "item1", "quantity": 2, "unitPrice": 10.5}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0
