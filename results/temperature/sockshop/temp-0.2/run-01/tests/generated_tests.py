# Tests generated in iteration 01
# Captured: 2026-06-29T00:20:07
# Count:    24
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1  name='User Register And' ---
def test_user_register_and_get():
    username = random_string()
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("username") == username
    assert data.get("email") == payload["email"]
    assert data.get("firstName") == payload["firstName"]
    assert data.get("lastName") == payload["lastName"]

# --- id=2  name='User Register Conflict' ---
def test_user_register_conflict():
    username = random_string()
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=3  name='User Login Success' ---
def test_user_login_success():
    username = random_string()
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=4  name='User Login Failure' ---
def test_user_login_failure():
    username = random_string()
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=5  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Metropolis",
        "postcode": "12345",
        "country": "USA"
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None
    assert address_id.startswith(f"{username}:")

    resp_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    addresses = data.get("_embedded", {}).get("address", [])
    assert any(addr.get("id") == address_id for addr in addresses)

# --- id=6  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {
        "userID": username,
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123"
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None
    assert card_id.startswith(f"{username}:")

    resp_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    cards = data.get("_embedded", {}).get("card", [])
    assert any(card.get("id") == card_id for card in cards)

# --- id=7  name='User Customer' ---
def test_user_delete_customer():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_again.status_code == 200, f"Expected 200, got {resp_again.status_code}: {resp_again.text}"
    assert resp_again.json().get("status") is False

# --- id=8  name='User Address' ---
def test_user_delete_address():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {"userID": username, "number": "123", "street": "Main", "city": "City", "postcode": "12345", "country": "USA"}
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    address_id = resp.json().get("id")

    del_resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_resp.status_code == 200
    addresses = get_resp.json().get("_embedded", {}).get("address", [])
    assert not any(addr.get("id") == address_id for addr in addresses)

# --- id=9  name='User Card' ---
def test_user_delete_card():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {"userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    card_id = resp.json().get("id")

    del_resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert get_resp.status_code == 200
    cards = get_resp.json().get("_embedded", {}).get("card", [])
    assert not any(card.get("id") == card_id for card in cards)

# --- id=10  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 9.99
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert any(item.get("itemId") == item_id and item.get("quantity") == 2 for item in cart_items)

# --- id=11  name='Carts Update Item And' ---
def test_carts_update_item_and_get():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 5.0}
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=update_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 5

# --- id=12  name='Carts Item' ---
def test_carts_delete_item():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=13  name='Carts Cart' ---
def test_carts_delete_cart():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

# --- id=14  name='Catalogue Items' ---
def test_catalogue_get_items():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)

# --- id=15  name='Catalogue Size' ---
def test_catalogue_get_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

# --- id=16  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=17  name='Catalogue Image' ---
def test_catalogue_get_image():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if items and items[0].get("imageUrl"):
        image_path = items[0]["imageUrl"][0]
        image_name = image_path.split("/")[-1]
        resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=18  name='Orders Create And' ---
def test_orders_create_and_get():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "John", "lastName": "Doe", "email": "j@d.com"}, timeout=10)

    addr_payload = {"userID": username, "number": "123", "street": "Main", "city": "City", "postcode": "12345", "country": "USA"}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    address_id = addr_resp.json().get("id")

    card_payload = {"userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = card_resp.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    item_price = cat_resp.json()[0]["price"]

    cart_payload = {"itemId": item_id, "quantity": 2, "unitPrice": item_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("id") == order_id
    assert get_data.get("customer", {}).get("username") == username

# --- id=19  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "John", "lastName": "Doe", "email": "j@d.com"}, timeout=10)
    payload = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=20  name='Orders Create Invalid Composite Id' ---
def test_orders_create_invalid_composite_id():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "John", "lastName": "Doe", "email": "j@d.com"}, timeout=10)

    cart_payload = {"itemId": "item1", "quantity": 2, "unitPrice": 15.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)

    payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=21  name='Orders Customer Orders' ---
def test_orders_get_customer_orders():
    order_id, username = create_full_order()

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    orders = data.get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders)

# --- id=22  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id, username = create_full_order()
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"number": "123", "street": "Main", "city": "City", "postcode": "12345", "country": "USA"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is True
    assert auth_data.get("orderId") == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id
    assert auths[-1].get("authorised") is True

# --- id=23  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id, username = create_full_order()
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"number": "123", "street": "Main", "city": "City", "postcode": "12345", "country": "USA"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is False

# --- id=24  name='Shipping Ship And' ---
def test_shipping_ship_and_get():
    order_id, username = create_full_order()
    payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {
            "number": "123",
            "street": "Main",
            "city": "City",
            "postcode": "12345",
            "country": "USA"
        }
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    ship_data = resp.json()
    assert ship_data.get("orderId") == order_id
    assert "trackingNumber" in ship_data

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("orderId") == order_id
    assert get_data.get("trackingNumber") == ship_data.get("trackingNumber")
