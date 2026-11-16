# Tests generated in iteration 03
# Captured: 2026-07-05T01:49:05
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=652  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "testpassword"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register user
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET customer
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"
    assert "password" not in customer or customer.get("password") != password

    # Repeat registration (Conflict)
    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=653  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": "a@b.c", "firstName": "A", "lastName": "B"}, timeout=10)

    # Add Address
    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Follow-up GET Address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_obj = resp_addr_get.json()
    assert addr_obj.get("city") == "London"
    assert addr_obj.get("postcode") == "NW1"

    # Add Card
    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Follow-up GET Card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_obj = resp_card_get.json()
    assert card_obj.get("expires") == "12/25"
    assert "1234567890123456" not in card_obj.get("longNum", "")

    # Delete Address
    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    # Delete Card
    resp_card_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

# --- id=654  name='Catalogue Retrieval And Not Found' ---
def test_catalogue_retrieval_and_not_found():
    # GET catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), params={"size": 5}, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)

    if items:
        # GET specific item
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id

    # GET invalid item
    resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid-id-xyz"), timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=655  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = str(uuid.uuid4())

    # Add item
    item_data = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Follow-up GET items
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id and i.get("quantity") == 2 for i in items)

    # Patch item
    patch_data = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Follow-up GET specific item
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 5

    # Delete item
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Follow-up GET specific item (should be 404)
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=656  name='Orders End To End And Negative' ---
def test_orders_end_to_end_and_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@a.c", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    item_id = str(uuid.uuid4())
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 15.0}, timeout=10)

    # Place valid order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username
    assert len(order.get("items", [])) == 1

    # Follow-up GET order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    # Search orders
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded = resp_search.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

    # Negative: Empty cart -> 406
    empty_user = f"empty_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": empty_user, "password": "pw", "email": "e@a.c", "firstName": "E", "lastName": "U"}, timeout=10)
    empty_order_payload = {
        "customer": f"/customers/{empty_user}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{empty_user}/items"
    }
    resp_empty_order = requests.post(get_url("orders", "/orders"), json=empty_order_payload, timeout=10)
    assert resp_empty_order.status_code == 406, f"Expected 406, got {resp_empty_order.status_code}: {resp_empty_order.text}"

    # Negative: Invalid composite ID -> 404
    invalid_order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid-format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_invalid_order = requests.post(get_url("orders", "/orders"), json=invalid_order_payload, timeout=10)
    assert resp_invalid_order.status_code == 404, f"Expected 404, got {resp_invalid_order.status_code}: {resp_invalid_order.text}"

# --- id=657  name='Payment Authorization Limits' ---
def test_payment_authorization_limits():
    order_id = str(uuid.uuid4())

    # Valid payment (amount <= 100)
    payment_req_valid = {
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234123412341234"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }
    resp_pay_valid = requests.post(get_url("payment-http", "/payments"), json=payment_req_valid, timeout=10)
    assert resp_pay_valid.status_code == 200, f"Expected 200, got {resp_pay_valid.status_code}: {resp_pay_valid.text}"
    assert resp_pay_valid.json().get("authorised") is True

    # Invalid payment (amount > 100)
    payment_req_invalid = payment_req_valid.copy()
    payment_req_invalid["amount"] = 150.0
    resp_pay_invalid = requests.post(get_url("payment-http", "/payments"), json=payment_req_invalid, timeout=10)
    assert resp_pay_invalid.status_code == 200, f"Expected 200, got {resp_pay_invalid.status_code}: {resp_pay_invalid.text}"
    assert resp_pay_invalid.json().get("authorised") is False

    # Follow-up GET authorizations
    resp_get_auth = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_auth.status_code == 200, f"Expected 200, got {resp_get_auth.status_code}: {resp_get_auth.text}"
    auths = resp_get_auth.json()
    assert len(auths) == 2
    assert auths[0].get("authorised") is True
    assert auths[1].get("authorised") is False

# --- id=658  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = str(uuid.uuid4())
    shipping_req = {
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"},
        "itemCount": 3,
        "orderId": order_id
    }

    # Create shipment
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id
    assert shipment.get("carrier") is not None

    # Follow-up GET shipment
    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json().get("orderId") == order_id
    assert resp_get_ship.json().get("carrier") == shipment.get("carrier")
