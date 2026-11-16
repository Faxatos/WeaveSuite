# Tests generated in iteration 12
# Captured: 2026-06-30T16:06:00
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=640  name='User Register Conflict And Login' ---
def test_user_register_conflict_and_login():
    user_data = create_user()
    username = user_data["username"]

    # Follow-up GET to verify state
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == user_data["firstName"]

    # Conflict: Register same user
    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login success
    resp_login = requests.get(get_url("user", "/login"), auth=(username, user_data["password"]), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=641  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    user_data = create_user()
    username = user_data["username"]

    # Add Address
    addr_req = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Follow-up GET Address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    fetched_addr = resp_addr_get.json()
    assert fetched_addr.get("city") == addr_req["city"]

    # Add Card
    card_req = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1111222233334444",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Follow-up GET Card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    fetched_card = resp_card_get.json()
    assert fetched_card.get("expires") == card_req["expires"]
    assert "4444" in fetched_card.get("longNum", "")
    assert "*" in fetched_card.get("longNum", "")

# --- id=642  name='User Customer Deletion' ---
def test_user_customer_deletion():
    user_data = create_user()
    username = user_data["username"]

    # Delete customer
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    # Repeat Delete customer (should be false)
    resp_del_repeat = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_repeat.status_code == 200, f"Expected 200, got {resp_del_repeat.status_code}: {resp_del_repeat.text}"
    assert resp_del_repeat.json().get("status") is False

# --- id=643  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0

    item_id = items[0]["id"]
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json().get("id") == item_id

# --- id=644  name='Cart Management' ---
def test_cart_management():
    # Get a real item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]

    customer_id = f"cust_{generate_random_string()}"

    # Add to cart
    item_req = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify cart
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

    # Delete from cart
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify empty
    resp_get_empty = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_empty.status_code == 200, f"Expected 200, got {resp_get_empty.status_code}: {resp_get_empty.text}"
    assert len(resp_get_empty.json()) == 0

# --- id=645  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    user_data = create_user()
    username = user_data["username"]

    # Add Address
    addr_req = {"city": "City", "country": "Country", "number": "1", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json()["id"]

    # Add Card
    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Get Catalogue Item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]

    # Add to Cart
    item_req = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_req, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Create Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username

    # Follow-up GET Order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    fetched_order = resp_order_get.json()
    assert fetched_order.get("id") == order_id
    assert fetched_order.get("status") in ["CREATED", "PAID", "SHIPPED"]

    # Search Orders by Customer
    resp_search = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert len(embedded_orders) > 0
    assert any(o.get("id") == order_id for o in embedded_orders)

# --- id=646  name='Orders Empty Cart Not Acceptable' ---
def test_orders_empty_cart_not_acceptable():
    user_data = create_user()
    username = user_data["username"]

    # Add Address
    addr_req = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    address_id = resp_addr.json()["id"]

    # Add Card
    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id = resp_card.json()["id"]

    # Do NOT add items to cart. Cart is empty.
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=647  name='Orders Malformed Composite Id Not Found' ---
def test_orders_malformed_composite_id_not_found():
    user_data = create_user()
    username = user_data["username"]

    # Add to Cart
    item_req = {"itemId": "fake-item", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_req, timeout=10)

    # Malformed address URI
    order_req = {
        "customer": f"/customers/{username}",
        "address": "/addresses/malformed_id_without_colon",
        "card": "/cards/malformed_id",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=648  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())

    # Valid amount (<= 100)
    pay_req_valid = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"}
    }
    resp_pay_1 = requests.post(get_url("payment-http", "/payments"), json=pay_req_valid, timeout=10)
    assert resp_pay_1.status_code == 200, f"Expected 200, got {resp_pay_1.status_code}: {resp_pay_1.text}"
    assert resp_pay_1.json().get("authorised") is True

    # Follow-up GET
    resp_get_1 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_1.status_code == 200, f"Expected 200, got {resp_get_1.status_code}: {resp_get_1.text}"
    auths_1 = resp_get_1.json()
    assert len(auths_1) == 1
    assert auths_1[0].get("authorised") is True

    # Invalid amount (> 100) - spec says "Authorized only when amount is greater than 0 and at most 100"
    pay_req_invalid = pay_req_valid.copy()
    pay_req_invalid["amount"] = 150.0
    resp_pay_2 = requests.post(get_url("payment-http", "/payments"), json=pay_req_invalid, timeout=10)
    assert resp_pay_2.status_code == 200, f"Expected 200, got {resp_pay_2.status_code}: {resp_pay_2.text}"
    assert resp_pay_2.json().get("authorised") is False

    # Follow-up GET to check both are recorded (no deduplication)
    resp_get_2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_2.status_code == 200, f"Expected 200, got {resp_get_2.status_code}: {resp_get_2.text}"
    auths_2 = resp_get_2.json()
    assert len(auths_2) == 2
    assert auths_2[1].get("authorised") is False

# --- id=649  name='Shipping Workflow' ---
def test_shipping_workflow():
    order_id = str(uuid.uuid4())
    ship_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A", "street": "Downing"}
    }

    # Post shipping
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id
    assert shipment.get("carrier") is not None

    # Follow-up GET
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched_shipment = resp_get.json()
    assert fetched_shipment.get("orderId") == order_id
    assert fetched_shipment.get("carrier") == shipment.get("carrier")
