# Tests generated in iteration 13
# Captured: 2026-06-30T16:40:11
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=650  name='User Registration And Login' ---
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

    # Register user
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Conflict: Register same user
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # Login via Basic Auth
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify user details via GET
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("email") == user_data["email"]
    assert customer.get("firstName") == user_data["firstName"]
    assert customer.get("lastName") == user_data["lastName"]
    assert "password" not in customer

# --- id=651  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add Address
    addr_req = {
        "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street", "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id_full = resp.json()["id"]

    # List Addresses
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Get Specific Address
    resp = requests.get(get_url("user", f"/addresses/{address_id_full}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_fetched = resp.json()
    assert addr_fetched["city"] == "City"

    # Add Card
    card_req = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id_full = resp.json()["id"]

    # List Cards
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Get Specific Card
    resp = requests.get(get_url("user", f"/cards/{card_id_full}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_fetched = resp.json()
    assert "1234567890123456" not in card_fetched.get("longNum", "")

    # Delete Address
    resp = requests.delete(get_url("user", f"/addresses/{address_id_full}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Delete Card
    resp = requests.delete(get_url("user", f"/cards/{card_id_full}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=652  name='Carts Add Update' ---
def test_carts_add_update_delete():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    customer_id = username

    # Get an item from catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add to cart
    cart_item = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

    # Update item in cart
    updated_item = {"itemId": item_id, "quantity": 5, "unitPrice": unit_price}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=updated_item, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["quantity"] == 5

    # Delete item from cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify delete
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete whole cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=653  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    customer_id = username

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    items = resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add to anonymous session cart
    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_item, timeout=10)

    # Merge into customer cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": session_id}, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify merged content
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert any(i["itemId"] == item_id for i in cart_items)

    # Merge non-existent session cart
    bad_session = f"bad_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": bad_session}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=654  name='End To End Order Placement' ---
def test_end_to_end_order_placement():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_req = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    address_id_full = resp.json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id_full = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    items = resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Place the order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id_full}",
        "card": f"/cards/{card_id_full}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    # Validate Order response
    assert order["customer"]["username"] == username
    assert order["total"] == unit_price * 1
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item_id
    assert order["payment"]["authorised"] is True

    # Fetch Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id

    # Verify Payment side-effect
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id
    assert payments[0]["authorised"] is True

    # Verify Shipping side-effect
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    # Search orders by customer
    resp = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    embedded = resp.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert len(customer_orders) > 0
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=655  name='Order Creation Invalid Uris' ---
def test_order_creation_invalid_uris():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Invalid composite ID for address (404)
    order_req = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format_no_colon",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Invalid prefix for address (406)
    order_req["address"] = f"/wrongprefix/{username}:1"
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=656  name='Direct Payment And Shipping' ---
def test_direct_payment_and_shipping():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    # Valid Payment
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "11/22", "longNum": "1234123412341234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    # Verify recorded payment
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) == 1
    assert payments[0]["authorised"] is True

    # Payment over limit (> 100)
    payment_req["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is False

    # Shipping
    shipping_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    # Verify recorded shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment["orderId"] == order_id

# --- id=657  name='Catalogue Size And Images' ---
def test_catalogue_size_and_images():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

    # Fetch image for an existing item
    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if len(items) > 0 and len(items[0].get("imageUrl", [])) > 0:
        image_path = items[0]["imageUrl"][0]
        image_name = image_path.split("/")[-1]

        resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        # Non-existent image
        resp = requests.get(get_url("catalogue", "/catalogue/images/nonexistent_image.jpg"), timeout=10)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=658  name='Customer Deletion' ---
def test_customer_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Delete non-existent customer
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is False

    # Register and delete existing customer
    user_data = {
        "username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

# --- id=659  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/non_existent_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=660  name='Orders Search By Customer Not Found' ---
def test_orders_search_by_customer_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
