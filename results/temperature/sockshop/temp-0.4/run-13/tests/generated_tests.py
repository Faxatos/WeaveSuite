# Tests generated in iteration 13
# Captured: 2026-06-29T23:48:16
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=416  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    # Add item to cart
    items_url = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.5
    }
    add_resp = requests.post(items_url, json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Follow-up GET items
    get_items_resp = requests.get(items_url, timeout=10)
    assert get_items_resp.status_code == 200, f"Expected 200, got {get_items_resp.status_code}: {get_items_resp.text}"
    items = get_items_resp.json()
    assert len(items) >= 1
    added_item = next((i for i in items if i["itemId"] == item_id), None)
    assert added_item is not None
    assert added_item["quantity"] == 2
    assert added_item["unitPrice"] == 15.5

    # Update item in cart
    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 15.5
    }
    update_resp = requests.patch(items_url, json=update_payload, timeout=10)
    assert update_resp.status_code == 202, f"Expected 202, got {update_resp.status_code}: {update_resp.text}"

    # Follow-up GET specific item
    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_item_resp = requests.get(item_url, timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    fetched_item = get_item_resp.json()
    assert fetched_item["quantity"] == 5

    # Delete item from cart
    del_item_resp = requests.delete(item_url, timeout=10)
    assert del_item_resp.status_code == 202, f"Expected 202, got {del_item_resp.status_code}: {del_item_resp.text}"

    # Follow-up GET specific item -> 404
    get_item_404_resp = requests.get(item_url, timeout=10)
    assert get_item_404_resp.status_code == 404, f"Expected 404, got {get_item_404_resp.status_code}: {get_item_404_resp.text}"

    # Delete cart
    cart_url = get_url("carts", f"/carts/{customer_id}")
    del_cart_resp = requests.delete(cart_url, timeout=10)
    assert del_cart_resp.status_code == 202, f"Expected 202, got {del_cart_resp.status_code}: {del_cart_resp.text}"

# --- id=417  name='Orders Creation And Search' ---
def test_orders_creation_and_search():
    username = f"user_{generate_random_string()}"

    # 1. Register user
    reg_url = get_url("user", "/register")
    requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "O", "lastName": "T"}, timeout=10)

    # 2. Add Address
    addr_url = get_url("user", "/addresses")
    addr_resp = requests.post(addr_url, json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    composite_addr_id = addr_resp.json()["id"]

    # 3. Add Card
    card_url = get_url("user", "/cards")
    card_resp = requests.post(card_url, json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    composite_card_id = card_resp.json()["id"]

    # 4. Add item to cart
    items_url = get_url("carts", f"/carts/{username}/items")
    requests.post(items_url, json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # 5. Create Order
    orders_url = get_url("orders", "/orders")
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{composite_addr_id}",
        "card": f"/cards/{composite_card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(orders_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    assert "id" in order_data
    order_id = order_data["id"]
    assert order_data["customer"]["username"] == username
    assert len(order_data["items"]) >= 1

    # Follow-up GET order
    get_order_url = get_url("orders", f"/orders/{order_id}")
    get_order_resp = requests.get(get_order_url, timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    fetched_order = get_order_resp.json()
    assert fetched_order["id"] == order_id

    # Search orders by customer
    search_url = get_url("orders", "/orders/search/customerId")
    search_resp = requests.get(search_url, params={"custId": username}, timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    search_data = search_resp.json()
    assert "_embedded" in search_data
    assert "customerOrders" in search_data["_embedded"]
    customer_orders = search_data["_embedded"]["customerOrders"]
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=418  name='Orders Creation Missing Fields 406' ---
def test_orders_creation_missing_fields_406():
    username = f"user_{generate_random_string()}"

    # Create Order with missing items URI
    orders_url = get_url("orders", "/orders")
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1",
        "card": f"/cards/{username}:1234"
        # Missing items
    }
    order_resp = requests.post(orders_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
    assert "message" in order_resp.json()

# --- id=419  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"order_{generate_random_string()}"

    # Authorize payment
    payments_url = get_url("payment-http", "/payments")
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    pay_resp = requests.post(payments_url, json=payment_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auth_data = pay_resp.json()
    assert auth_data["authorised"] is True
    assert auth_data["orderId"] == order_id

    # Follow-up GET payments for order
    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    get_pay_resp = requests.get(get_pay_url, timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert isinstance(auths, list)
    assert len(auths) >= 1
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True

# --- id=413  name='Catalogue Items And Tags' ---
def test_catalogue_get_items_and_tags():
    # Get catalogue items
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, params={"size": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list), "Expected a list of items"

    if items:
        item = items[0]
        item_id = item["id"]

        # Get specific item
        item_url = get_url("catalogue", f"/catalogue/{item_id}")
        item_resp = requests.get(item_url, timeout=10)
        assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
        fetched_item = item_resp.json()
        assert fetched_item["id"] == item_id
        assert fetched_item["name"] == item["name"]

        # Get item that does not exist (Negative)
        bad_item_url = get_url("catalogue", "/catalogue/nonexistent-id-12345")
        bad_item_resp = requests.get(bad_item_url, timeout=10)
        assert bad_item_resp.status_code == 404, f"Expected 404, got {bad_item_resp.status_code}: {bad_item_resp.text}"

    # Get tags
    tags_url = get_url("catalogue", "/tags")
    tags_resp = requests.get(tags_url, timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags_data = tags_resp.json()
    assert "tags" in tags_data

# --- id=414  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    # Register user
    reg_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(reg_url, json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    # Follow-up GET on customer
    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    cust_data = cust_resp.json()
    assert cust_data["username"] == username
    assert cust_data["email"] == email
    assert cust_data["firstName"] == "Test"
    assert cust_data["lastName"] == "User"

    # Register same user again -> 409 (Conflict)
    reg_resp_conflict = requests.post(reg_url, json=user_payload, timeout=10)
    assert reg_resp_conflict.status_code == 409, f"Expected 409, got {reg_resp_conflict.status_code}: {reg_resp_conflict.text}"

    # Login successful
    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    # Login failed (Negative)
    login_fail_resp = requests.get(login_url, auth=(username, "wrongpassword"), timeout=10)
    assert login_fail_resp.status_code == 401, f"Expected 401, got {login_fail_resp.status_code}: {login_fail_resp.text}"

    # Delete customer
    del_cust_resp = requests.delete(cust_url, timeout=10)
    assert del_cust_resp.status_code == 200, f"Expected 200, got {del_cust_resp.status_code}: {del_cust_resp.text}"
    assert del_cust_resp.json().get("status") is True

# --- id=415  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{generate_random_string()}"

    # Register user to ensure it exists
    reg_url = get_url("user", "/register")
    requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    # Add Address
    addr_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    addr_resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id_data = addr_resp.json()
    assert "id" in addr_id_data
    composite_addr_id = addr_id_data["id"]

    # Follow-up GET address
    get_addr_url = get_url("user", f"/addresses/{composite_addr_id}")
    get_addr_resp = requests.get(get_addr_url, timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    fetched_addr = get_addr_resp.json()
    assert fetched_addr["city"] == "Test City"
    assert fetched_addr["street"] == "Test Street"

    # Follow-up GET customer addresses
    cust_addr_url = get_url("user", f"/customers/{username}/addresses")
    cust_addr_resp = requests.get(cust_addr_url, timeout=10)
    assert cust_addr_resp.status_code == 200, f"Expected 200, got {cust_addr_resp.status_code}: {cust_addr_resp.text}"
    cust_addr_data = cust_addr_resp.json()
    assert "_embedded" in cust_addr_data
    assert "address" in cust_addr_data["_embedded"]
    assert any(a.get("id") == composite_addr_id for a in cust_addr_data["_embedded"]["address"])

    # Add Card
    card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id_data = card_resp.json()
    assert "id" in card_id_data
    composite_card_id = card_id_data["id"]

    # Follow-up GET card
    get_card_url = get_url("user", f"/cards/{composite_card_id}")
    get_card_resp = requests.get(get_card_url, timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    fetched_card = get_card_resp.json()
    assert fetched_card["expires"] == "12/25"
    assert "3456" in fetched_card["longNum"] # Masked card check

    # Follow-up GET customer cards
    cust_card_url = get_url("user", f"/customers/{username}/cards")
    cust_card_resp = requests.get(cust_card_url, timeout=10)
    assert cust_card_resp.status_code == 200, f"Expected 200, got {cust_card_resp.status_code}: {cust_card_resp.text}"
    cust_card_data = cust_card_resp.json()
    assert "_embedded" in cust_card_data
    assert "card" in cust_card_data["_embedded"]
    assert any(c.get("id") == composite_card_id for c in cust_card_data["_embedded"]["card"])

    # Delete Address
    del_addr_resp = requests.delete(get_addr_url, timeout=10)
    assert del_addr_resp.status_code == 200, f"Expected 200, got {del_addr_resp.status_code}: {del_addr_resp.text}"

    # Delete Card
    del_card_resp = requests.delete(get_card_url, timeout=10)
    assert del_card_resp.status_code == 200, f"Expected 200, got {del_card_resp.status_code}: {del_card_resp.text}"

# --- id=420  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = f"order_{generate_random_string()}"

    # Authorize payment with amount > 100 (Boundary/Limit test)
    payments_url = get_url("payment-http", "/payments")
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    pay_resp = requests.post(payments_url, json=payment_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auth_data = pay_resp.json()
    assert auth_data["authorised"] is False

    # Follow-up GET payments for order
    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    get_pay_resp = requests.get(get_pay_url, timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert len(auths) >= 1
    assert auths[-1]["authorised"] is False

# --- id=421  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"order_{generate_random_string()}"

    # Create shipment
    shipping_url = get_url("shipping-http", "/shipping")
    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    ship_resp = requests.post(shipping_url, json=shipping_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    ship_data = ship_resp.json()
    assert ship_data["orderId"] == order_id
    assert "trackingNumber" in ship_data

    # Follow-up GET shipment
    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    get_ship_resp = requests.get(get_ship_url, timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"
    fetched_ship = get_ship_resp.json()
    assert fetched_ship["orderId"] == order_id
    assert fetched_ship["trackingNumber"] == ship_data["trackingNumber"]
