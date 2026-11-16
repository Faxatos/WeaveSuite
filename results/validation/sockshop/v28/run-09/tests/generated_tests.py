# Tests generated in iteration 09
# Captured: 2026-06-21T07:37:58
# Count:    24
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1197  name='Catalogue Image' ---
def test_catalogue_get_image():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    if items[0].get("imageUrl") and len(items[0]["imageUrl"]) > 0:
        image_url = items[0]["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=1198  name='User Register And Login' ---
def test_user_register_and_login():
    username = generate_username()
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    auth = (username, password)
    resp_login = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1199  name='User Register Conflict' ---
def test_user_register_conflict():
    username = generate_username()
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp1 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1200  name='User Add Address' ---
def test_user_add_address():
    username, _ = create_user()
    payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addr_data = resp_get.json()
    assert addr_data["city"] == "Test City"
    assert addr_data["id"] == address_id

    resp_cust = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    addresses = resp_cust.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == address_id for a in addresses)

# --- id=1201  name='User Address' ---
def test_user_delete_address():
    username, _ = create_user()
    payload = {
        "city": "Test City", "country": "Test Country", "number": "123",
        "postcode": "12345", "street": "Test Street", "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp_del = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    addresses = resp_cust.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == address_id for a in addresses)

# --- id=1202  name='User Add Card' ---
def test_user_add_card():
    username, _ = create_user()
    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    card_data = resp_get.json()
    assert card_data["id"] == card_id
    assert card_data["longNum"].endswith("3456")
    assert "*" in card_data["longNum"]

    resp_cust = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    cards = resp_cust.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in cards)

# --- id=1203  name='User Card' ---
def test_user_delete_card():
    username, _ = create_user()
    payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    cards = resp_cust.json().get("_embedded", {}).get("card", [])
    assert not any(c["id"] == card_id for c in cards)

# --- id=1204  name='User Customer' ---
def test_user_delete_customer():
    username, _ = create_user()
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json()["status"] is False

# --- id=1205  name='Carts Add And Item' ---
def test_carts_add_and_get_item():
    customer_id = generate_username()
    item_id = get_valid_item_id()
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 2 for i in items)

    resp_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["itemId"] == item_id

# --- id=1206  name='Carts Add Item Increment' ---
def test_carts_add_item_increment():
    customer_id = generate_username()
    item_id = get_valid_item_id()
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"

    resp_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["quantity"] == 4

# --- id=1207  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = generate_username()
    item_id = get_valid_item_id()
    payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.5
    }
    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    payload_update = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 10.5
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=payload_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["quantity"] == 5

# --- id=1208  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = generate_username()
    item_id = get_valid_item_id()
    payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.5
    }
    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item.status_code == 404, f"Expected 404, got {resp_item.status_code}: {resp_item.text}"

# --- id=1209  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = generate_username()
    item_id = get_valid_item_id()
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

# --- id=1210  name='Carts Merge' ---
def test_carts_merge():
    session_id = generate_username()
    customer_id = generate_username()
    item_id = get_valid_item_id()
    payload = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": 15.0
    }
    resp1 = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=payload, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 3 for i in items)

# --- id=1211  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = generate_username()
    session_id = generate_username()

    item_id = get_valid_item_id()
    resp1 = requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{session_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=1212  name='Orders Create And' ---
def test_orders_create_and_get():
    username, _ = create_user()

    addr_payload = {
        "city": "Test City", "country": "Test Country", "number": "123",
        "postcode": "12345", "street": "Test Street", "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json()["id"]

    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    item_id = get_valid_item_id()
    cart_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.0}
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    order_payload = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]
    assert order_data["customer"]["username"] == username
    assert order_data["total"] == 20.0
    assert order_data["status"] in ["CREATED", "PAID", "SHIPPED"]

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders)

# --- id=1213  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username, _ = create_user()

    item_id = get_valid_item_id()
    cart_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.0}
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1214  name='Orders Create Invalid Uri' ---
def test_orders_create_invalid_uri():
    username, _ = create_user()

    item_id = get_valid_item_id()
    cart_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.0}
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    order_payload = {
        "address": f"/addresses/{username}_invalid",
        "card": f"/cards/{username}_invalid",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=1215  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = create_order_id()
    payload = {
        "address": {
            "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "First", "lastName": "Last"
        },
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data["authorised"] is True
    assert auth_data["orderId"] == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert any(a["orderId"] == order_id for a in auths)

# --- id=1216  name='Payment Authorize Multiple' ---
def test_payment_authorize_multiple():
    order_id = create_order_id()
    payload = {
        "address": {
            "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "First", "lastName": "Last"
        },
        "orderId": order_id
    }
    resp1 = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 3

# --- id=1217  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = create_order_id()
    payload = {
        "address": {
            "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"
        },
        "amount": 150.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "First", "lastName": "Last"
        },
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data["authorised"] is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert any(a["authorised"] is False for a in auths)

# --- id=1218  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = create_order_id()
    payload = {
        "address": {
            "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id

# --- id=1195  name='Catalogue Items' ---
def test_catalogue_get_items():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

# --- id=1196  name='Catalogue Size And Tags' ---
def test_catalogue_get_size_and_tags():
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags = resp_tags.json().get("tags", [])
    assert isinstance(tags, list)

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()
