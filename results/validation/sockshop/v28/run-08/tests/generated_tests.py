# Tests generated in iteration 08
# Captured: 2026-06-21T07:00:02
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1183  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    if socks:
        sock = socks[0]
        sock_id = sock["id"]
        resp_id = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_id.status_code == 200, f"Expected 200, got {resp_id.status_code}: {resp_id.text}"
        assert resp_id.json()["id"] == sock_id

# --- id=1184  name='Catalogue Tags And Size' ---
def test_catalogue_get_tags_and_size():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    tags = tags_data.get("tags", [])
    if tags:
        tag = tags[0]
        resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

# --- id=1185  name='User Register And Login' ---
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
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json()["username"] == username

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1186  name='User Add Address' ---
def test_user_add_get_delete_address():
    username = f"user_{uuid.uuid4().hex[:8]}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    addr_data = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    resp_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["city"] == "City"

    resp_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_list = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    embedded = resp_list.json().get("_embedded", {})
    addresses = embedded.get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses)

# --- id=1187  name='User Add Card' ---
def test_user_add_get_delete_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    card_data = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["expires"] == "12/25"

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_list = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    embedded = resp_list.json().get("_embedded", {})
    cards = embedded.get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=1188  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert "firstName" not in resp_get.json() or not resp_get.json()["firstName"]

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=1189  name='Carts Add Update Item' ---
def test_carts_add_get_update_delete_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": customer_id, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{customer_id}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    item_id = _get_real_sock_id()
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }

    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["quantity"] == 2

    resp_inc = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_inc.status_code == 201, f"Expected 201, got {resp_inc.status_code}: {resp_inc.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()[0]["quantity"] == 4

    patch_data = {"itemId": item_id, "quantity": 10, "unitPrice": 10.5}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 10

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_item_404 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item_404.status_code == 404, f"Expected 404, got {resp_get_item_404.status_code}: {resp_get_item_404.text}"

# --- id=1190  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]
    addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]
    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    sock_id = _get_real_sock_id()
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock_id, "quantity": 2, "unitPrice": 15.0}, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert cart_get.status_code == 200, f"Expected 200, got {cart_get.status_code}: {cart_get.text}"

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == sock_id
    assert order["items"][0]["quantity"] == 2

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded = resp_search.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert len(customer_orders) == 1
    assert customer_orders[0]["id"] == order_id

# --- id=1191  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = f"user_{uuid.uuid4().hex[:8]}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    order_req = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1192  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = _create_order()
    payment_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is True

    resp2 = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"

    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert len(resp_get2.json()) == 2

# --- id=1193  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = _create_order()
    payment_req = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

# --- id=1194  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = _create_order()
    shipping_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"}
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
