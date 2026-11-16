# Tests generated in iteration 12
# Captured: 2026-07-05T07:44:20
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=787  name='Carts Add Item And' ---
def test_carts_add_item_and_delete():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.5
    }

    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("itemId") == item_id
    assert resp_get.json().get("quantity") == 2
    assert resp_get.json().get("unitPrice") == 15.5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=788  name='Orders Create Successful Order' ---
def test_orders_create_successful_order():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "John", "lastName": "Doe", "email": "j@d.com"}, timeout=10)

    addr_data = {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_data = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp_card.json().get("id")

    item_data = {"itemId": "03fef6ac-1896-4ce8-bd69-b798f85c6e0b", "quantity": 1, "unitPrice": 10.0}
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    if resp_cat.status_code == 200 and len(resp_cat.json()) > 0:
        item_data["itemId"] = resp_cat.json()[0]["id"]
        item_data["unitPrice"] = resp_cat.json()[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    fetched_order = resp_order_get.json()
    assert fetched_order.get("id") == order_id
    assert fetched_order.get("customer", {}).get("username") == username
    assert fetched_order.get("total") == order.get("total")
    assert len(fetched_order.get("items", [])) == len(order.get("items", []))
    assert fetched_order.get("status") in ["CREATED", "PAID", "SHIPPED", "PAYMENT_FAILED", "SHIPMENT_FAILED"]

# --- id=789  name='Orders Create Missing Field 406' ---
def test_orders_create_missing_field_406():
    order_req = {
        "customer": "/customers/someuser"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

# --- id=790  name='Orders Create Invalid Composite Id 404' ---
def test_orders_create_invalid_composite_id_404():
    order_req = {
        "customer": "/customers/someuser",
        "address": "/addresses/invalid_id_format",
        "card": "/cards/someuser:1234",
        "items": "/carts/someuser/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=791  name='Payment Authorize And History' ---
def test_payment_authorize_and_history():
    order_id = str(uuid.uuid4())

    payment_req_1 = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"},
        "card": {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123"}
    }
    resp_pay_1 = requests.post(get_url("payment-http", "/payments"), json=payment_req_1, timeout=10)
    assert resp_pay_1.status_code == 200, f"Expected 200, got {resp_pay_1.status_code}: {resp_pay_1.text}"
    assert resp_pay_1.json().get("authorised") is True

    payment_req_2 = payment_req_1.copy()
    payment_req_2["amount"] = 150.0
    resp_pay_2 = requests.post(get_url("payment-http", "/payments"), json=payment_req_2, timeout=10)
    assert resp_pay_2.status_code == 200, f"Expected 200, got {resp_pay_2.status_code}: {resp_pay_2.text}"
    assert resp_pay_2.json().get("authorised") is False

    resp_history = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_history.status_code == 200, f"Expected 200, got {resp_history.status_code}: {resp_history.text}"
    history = resp_history.json()
    assert isinstance(history, list)
    assert len(history) == 2
    assert history[0].get("authorised") is True
    assert history[1].get("authorised") is False

# --- id=792  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = str(uuid.uuid4())
    ship_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"}
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment
    assert "deliveryDate" in shipment

    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"
    shipment_get = resp_ship_get.json()
    assert shipment_get.get("orderId") == order_id
    assert shipment_get.get("carrier") == shipment.get("carrier")
    assert shipment_get.get("trackingNumber") == shipment.get("trackingNumber")
    assert shipment_get.get("deliveryDate") == shipment.get("deliveryDate")

# --- id=782  name='User Registration And Conflict' ---
def test_user_registration_and_conflict():
    username = f"user_{generate_random_string()}"
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
    customer = resp_get.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"
    assert "password" not in customer

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=783  name='User Login Success And Failure' ---
def test_user_login_success_and_failure():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=784  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{generate_random_string()}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=785  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_data = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_obj = resp_addr_get.json()
    assert addr_obj.get("city") == "Test City"
    assert addr_obj.get("id") == addr_id

    card_data = {
        "longNum": "1234567812345678",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_obj = resp_card_get.json()
    assert card_obj.get("id") == card_id
    assert "12345678" not in card_obj.get("longNum", "")
    assert "*" in card_obj.get("longNum", "")

# --- id=786  name='Catalogue And Not Found' ---
def test_catalogue_get_and_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json()["id"] == item_id

    resp_not_found = requests.get(get_url("catalogue", "/catalogue/non_existent_id_12345"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"
