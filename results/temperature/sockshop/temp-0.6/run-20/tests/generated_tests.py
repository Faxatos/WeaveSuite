# Tests generated in iteration 20
# Captured: 2026-07-05T12:53:29
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=895  name='Order Placement Negative' ---
def test_order_placement_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "customer": f"/customers/{username}"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

# --- id=896  name='Order Placement Invalid Uri 404' ---
def test_order_placement_invalid_uri_404():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_no_colon",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=897  name='Order Not Found' ---
def test_order_not_found():
    resp = requests.get(get_url("orders", "/orders/invalid_order_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=898  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "123", "number": "1", "city": "C", "postcode": "1", "country": "US"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth_data = resp_pay.json()
    assert auth_data.get("orderId") == order_id
    assert auth_data.get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0].get("orderId") == order_id
    assert auths[0].get("authorised") is True

# --- id=899  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "123", "number": "1", "city": "C", "postcode": "1", "country": "US"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth_data = resp_pay.json()
    assert auth_data.get("orderId") == order_id
    assert auth_data.get("authorised") is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0].get("orderId") == order_id
    assert auths[0].get("authorised") is False

# --- id=900  name='Shipping Request' ---
def test_shipping_request():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    ship_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "123", "number": "1", "city": "C", "postcode": "1", "country": "US"}
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data.get("orderId") == order_id
    assert "trackingNumber" in ship_data

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id

# --- id=888  name='User Register And Login' ---
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

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username

    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    resp_bad_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrong"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=889  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "A",
        "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_data = {
        "street": "123 Main St",
        "number": "42",
        "city": "Cityville",
        "postcode": "12345",
        "country": "Countryland",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None
    assert addr_id.startswith(f"{username}:")

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json().get("street") == "123 Main St"

    card_data = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None
    assert card_id.startswith(f"{username}:")

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json().get("expires") == "12/25"

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    addrs = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addrs)

    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    cards = resp_cust_card.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_cust_addr_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addrs_after = resp_cust_addr_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addrs_after)

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_cust_card_after = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    cards_after = resp_cust_card_after.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards_after)

# --- id=890  name='User Deletion' ---
def test_user_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_get_after = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    assert resp_get_after.json().get("firstName") is None

    resp_del_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_again.status_code == 200, f"Expected 200, got {resp_del_again.status_code}: {resp_del_again.text}"
    assert resp_del_again.json().get("status") is False

# --- id=891  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if len(items) > 0:
        item_id = items[0].get("id")
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=892  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_999"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=893  name='Cart Management' ---
def test_cart_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0].get("id")
    price = items[0].get("price", 10.0)

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    assert resp_add.json().get("itemId") == item_id

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0].get("itemId") == item_id
    assert cart_items[0].get("quantity") == 1

    resp_add_again = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp_add_again.status_code == 201, f"Expected 201, got {resp_add_again.status_code}: {resp_add_again.text}"

    resp_get_again = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_again.status_code == 200, f"Expected 200, got {resp_get_again.status_code}: {resp_get_again.text}"
    assert resp_get_again.json().get("quantity") == 2

    patch_item = {"itemId": item_id, "quantity": 5, "unitPrice": price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_item, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_patched = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_patched.status_code == 200, f"Expected 200, got {resp_get_patched.status_code}: {resp_get_patched.text}"
    assert resp_get_patched.json().get("quantity") == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=894  name='Order Placement E2e' ---
def test_order_placement_e2e():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_data = {"street": "123 Main", "number": "1", "city": "City", "postcode": "123", "country": "USA", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_data = {"longNum": "1111222233334444", "expires": "12/26", "ccv": "123", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    assert len(items) > 0
    item_id = items[0].get("id")
    price = items[0].get("price", 10.0)

    cart_item = {"itemId": item_id, "quantity": 2, "unitPrice": price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    resp_cust_orders = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_cust_orders.status_code == 200, f"Expected 200, got {resp_cust_orders.status_code}: {resp_cust_orders.text}"
    cust_orders = resp_cust_orders.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in cust_orders)

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    pay_auths = resp_pay.json()
    assert isinstance(pay_auths, list)
    assert len(pay_auths) > 0
    assert pay_auths[0].get("orderId") == order_id

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id
