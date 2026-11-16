# Tests generated in iteration 04
# Captured: 2026-06-20T03:33:44
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=701  name='User Registration And Login' ---
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

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer["username"] == username
    assert customer["firstName"] == "Test"
    assert "password" not in customer or customer["password"] != password

    # Conflict: Register again
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # Login Success
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login Failure
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=702  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add Address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Follow-up GET Address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address = resp.json()
    assert address["city"] == "London"
    assert address["postcode"] == "SW1A 1AA"

    # Add Address again (no-op)
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == address_id

    # Add Card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Follow-up GET Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card = resp.json()
    assert card["expires"] == "12/25"
    assert card["longNum"].endswith("3456")
    assert "1234567890" not in card["longNum"]

    # Get all addresses for customer
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert len(addresses) == 1
    assert addresses[0]["id"] == address_id

    # Get all cards for customer
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 1
    assert cards[0]["id"] == card_id

    # Test the quirk: GET /addresses always returns empty
    resp = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("address", [])) == 0

    # Test the quirk: GET /cards always returns empty
    resp = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("card", [])) == 0

    # Delete Address
    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Delete Card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=703  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    # Get tags
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data
    tags = tags_data["tags"]

    if tags:
        tag = tags[0]
        resp = requests.get(get_url("catalogue", "/catalogue"), params={"tags": tag}, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        items = resp.json()

        # Get size
        resp = requests.get(get_url("catalogue", "/catalogue/size"), params={"tags": tag}, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        size_data = resp.json()
        assert size_data["size"] == len(items)

        if items:
            item_id = items[0]["id"]
            # Get specific item
            resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
            assert resp.json()["id"] == item_id

            # Get image
            if items[0].get("imageUrl"):
                image_url = items[0]["imageUrl"][0]
                image_name = image_url.split("/")[-1]
                resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
                assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Negative: non-existent item
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_item_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=704  name='Catalogue And Carts' ---
def test_catalogue_and_carts():
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add Item to Cart
    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Follow-up GET Cart Items
    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 1

    # Update Item in Cart
    cart_item_update = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": unit_price
    }
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=cart_item_update, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET specific item
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    updated_item = resp.json()
    assert updated_item["quantity"] == 3

    # Delete Item from Cart
    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET specific item -> 404
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete Cart
    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=705  name='Cart Merge' ---
def test_cart_merge():
    session_id = f"anon_{uuid.uuid4().hex[:8]}"
    customer_id = f"user_{uuid.uuid4().hex[:8]}"

    items = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10).json()
    item = items[0]
    cart_item = {"itemId": item["id"], "quantity": 2, "unitPrice": item["price"]}

    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Merge into customer cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": session_id}, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET customer cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    merged_items = resp.json()
    assert len(merged_items) == 1
    assert merged_items[0]["itemId"] == item["id"]
    assert merged_items[0]["quantity"] == 2

    # Negative: merge non-existent session cart
    bad_session = "nonexistent_session"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": bad_session}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=706  name='Carts Async' ---
def test_carts_async():
    username = f"user_{uuid.uuid4().hex[:8]}"
    items = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10).json()
    item = items[0]

    resp = requests.post(get_url("carts", f"/carts-async/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts-async/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["customerId"] == username

    resp = requests.delete(get_url("carts", f"/carts-async/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=707  name='E2e Order Placement' ---
def test_e2e_order_placement():
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

    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    cart_item = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    assert order["customer"]["username"] == username
    assert order["address"]["city"] == "London"
    assert order["card"]["longNum"].endswith("3456")
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item_id
    assert order["items"][0]["quantity"] == 2
    assert abs(order["total"] - (2 * unit_price)) < 0.01
    assert order["payment"]["authorised"] is True
    assert "carrier" in order["shipment"]
    assert order["status"] in ["CREATED", "PAID", "SHIPPED"]

    # Follow-up GET Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["total"] == order["total"]
    assert fetched_order["status"] == order["status"]

    # Check Payment
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) == 1
    assert payments[0]["orderId"] == order_id
    assert payments[0]["authorised"] is True

    # Check Shipping
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert shipment["carrier"] == order["shipment"]["carrier"]
    assert shipment["trackingNumber"] == order["shipment"]["trackingNumber"]

# --- id=708  name='Order Placement Failures' ---
def test_order_placement_failures():
    username = f"user_{uuid.uuid4().hex[:8]}"

    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street", "userID": username}
    address_id = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10).json()["id"]

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_data, timeout=10).json()["id"]

    # 1. Missing required fields (empty cart) -> 406
    order_req_empty_cart = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req_empty_cart, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

    # Add item to cart
    items = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10).json()
    item = items[0]
    cart_item = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    # 2. Malformed URI -> 404
    order_req_malformed = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format", 
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req_malformed, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # 3. Wrong prefix -> 406
    order_req_wrong_prefix = {
        "customer": f"/customers/{username}",
        "address": f"/wrongprefix/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req_wrong_prefix, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # 4. Payment declined (total > 100) -> 406
    expensive_item = {"itemId": item["id"], "quantity": 100, "unitPrice": 50.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=expensive_item, timeout=10)

    order_req_expensive = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req_expensive, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=709  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing Street", "userID": username}
    address_id = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10).json()["id"]

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_data, timeout=10).json()["id"]

    items = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10).json()
    item = items[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10).json()
    order_id = order["id"]

    payment_address = {
        "city": address_data["city"],
        "country": address_data["country"],
        "number": address_data["number"],
        "postcode": address_data["postcode"],
        "street": address_data["street"]
    }
    payment_card = {
        "ccv": card_data["ccv"],
        "expires": card_data["expires"],
        "longNum": card_data["longNum"]
    }

    payment_req_declined = {
        "address": payment_address,
        "amount": 150.0,
        "card": payment_card,
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req_declined, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    authorizations = resp.json()
    assert len(authorizations) >= 2
    assert authorizations[-1]["authorised"] is False

    shipping_req = {
        "address": payment_address,
        "itemCount": 5,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id

# --- id=710  name='Orders Search' ---
def test_orders_search():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    address_id = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S", "userID": username}, timeout=10).json()["id"]
    card_id = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10).json()["id"]

    items = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10).json()
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": items[0]["id"], "quantity": 1, "unitPrice": items[0]["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10).json()

    resp = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    search_results = resp.json()
    assert "_embedded" in search_results
    customer_orders = search_results["_embedded"]["customerOrders"]
    assert len(customer_orders) == 1
    assert customer_orders[0]["id"] == order["id"]

    resp = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": "nonexistent_user_123"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=711  name='User Deletion' ---
def test_user_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is False

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    empty_customer = resp.json()
    assert empty_customer["username"] == username
    assert "firstName" not in empty_customer or not empty_customer["firstName"]

# --- id=712  name='All Customers' ---
def test_get_all_customers():
    resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
