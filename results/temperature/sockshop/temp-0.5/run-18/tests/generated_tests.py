# Tests generated in iteration 18
# Captured: 2026-07-04T22:08:26
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=603  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {
        "itemId": "item2",
        "quantity": 1,
        "unitPrice": 5.0
    }
    url = get_url("carts", f"/carts/{customer_id}/items")
    requests.post(url, json=item_data, timeout=10)

    item_data["quantity"] = 5
    resp = requests.patch(url, json=item_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    item_url = get_url("carts", f"/carts/{customer_id}/items/item2")
    resp = requests.get(item_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

# --- id=604  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {
        "itemId": "item3",
        "quantity": 1,
        "unitPrice": 5.0
    }
    url = get_url("carts", f"/carts/{customer_id}/items")
    requests.post(url, json=item_data, timeout=10)

    del_url = get_url("carts", f"/carts/{customer_id}/items/item3")
    resp = requests.delete(del_url, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(del_url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=605  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {"itemId": "item1", "quantity": 1, "unitPrice": 1.0}
    url = get_url("carts", f"/carts/{customer_id}/items")
    requests.post(url, json=item_data, timeout=10)

    del_url = get_url("carts", f"/carts/{customer_id}")
    resp = requests.delete(del_url, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    items_resp = requests.get(url, timeout=10)
    assert items_resp.status_code == 200, f"Expected 200, got {items_resp.status_code}: {items_resp.text}"
    assert len(items_resp.json()) == 0

# --- id=606  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_data = {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    address_id = resp.json()["id"]

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json()["id"]

    item_data = {"itemId": "sock1", "quantity": 2, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

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
    assert len(order["items"]) == 1

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp = requests.get(search_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    embedded = resp.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=607  name='Orders Create Missing Cart' ---
def test_orders_create_missing_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1",
        "card": f"/cards/{username}:3456",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=608  name='Orders Create Invalid Address Uri' ---
def test_orders_create_invalid_address_uri():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{username}:3456",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=609  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id
    assert auths[0]["authorised"] is True

# --- id=610  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is False

# --- id=611  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id

# --- id=594  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)

# --- id=595  name='Catalogue Sock By Id' ---
def test_catalogue_get_sock_by_id():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if not socks:
        pytest.skip("No socks in catalogue")
    sock_id = socks[0]["id"]

    sock_url = get_url("catalogue", f"/catalogue/{sock_id}")
    resp = requests.get(sock_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == sock_id

# --- id=596  name='Catalogue Sock By Id Not Found' ---
def test_catalogue_get_sock_by_id_not_found():
    sock_url = get_url("catalogue", "/catalogue/invalid-id-12345")
    resp = requests.get(sock_url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=597  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_url = get_url("user", "/register")
    resp = requests.post(reg_url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_url = get_url("user", "/login")
    resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=598  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_url = get_url("user", "/register")
    resp = requests.post(reg_url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(reg_url, json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=599  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    addr_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }
    url = get_url("user", "/addresses")
    resp = requests.post(url, json=addr_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None

    get_url_addr = get_url("user", f"/addresses/{address_id}")
    resp = requests.get(get_url_addr, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["city"] == "London"

# --- id=600  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    url = get_url("user", "/cards")
    resp = requests.post(url, json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    get_url_card = get_url("user", f"/cards/{card_id}")
    resp = requests.get(get_url_card, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["expires"] == "12/25"
    assert "123456789012" not in resp.json()["longNum"]

# --- id=601  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    del_url = get_url("user", f"/customers/{username}")
    resp = requests.delete(del_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

# --- id=602  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {
        "itemId": "item1",
        "quantity": 2,
        "unitPrice": 10.5
    }
    url = get_url("carts", f"/carts/{customer_id}/items")
    resp = requests.post(url, json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item1"
    assert items[0]["quantity"] == 2
