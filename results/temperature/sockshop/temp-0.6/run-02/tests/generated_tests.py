# Tests generated in iteration 02
# Captured: 2026-07-05T01:17:51
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=644  name='User Register And Login Workflow' ---
def test_user_register_and_login_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Action: Register user
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verification: Follow-up GET on customer
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["username"] == username
    assert resp_get.json()["firstName"] == "Test"
    assert "password" not in resp_get.json() or resp_get.json()["password"] != password

    # Action: Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Constraint: Conflict/Repetition
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Negative: Login with wrong password
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=645  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"

    # Action: Add Address
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A", "street": "Downing", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    # Verification: GET Address
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json()["city"] == "London"

    # Action: Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Verification: GET Card
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert "1234567890" not in resp_get_card.json()["longNum"]

    # Action: Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Verification: Address is missing from customer's addresses
    resp_get_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addrs.status_code == 200, f"Expected 200, got {resp_get_addrs.status_code}: {resp_get_addrs.text}"
    addrs = resp_get_addrs.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addrs)

    # Action: Delete customer
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json()["status"] is True

    # Verification: GET returns empty customer (spec behavior)
    resp_get_del = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_del.status_code == 200, f"Expected 200, got {resp_get_del.status_code}: {resp_get_del.text}"
    assert resp_get_del.json()["username"] == username
    assert "firstName" not in resp_get_del.json() or not resp_get_del.json()["firstName"]

# --- id=646  name='Catalogue Retrieval And Not Found' ---
def test_catalogue_retrieval_and_not_found():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]
    item_name = items[0]["name"]

    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["name"] == item_name

    resp_not_found = requests.get(get_url("catalogue", "/catalogue/non-existent-id-999"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=647  name='Carts Add Increment And Items' ---
def test_carts_add_increment_and_delete_items():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    price = resp_cat.json()[0]["price"]

    # Action: Add item
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verification: GET item
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 1

    # Action: Increment quantity
    resp_inc = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_inc.status_code == 201, f"Expected 201, got {resp_inc.status_code}: {resp_inc.text}"

    # Verification: GET item incremented
    resp_get_inc = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_inc.status_code == 200, f"Expected 200, got {resp_get_inc.status_code}: {resp_get_inc.text}"
    assert resp_get_inc.json()["quantity"] == 2

    # Action: Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verification: GET item returns 404
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=648  name='Orders Full Checkout Workflow' ---
def test_orders_full_checkout_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A", "street": "Downing", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    price = resp_cat.json()[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    # Action: Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json()["id"]

    # Verification: GET Order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    order_data = resp_get_order.json()
    assert order_data["customer"]["username"] == username
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["itemId"] == item_id
    assert order_data["items"][0]["quantity"] == 2

    # Verification: Search Orders
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in embedded_orders)

# --- id=649  name='Orders Negative Missing Fields And Malformed Uri' ---
def test_orders_negative_missing_fields_and_malformed_uri():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    price = resp_cat.json()[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    # Negative: Missing fields
    incomplete_payload = {
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp_missing = requests.post(get_url("orders", "/orders"), json=incomplete_payload, timeout=10)
    assert resp_missing.status_code == 406, f"Expected 406, got {resp_missing.status_code}: {resp_missing.text}"

    # Negative: Malformed URI
    malformed_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}invalid",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_malformed = requests.post(get_url("orders", "/orders"), json=malformed_payload, timeout=10)
    assert resp_malformed.status_code == 404, f"Expected 404, got {resp_malformed.status_code}: {resp_malformed.text}"

# --- id=650  name='Payment Authorization Append And Declined' ---
def test_payment_authorization_append_and_declined():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    pay_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "London", "country": "UK", "number": "1", "postcode": "123", "street": "Main"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"}
    }

    # Action: Authorize payment
    resp_pay1 = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert resp_pay1.status_code == 200, f"Expected 200, got {resp_pay1.status_code}: {resp_pay1.text}"
    assert resp_pay1.json()["authorised"] is True

    # Verification: GET Authorizations
    resp_get1 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert len(resp_get1.json()) == 1

    # Action: Authorize payment again
    resp_pay2 = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert resp_pay2.status_code == 200, f"Expected 200, got {resp_pay2.status_code}: {resp_pay2.text}"

    # Verification: GET Authorizations has 2 entries
    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert len(resp_get2.json()) == 2

    # Action: Declined payment (Amount > 100)
    declined_payload = pay_payload.copy()
    declined_payload["amount"] = 150.0
    resp_declined = requests.post(get_url("payment-http", "/payments"), json=declined_payload, timeout=10)
    assert resp_declined.status_code == 200, f"Expected 200, got {resp_declined.status_code}: {resp_declined.text}"
    assert resp_declined.json()["authorised"] is False

    # Verification: GET Authorizations has 3 entries
    resp_get3 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert len(resp_get3.json()) == 3
    assert resp_get3.json()[2]["authorised"] is False

# --- id=651  name='Shipping Creation And Retrieval' ---
def test_shipping_creation_and_retrieval():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    ship_payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"city": "London", "country": "UK", "number": "1", "postcode": "123", "street": "Main"}
    }

    # Action: Ship order
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id
    assert "trackingNumber" in resp_ship.json()

    # Verification: GET Shipment
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
    assert resp_get.json()["trackingNumber"] == resp_ship.json()["trackingNumber"]
