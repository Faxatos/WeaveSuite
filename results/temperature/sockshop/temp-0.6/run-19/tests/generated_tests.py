# Tests generated in iteration 19
# Captured: 2026-07-05T12:10:05
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=880  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = generate_random_string()
    url_cust = get_url("user", f"/customers/{username}")
    requests.get(url_cust, timeout=10)

    addr_payload = {
        "street": "123 Main St", "number": "123", "city": "Anytown",
        "postcode": "12345", "country": "USA", "userID": username
    }
    url_addr = get_url("user", "/addresses")
    resp_addr = requests.post(url_addr, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    url_get_addr = get_url("user", f"/addresses/{addr_id}")
    resp_get_addr = requests.get(url_get_addr, timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json().get("city") == "Anytown"

    url_cust_addrs = get_url("user", f"/customers/{username}/addresses")
    resp_cust_addrs = requests.get(url_cust_addrs, timeout=10)
    assert resp_cust_addrs.status_code == 200, f"Expected 200, got {resp_cust_addrs.status_code}: {resp_cust_addrs.text}"
    assert any(a.get("id") == addr_id for a in resp_cust_addrs.json().get("_embedded", {}).get("address", []))

    card_payload = {
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }
    url_card = get_url("user", "/cards")
    resp_card = requests.post(url_card, json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    url_get_card = get_url("user", f"/cards/{card_id}")
    resp_get_card = requests.get(url_get_card, timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json().get("expires") == "12/25"

    url_cust_cards = get_url("user", f"/customers/{username}/cards")
    resp_cust_cards = requests.get(url_cust_cards, timeout=10)
    assert resp_cust_cards.status_code == 200, f"Expected 200, got {resp_cust_cards.status_code}: {resp_cust_cards.text}"
    assert any(c.get("id") == card_id for c in resp_cust_cards.json().get("_embedded", {}).get("card", []))

    resp_del_addr = requests.delete(url_get_addr, timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_del_card = requests.delete(url_get_card, timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_del_cust = requests.delete(url_cust, timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"
    assert resp_del_cust.json().get("status") is True

# --- id=881  name='Carts Workflow' ---
def test_carts_workflow():
    customer_id = generate_random_string()
    item_id = str(uuid.uuid4())

    url_items = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp_add = requests.post(url_items, json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(url_items, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id for i in items)

    url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_get_item = requests.get(url_item, timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 2

    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 10.5
    }
    resp_patch = requests.patch(url_items, json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item2 = requests.get(url_item, timeout=10)
    assert resp_get_item2.status_code == 200, f"Expected 200, got {resp_get_item2.status_code}: {resp_get_item2.text}"
    assert resp_get_item2.json().get("quantity") == 5

    resp_del = requests.delete(url_item, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_item3 = requests.get(url_item, timeout=10)
    assert resp_get_item3.status_code == 404, f"Expected 404, got {resp_get_item3.status_code}: {resp_get_item3.text}"

    url_cart = get_url("carts", f"/carts/{customer_id}")
    resp_del_cart = requests.delete(url_cart, timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=882  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())

    pay_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    url_pay = get_url("payment-http", "/payments")
    resp_pay = requests.post(url_pay, json=pay_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    url_get_pay = get_url("payment-http", f"/payments/{order_id}")
    resp_get_pay = requests.get(url_get_pay, timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert len(auths) == 1
    assert auths[0].get("authorised") is True

# --- id=883  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = str(uuid.uuid4())

    pay_payload = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    url_pay = get_url("payment-http", "/payments")
    resp_pay = requests.post(url_pay, json=pay_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is False

    url_get_pay = get_url("payment-http", f"/payments/{order_id}")
    resp_get_pay = requests.get(url_get_pay, timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert len(auths) == 1
    assert auths[0].get("authorised") is False

# --- id=884  name='Shipping Shipment' ---
def test_shipping_shipment():
    order_id = str(uuid.uuid4())
    ship_payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"}
    }
    url_ship = get_url("shipping-http", "/shipping")
    resp_ship = requests.post(url_ship, json=ship_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id

    url_get_ship = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get_ship = requests.get(url_get_ship, timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json().get("orderId") == order_id

# --- id=885  name='Orders Create Order Success' ---
def test_orders_create_order_success():
    username = generate_random_string()
    password = generate_random_string()

    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username, "password": password, "email": f"{username}@example.com",
        "firstName": "Test", "lastName": "User"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "street": "123 Main St", "number": "123", "city": "Anytown",
        "postcode": "12345", "country": "USA", "userID": username
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    sock = socks[0]
    sock_id = sock["id"]
    price = sock["price"]

    resp_add_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": sock_id, "quantity": 2, "unitPrice": price
    }, timeout=10)
    assert resp_add_cart.status_code == 201, f"Expected 201, got {resp_add_cart.status_code}: {resp_add_cart.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    url_orders = get_url("orders", "/orders")
    resp_order = requests.post(url_orders, json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username

    url_get_order = get_url("orders", f"/orders/{order_id}")
    resp_get_order = requests.get(url_get_order, timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    url_search = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp_search = requests.get(url_search, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded = resp_search.json().get("_embedded", {})
    cust_orders = embedded.get("customerOrders", [])
    assert any(o.get("id") == order_id for o in cust_orders)

# --- id=886  name='Orders Create Order Empty Cart' ---
def test_orders_create_order_empty_cart():
    username = generate_random_string()

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    url_orders = get_url("orders", "/orders")
    resp_order = requests.post(url_orders, json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=887  name='Orders Create Order Invalid Address Uri' ---
def test_orders_create_order_invalid_address_uri():
    username = generate_random_string()

    resp_add_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "some-item", "quantity": 1, "unitPrice": 10.0
    }, timeout=10)
    assert resp_add_cart.status_code == 201, f"Expected 201, got {resp_add_cart.status_code}: {resp_add_cart.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid-format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    url_orders = get_url("orders", "/orders")
    resp_order = requests.post(url_orders, json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=876  name='Catalogue Socks And Images' ---
def test_catalogue_get_socks_and_images():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    assert len(socks) > 0

    sock = socks[0]
    sock_id = sock.get("id")

    url_id = get_url("catalogue", f"/catalogue/{sock_id}")
    resp_id = requests.get(url_id, timeout=10)
    assert resp_id.status_code == 200, f"Expected 200, got {resp_id.status_code}: {resp_id.text}"
    sock_details = resp_id.json()
    assert sock_details.get("id") == sock_id

    if sock_details.get("imageUrl"):
        image_path = sock_details["imageUrl"][0]
        image_name = image_path.split("/")[-1]
        image_url = get_url("catalogue", f"/catalogue/images/{image_name}")
        resp_img = requests.get(image_url, timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=877  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    url = get_url("catalogue", "/catalogue/invalid-sock-id")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=878  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = generate_random_string()
    password = generate_random_string()

    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    url_reg = get_url("user", "/register")
    resp_reg = requests.post(url_reg, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    url_cust = get_url("user", f"/customers/{username}")
    resp_cust = requests.get(url_cust, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    assert resp_cust.json().get("username") == username

    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_reg_conflict = requests.post(url_reg, json=user_payload, timeout=10)
    assert resp_reg_conflict.status_code == 409, f"Expected 409, got {resp_reg_conflict.status_code}: {resp_reg_conflict.text}"

# --- id=879  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=HTTPBasicAuth("nonexistent", "wrongpass"), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"
