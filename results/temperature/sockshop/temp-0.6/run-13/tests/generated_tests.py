# Tests generated in iteration 13
# Captured: 2026-07-05T08:19:08
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=800  name='Payment Authorization Boundary Valid' ---
def test_payment_authorization_boundary_valid():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 100.00,  # Boundary: at most 100
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    # Action: Authorize Payment
    pay_resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auth_result = pay_resp.json()
    assert auth_result["authorised"] is True

    # Verify: Authorization recorded
    get_pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is True
    assert auths[0]["orderId"] == order_id

# --- id=801  name='Payment Authorization Boundary Declined' ---
def test_payment_authorization_boundary_declined():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 100.01,  # Boundary: strictly greater than 100
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    # Action: Authorize Payment
    pay_resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auth_result = pay_resp.json()
    # Spec states declined payment is returned as HTTP 200 with authorised=false
    assert auth_result["authorised"] is False

    # Verify: Authorization recorded as declined
    get_pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

# --- id=802  name='Shipping Direct Request' ---
def test_shipping_direct_request():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    ship_req = {
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "12345", "street": "Street"},
        "itemCount": 5,
        "orderId": order_id
    }

    # Action: Ship request
    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    shipment = ship_resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    # Verify: Shipment recorded
    get_ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"
    fetched_shipment = get_ship_resp.json()
    assert fetched_shipment["orderId"] == order_id
    assert fetched_shipment["trackingNumber"] == shipment["trackingNumber"]
    assert fetched_shipment["carrier"] == shipment["carrier"]

# --- id=793  name='User Registration And Login Workflow' ---
def test_user_registration_and_login_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "securepass123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Action: Register User
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify: Customer exists
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()
    assert customer["username"] == username
    assert customer["firstName"] == "Test"
    assert customer["lastName"] == "User"
    assert customer["email"] == f"{username}@example.com"
    assert "password" not in customer or customer["password"] != password  # Ensure no plaintext password

    # Action: Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Repetition / Conflict
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Negative: Invalid Login
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=794  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # Action: Add Address
    addr_payload = {"city": "Cityville", "country": "Countryland", "number": "42", "postcode": "12345", "street": "Main St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    # Verify: Address added
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addresses = resp_addr_get.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == addr_id for a in addresses)
    added_addr = next(a for a in addresses if a["id"] == addr_id)
    assert added_addr["city"] == "Cityville"

    # Action: Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Verify: Card added and masked
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    cards = resp_card_get.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in cards)
    added_card = next(c for c in cards if c["id"] == card_id)
    assert "3456" in added_card["longNum"]
    assert "*" in added_card["longNum"]

    # Action: Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Verify: Address deleted
    resp_addr_get2 = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get2.status_code == 200, f"Expected 200, got {resp_addr_get2.status_code}: {resp_addr_get2.text}"
    addresses2 = resp_addr_get2.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == addr_id for a in addresses2)

# --- id=795  name='User Customer Deletion' ---
def test_user_customer_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # Action: Delete Customer
    del_resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
    assert del_resp.json()["status"] is True

    # Verify: Customer deleted (Spec says GET never returns 404, returns empty customer with only username populated)
    get_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()
    assert customer["username"] == username
    assert "firstName" not in customer or not customer["firstName"]

# --- id=796  name='Carts Management Workflow' ---
def test_carts_management_workflow():
    # Setup: Get a real item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Action: Add item to cart
    item_payload = {"itemId": item_id, "quantity": 3, "unitPrice": unit_price}
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Verify: Item is in cart
    cart_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert cart_resp.status_code == 200, f"Expected 200, got {cart_resp.status_code}: {cart_resp.text}"
    cart_items = cart_resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 3
    assert cart_items[0]["unitPrice"] == unit_price

    # Action: Delete cart
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Verify: Cart is empty
    cart_resp2 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert cart_resp2.status_code == 200, f"Expected 200, got {cart_resp2.status_code}: {cart_resp2.text}"
    assert len(cart_resp2.json()) == 0

# --- id=797  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    # Setup: User, Address, Card
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    # Setup: Cart
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    item_id = item["id"]
    unit_price = item["price"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": unit_price}, timeout=10)

    # Action: Place Order
    order_req = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order = order_resp.json()
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert order["total"] == 2 * unit_price

    # Verify: Order retrieved directly
    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    fetched_order = get_order_resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["status"] in ["CREATED", "PAID", "SHIPPED"]

    # Verify: Order retrieved via customer search
    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    customer_orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

    # Verify: Payment created by order
    pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    payments = pay_resp.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id

    # Verify: Shipment created by order
    ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    shipment = ship_resp.json()
    assert shipment["orderId"] == order_id

# --- id=798  name='Orders Negative Empty Cart Not Acceptable' ---
def test_orders_negative_empty_cart_not_acceptable():
    # Setup context identical to positive workflow
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    # Explicitly ensure cart is empty
    requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)

    # Action: Place Order with empty cart
    order_req = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)

    # Verify: 406 Not Acceptable
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=799  name='Orders Negative Invalid Uri Format Not Found' ---
def test_orders_negative_invalid_uri_format_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # Action: Place Order with malformed URI (missing composite ID structure)
    order_req = {
        "address": "/addresses/malformed_no_colon",
        "card": f"/cards/{username}:1234",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)

    # Verify: 404 Not Found due to unparseable URI
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"
