# Tests generated in iteration 08
# Captured: 2026-06-20T06:10:20
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=759  name='User Registration And Authentication' ---
def test_user_registration_and_authentication():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=760  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "number": "123",
        "street": "Main St",
        "city": "Springfield",
        "postcode": "12345",
        "country": "USA",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None, "Expected address id in response"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == address_id for a in addresses), "Added address not found in customer addresses"

    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None, "Expected card id in response"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), "Added card not found in customer cards"

# --- id=761  name='Catalogue And Cart Workflow' ---
def test_catalogue_and_cart_workflow():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0, "Catalogue is empty"
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    customer_id = f"cust_{generate_random_string()}"

    item_payload = {
        "itemId": sock_id,
        "quantity": 2,
        "unitPrice": sock_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1, "Expected 1 item in cart"
    assert items[0]["itemId"] == sock_id
    assert items[0]["quantity"] == 2

    update_payload = {
        "itemId": sock_id,
        "quantity": 5,
        "unitPrice": sock_price
    }
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=762  name='Orders Successful Checkout' ---
def test_orders_successful_checkout():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C", "userID": username}, timeout=10)
    address_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in cust_orders)

# --- id=763  name='Orders Empty Cart Failure' ---
def test_orders_empty_cart_failure():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C", "userID": username}, timeout=10)
    address_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=764  name='Orders Invalid Uri Format' ---
def test_orders_invalid_uri_format():
    order_payload = {
        "customer": "/customers/testuser",
        "address": "/addresses/invalid_format",
        "card": "/cards/invalid_format",
        "items": "/carts/testuser/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=765  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("orderId") == order_id
    assert "authorised" in auth

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0
    assert auths[-1]["orderId"] == order_id

# --- id=766  name='Shipping Request' ---
def test_shipping_request():
    order_id = str(uuid.uuid4())
    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id

# --- id=767  name='Catalogue Image Not Found' ---
def test_catalogue_image_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/images/nonexistent_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
