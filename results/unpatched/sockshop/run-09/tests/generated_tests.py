# Tests generated in iteration 09
# Captured: 2026-07-10T19:14:34
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=83  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=84  name='User Login Negative' ---
def test_user_login_negative():
    resp = requests.get(get_url("user", "/login"), auth=("wronguser", "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=85  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_data = resp.json()

    address_id = None
    if isinstance(addr_data, dict) and "_embedded" in addr_data:
        address_id = addr_data["_embedded"]["address"][0].get("addressId", addr_data["_embedded"]["address"][0].get("id"))
    elif isinstance(addr_data, list) and len(addr_data) > 0:
        address_id = addr_data[0].get("addressId", addr_data[0].get("id"))

    if isinstance(address_id, dict):
        address_id = address_id.get("addressId")

    if address_id:
        resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_data = resp.json()

    card_id = None
    if isinstance(card_data, dict) and "_embedded" in card_data:
        card_id = card_data["_embedded"]["card"][0].get("cardId", card_data["_embedded"]["card"][0].get("id"))
    elif isinstance(card_data, list) and len(card_data) > 0:
        card_id = card_data[0].get("cardId", card_data[0].get("id"))

    if isinstance(card_id, dict):
        card_id = card_id.get("cardId")

    if card_id:
        resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=86  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0

    item_id = items[0]["id"]

    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

    resp = requests.get(get_url("catalogue", "/catalogue/non-existent-id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=87  name='Catalogue Images' ---
def test_catalogue_images():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0

    image_urls = items[0].get("imageUrl", [])
    if image_urls:
        image_path = image_urls[0]
        image_name = image_path.split("/")[-1]

        resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue/images/non-existent-image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=88  name='Carts Add' ---
def test_carts_add_get_delete():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

    item_payload["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=89  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) >= 1
    assert any(item["itemId"] == item_id for item in cart_items)

    bad_session_id = f"sess_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={bad_session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=90  name='Carts Negative' ---
def test_carts_negative():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/non-existent-item"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=91  name='Order Workflow' ---
def test_order_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    addr_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_data = addr_resp.json()
    address_id = None
    if isinstance(addr_data, dict) and "_embedded" in addr_data:
        address_id = addr_data["_embedded"]["address"][0].get("addressId", addr_data["_embedded"]["address"][0].get("id"))
    elif isinstance(addr_data, list) and len(addr_data) > 0:
        address_id = addr_data[0].get("addressId", addr_data[0].get("id"))

    if isinstance(address_id, dict):
        address_id = address_id.get("addressId", "")

    card_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_data = card_resp.json()
    card_id = None
    if isinstance(card_data, dict) and "_embedded" in card_data:
        card_id = card_data["_embedded"]["card"][0].get("cardId", card_data["_embedded"]["card"][0].get("id"))
    elif isinstance(card_data, list) and len(card_data) > 0:
        card_id = card_data[0].get("cardId", card_data[0].get("id"))

    if isinstance(card_id, dict):
        card_id = card_id.get("cardId", "")

    addr_uri = get_url("user", f"/addresses/{address_id}") if address_id else get_url("user", "/addresses")
    card_uri = get_url("user", f"/cards/{card_id}") if card_id else get_url("user", "/cards")

    order_payload = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": addr_uri,
        "card": card_uri,
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_id = None
    try:
        order_data = resp.json()
        order_id = order_data.get("id")
    except Exception:
        pass

    if not order_id:
        resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        orders_data = resp.json()
        if isinstance(orders_data, dict) and "_embedded" in orders_data:
            if len(orders_data["_embedded"]["customerOrders"]) > 0:
                order_id = orders_data["_embedded"]["customerOrders"][0].get("id")
        elif isinstance(orders_data, list) and len(orders_data) > 0:
            order_id = orders_data[0].get("id")

    if order_id:
        resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        payment_req = {
            "address": {
                "city": "London",
                "country": "UK",
                "number": "10",
                "postcode": "W1",
                "street": "Baker St"
            },
            "amount": unit_price,
            "card": {
                "ccv": "123",
                "expires": "12/25",
                "longNum": "1234567890123456"
            },
            "customer": {
                "firstName": "John",
                "lastName": "Doe"
            },
            "orderId": order_id
        }
        resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        shipping_req = {
            "address": {
                "city": "London",
                "country": "UK",
                "number": "10",
                "postcode": "W1",
                "street": "Baker St"
            },
            "itemCount": 1,
            "orderId": order_id
        }
        resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=92  name='Orders Negative' ---
def test_orders_negative():
    resp = requests.get(get_url("orders", "/orders/non-existent-order-id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("orders", "/orders/search/customerId?custId=non-existent-customer"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
