# Tests generated in iteration 05
# Captured: 2026-06-04T18:53:33
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=308  name='Orders E2e Placement Payment Declined' ---
def test_orders_e2e_placement_payment_declined():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Jane",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET for User
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Add Address
    address_data = {
        "city": "Paris",
        "country": "France",
        "number": "5",
        "postcode": "75001",
        "street": "Rue de Rivoli",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Follow-up GET for Address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Add Card
    card_data = {
        "ccv": "456",
        "expires": "11/26",
        "longNum": "9876543210987654",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Follow-up GET for Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 4. Get Catalogue Item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0, "Catalogue is empty"
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    # 5. Add to Cart with large quantity to exceed 100.00
    quantity = int(101.0 // sock_price) + 1 if sock_price > 0 else 1000
    item_data = {
        "itemId": sock_id,
        "quantity": quantity,
        "unitPrice": sock_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Follow-up GET for Cart Item
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 6. Place Order - Expect 406 Not Acceptable
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=309  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Get Catalogue Item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0, "Catalogue is empty"
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    # 1. Add Item
    item_data = {
        "itemId": sock_id,
        "quantity": 2,
        "unitPrice": sock_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_item = resp.json()
    assert resp_item["itemId"] == item_data["itemId"]
    assert resp_item["quantity"] == item_data["quantity"]
    assert resp_item["unitPrice"] == item_data["unitPrice"]

    # Follow-up GET
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_item = resp.json()
    assert cart_item["itemId"] == item_data["itemId"]
    assert cart_item["quantity"] == item_data["quantity"]
    assert cart_item["unitPrice"] == item_data["unitPrice"]

    # 2. Update Item
    item_data["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_item = resp.json()
    assert cart_item["quantity"] == 5, f"Expected 5, got {cart_item.get('quantity')}"

    # 3. Delete Item
    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # 4. Delete Cart
    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0, "Expected cart to be empty after deletion"

# --- id=310  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Alice",
        "lastName": "Smith"
    }

    # 1. Register User
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Duplicate Registration
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=311  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    # 1. Get all tags
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data
    tags = tags_data["tags"]
    assert len(tags) > 0, "No tags found"

    # 2. Get size for a tag
    tag = tags[0]
    resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size_data = resp.json()
    assert "size" in size_data

    # 3. Get catalogue items
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0, "Catalogue is empty"

    # 4. Get specific item
    sock_id = socks[0]["id"]
    resp = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    sock = resp.json()
    assert sock["id"] == sock_id

# --- id=312  name='User Resource Deletion' ---
def test_user_resource_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Bob",
        "lastName": "Builder"
    }

    # Register User
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    address_data = {
        "city": "Berlin",
        "country": "Germany",
        "number": "1",
        "postcode": "10115",
        "street": "Mitte",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Follow-up GET
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == address_id for a in addresses), "Address not found in listing"

    # Delete Address
    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Address Deletion via listing
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses), "Address still found in listing"

    # Delete User
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify User Deletion via listing
    resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert username not in resp.text, "User still found in listing"

# --- id=307  name='Orders E2e Placement Successful' ---
def test_orders_e2e_placement_successful():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET for User
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Add Address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Follow-up GET for Address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_resp = resp.json()
    assert addr_resp["city"] == address_data["city"], f"Expected {address_data['city']}, got {addr_resp.get('city')}"
    assert addr_resp["country"] == address_data["country"], f"Expected {address_data['country']}, got {addr_resp.get('country')}"
    assert addr_resp["number"] == address_data["number"], f"Expected {address_data['number']}, got {addr_resp.get('number')}"
    assert addr_resp["postcode"] == address_data["postcode"], f"Expected {address_data['postcode']}, got {addr_resp.get('postcode')}"
    assert addr_resp["street"] == address_data["street"], f"Expected {address_data['street']}, got {addr_resp.get('street')}"

    # 3. Add Card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Follow-up GET for Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_resp = resp.json()
    assert card_resp["ccv"] == card_data["ccv"], f"Expected {card_data['ccv']}, got {card_resp.get('ccv')}"
    assert card_resp["expires"] == card_data["expires"], f"Expected {card_data['expires']}, got {card_resp.get('expires')}"

    # 4. Get Catalogue Item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0, "Catalogue is empty"
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    # 5. Add to Cart
    item_data = {
        "itemId": sock_id,
        "quantity": 1,
        "unitPrice": sock_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_item = resp.json()
    assert resp_item["itemId"] == item_data["itemId"]
    assert resp_item["quantity"] == item_data["quantity"]
    assert resp_item["unitPrice"] == item_data["unitPrice"]

    # Follow-up GET for Cart Item
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_item = resp.json()
    assert cart_item["itemId"] == item_data["itemId"], f"Expected {item_data['itemId']}, got {cart_item.get('itemId')}"
    assert cart_item["quantity"] == item_data["quantity"], f"Expected {item_data['quantity']}, got {cart_item.get('quantity')}"
    assert cart_item["unitPrice"] == item_data["unitPrice"], f"Expected {item_data['unitPrice']}, got {cart_item.get('unitPrice')}"

    # 6. Place Order
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
    assert order["payment"]["authorised"] is True, "Expected payment to be authorised"

    # Follow-up GET for Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id, f"Expected {order_id}, got {fetched_order.get('id')}"
    assert fetched_order["payment"]["authorised"] is True, "Expected payment to be authorised"

    # Verify Payment was created for this order
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0, "Expected payment record to exist"
    assert payments[0]["orderId"] == order_id
    assert payments[0]["authorised"] is True

    # Verify Shipment was created for this order
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment
