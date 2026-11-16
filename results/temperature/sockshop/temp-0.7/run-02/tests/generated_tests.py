# Tests generated in iteration 02
# Captured: 2026-06-30T10:05:08
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=524  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    email = f"{username}@example.com"

    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }
    url_register = get_url("user", "/register")
    resp_register = requests.post(url_register, json=payload, timeout=10)
    assert resp_register.status_code == 200, f"Expected 200, got {resp_register.status_code}: {resp_register.text}"

    url_customer = get_url("user", f"/customers/{username}")
    resp_customer = requests.get(url_customer, timeout=10)
    assert resp_customer.status_code == 200, f"Expected 200, got {resp_customer.status_code}: {resp_customer.text}"
    assert resp_customer.json().get("username") == username, f"Expected username {username}"
    assert "password" not in resp_customer.json() or resp_customer.json().get("password") is None, "Password should not be exposed"

    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_conflict = requests.post(url_register, json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=525  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_register = get_url("user", "/register")
    requests.post(url_register, json={"username": username, "password": "pwd"}, timeout=10)

    url_addr_post = get_url("user", "/addresses")
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(url_addr_post, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    url_addr_get = get_url("user", f"/addresses/{addr_id}")
    resp_addr_get = requests.get(url_addr_get, timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "London"

    url_cust_addr = get_url("user", f"/customers/{username}/addresses")
    resp_cust_addr = requests.get(url_cust_addr, timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded_addr = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in embedded_addr)

    resp_addr_del = requests.delete(url_addr_get, timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    url_card_post = get_url("user", "/cards")
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(url_card_post, json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    url_card_get = get_url("user", f"/cards/{card_id}")
    resp_card_get = requests.get(url_card_get, timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert "*" in resp_card_get.json().get("longNum", "")

    url_cust_card = get_url("user", f"/customers/{username}/cards")
    resp_cust_card = requests.get(url_cust_card, timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    embedded_card = resp_cust_card.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in embedded_card)

    resp_card_del = requests.delete(url_card_get, timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

# --- id=526  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_register = get_url("user", "/register")
    requests.post(url_register, json={"username": username, "password": "pwd"}, timeout=10)

    url_customer = get_url("user", f"/customers/{username}")
    resp_del = requests.delete(url_customer, timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_del_again = requests.delete(url_customer, timeout=10)
    assert resp_del_again.status_code == 200, f"Expected 200, got {resp_del_again.status_code}: {resp_del_again.text}"
    assert resp_del_again.json().get("status") is False

# --- id=527  name='User Customers' ---
def test_user_get_customers():
    url_cust = get_url("user", "/customers")
    resp_cust = requests.get(url_cust, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"

# --- id=528  name='Carts Add And Retrieve Items' ---
def test_carts_add_and_retrieve_items():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    url_items = get_url("carts", f"/carts/{customer_id}/items")
    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}
    resp_add = requests.post(url_items, json=payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    assert resp_add.json().get("itemId") == item_id

    resp_get = requests.get(url_items, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    payload_update = {"itemId": item_id, "quantity": 5, "unitPrice": 15.5}
    resp_patch = requests.patch(url_items, json=payload_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_get_item = requests.get(url_item, timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 5

    resp_del = requests.delete(url_item, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(url_item, timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=529  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    url_session_items = get_url("carts", f"/carts/{session_id}/items")
    requests.post(url_session_items, json={"itemId": "item_sess", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    url_merge = get_url("carts", f"/carts/{customer_id}/merge")
    resp_merge = requests.get(url_merge, params={"sessionId": session_id}, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    url_cust_items = get_url("carts", f"/carts/{customer_id}/items")
    resp_cust = requests.get(url_cust_items, timeout=10)
    assert resp_cust.status_code == 200
    items = resp_cust.json()
    assert any(i.get("itemId") == "item_sess" for i in items)

    bad_session_id = f"sess_{uuid.uuid4().hex[:8]}"
    resp_bad_merge = requests.get(url_merge, params={"sessionId": bad_session_id}, timeout=10)
    assert resp_bad_merge.status_code == 404, f"Expected 404, got {resp_bad_merge.status_code}: {resp_bad_merge.text}"

# --- id=530  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    url_items = get_url("carts", f"/carts/{customer_id}/items")
    requests.post(url_items, json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    url_cart = get_url("carts", f"/carts/{customer_id}")
    resp_del = requests.delete(url_cart, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(url_items, timeout=10)
    assert resp_get.status_code == 200
    assert len(resp_get.json()) == 0

# --- id=531  name='Catalogue Search And Size' ---
def test_catalogue_search_and_size():
    url_cat = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(url_cat, params={"page": 1, "size": 5}, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0]["id"]
        url_item = get_url("catalogue", f"/catalogue/{item_id}")
        resp_item = requests.get(url_item, timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id

    url_size = get_url("catalogue", "/catalogue/size")
    resp_size = requests.get(url_size, timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

# --- id=532  name='Catalogue Tags' ---
def test_catalogue_tags():
    url_tags = get_url("catalogue", "/tags")
    resp_tags = requests.get(url_tags, timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=533  name='Orders Creation Workflow' ---
def test_orders_creation_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_register = get_url("user", "/register")
    requests.post(url_register, json={"username": username, "password": "pwd"}, timeout=10)

    url_addresses = get_url("user", "/addresses")
    resp_addr = requests.post(url_addresses, json={"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username}, timeout=10)
    address_id = resp_addr.json().get("id")

    url_cards = get_url("user", "/cards")
    resp_card = requests.post(url_cards, json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    url_cart_items = get_url("carts", f"/carts/{username}/items")
    requests.post(url_cart_items, json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    url_orders = get_url("orders", "/orders")
    payload_order = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(url_orders, json=payload_order, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username

    url_order = get_url("orders", f"/orders/{order_id}")
    resp_get_order = requests.get(url_order, timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    url_search = get_url("orders", "/orders/search/customerId")
    resp_search = requests.get(url_search, params={"custId": username}, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded = resp_search.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=534  name='Orders Missing Cart Negative' ---
def test_orders_missing_cart_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_register = get_url("user", "/register")
    requests.post(url_register, json={"username": username, "password": "pwd"}, timeout=10)

    url_addresses = get_url("user", "/addresses")
    resp_addr = requests.post(url_addresses, json={"city": "London", "country": "UK", "number": "1", "postcode": "NW1", "street": "Baker", "userID": username}, timeout=10)
    address_id = resp_addr.json().get("id")

    url_cards = get_url("user", "/cards")
    resp_card = requests.post(url_cards, json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    url_orders = get_url("orders", "/orders")
    payload_order = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(url_orders, json=payload_order, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=535  name='Orders Payment Declined Negative' ---
def test_orders_payment_declined_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_register = get_url("user", "/register")
    requests.post(url_register, json={"username": username, "password": "pwd"}, timeout=10)

    url_addresses = get_url("user", "/addresses")
    resp_addr = requests.post(url_addresses, json={"city": "London", "country": "UK", "number": "1", "postcode": "NW1", "street": "Baker", "userID": username}, timeout=10)
    address_id = resp_addr.json().get("id")

    url_cards = get_url("user", "/cards")
    resp_card = requests.post(url_cards, json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    url_cart_items = get_url("carts", f"/carts/{username}/items")
    requests.post(url_cart_items, json={"itemId": "item1", "quantity": 10, "unitPrice": 15.0}, timeout=10)

    url_orders = get_url("orders", "/orders")
    payload_order = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(url_orders, json=payload_order, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=536  name='Orders Invalid Address Uri Negative' ---
def test_orders_invalid_address_uri_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_register = get_url("user", "/register")
    requests.post(url_register, json={"username": username, "password": "pwd"}, timeout=10)

    url_cart_items = get_url("carts", f"/carts/{username}/items")
    requests.post(url_cart_items, json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    url_orders = get_url("orders", "/orders")
    payload_order = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid-format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(url_orders, json=payload_order, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=537  name='Payment Http Authorization' ---
def test_payment_http_authorization():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    url_payment = get_url("payment-http", "/payments")

    payload = {
        "address": {"city": "London", "country": "UK", "number": "1", "postcode": "NW1", "street": "Baker"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    resp_pay = requests.post(url_payment, json=payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth = resp_pay.json()
    assert auth.get("orderId") == order_id
    assert auth.get("authorised") is True

    url_get_pay = get_url("payment-http", f"/payments/{order_id}")
    resp_get = requests.get(url_get_pay, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list)
    assert len(auths) == 1
    assert auths[0].get("orderId") == order_id
    assert auths[0].get("authorised") is True

# --- id=538  name='Payment Http Authorization Decline' ---
def test_payment_http_authorization_decline():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    url_payment = get_url("payment-http", "/payments")

    payload = {
        "address": {"city": "London", "country": "UK", "number": "1", "postcode": "NW1", "street": "Baker"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    resp_pay = requests.post(url_payment, json=payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth = resp_pay.json()
    assert auth.get("orderId") == order_id
    assert auth.get("authorised") is False

# --- id=539  name='Shipping Http Request' ---
def test_shipping_http_request():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    url_shipping = get_url("shipping-http", "/shipping")

    payload = {
        "address": {"city": "London", "country": "UK", "number": "1", "postcode": "NW1", "street": "Baker"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(url_shipping, json=payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id

    url_get_ship = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get = requests.get(url_get_ship, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
