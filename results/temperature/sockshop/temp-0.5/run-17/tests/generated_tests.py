# Tests generated in iteration 17
# Captured: 2026-07-04T21:26:10
# Count:    17
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=577  name='User Register And Login Success' ---
def test_user_register_and_login_success():
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

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=578  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{generate_random_string()}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=579  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_data = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Springfield",
        "postcode": "12345",
        "country": "USA"
    }

    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    created_id = resp.json().get("id")
    assert created_id is not None

    resp_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addresses = resp_get.json().get("_embedded", {}).get("address", [])
    assert len(addresses) == 1
    assert addresses[0]["id"] == created_id
    assert addresses[0]["city"] == "Springfield"

# --- id=580  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_data = {
        "userID": username,
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123"
    }

    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    created_id = resp.json().get("id")
    assert created_id is not None

    resp_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cards = resp_get.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 1
    assert cards[0]["id"] == created_id
    assert cards[0]["longNum"].endswith("3456")
    assert "*" in cards[0]["longNum"]

# --- id=581  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_again.status_code == 200, f"Expected 200, got {resp_again.status_code}: {resp_again.text}"
    assert resp_again.json().get("status") is False

# --- id=582  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    if len(socks) > 0:
        assert "id" in socks[0]
        assert "name" in socks[0]

# --- id=583  name='Catalogue Sock By Id' ---
def test_catalogue_get_sock_by_id():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    socks = resp_list.json()
    if len(socks) == 0:
        pytest.skip("No socks in catalogue to test")

    sock_id = socks[0]["id"]
    resp = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == sock_id

# --- id=584  name='Catalogue Sock Not Found' ---
def test_catalogue_get_sock_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-999"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=585  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    customer_id = f"cust_{generate_random_string()}"
    item_data = {
        "itemId": "item-1",
        "quantity": 2,
        "unitPrice": 15.5
    }

    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item-1"
    assert items[0]["quantity"] == 2

# --- id=586  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = f"cust_{generate_random_string()}"
    item_data = {"itemId": "item-1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)

    update_data = {"itemId": "item-1", "quantity": 5, "unitPrice": 10.0}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/item-1"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 5

# --- id=587  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{generate_random_string()}"
    item_data = {"itemId": "item-1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/item-1"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/item-1"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=588  name='Orders Create Success' ---
def test_orders_create_success():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"
    }, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={
        "userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"
    }, timeout=10)
    card_id = card_resp.json().get("id")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item-1", "quantity": 2, "unitPrice": 10.0
    }, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    assert "id" in order
    assert order["customer"]["username"] == username
    assert len(order["items"]) == 1
    assert order["total"] == 20.0

    order_id = order["id"]
    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders_list = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert len(orders_list) > 0
    assert any(o["id"] == order_id for o in orders_list)

# --- id=589  name='Orders Create Missing Field' ---
def test_orders_create_missing_field():
    username = f"user_{generate_random_string()}"
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1",
        "card": f"/cards/{username}:3456"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=590  name='Orders Create Invalid Uri Format' ---
def test_orders_create_invalid_uri_format():
    username = f"user_{generate_random_string()}"
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid-format",
        "card": f"/cards/{username}:3456",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=591  name='Payment Authorize Success' ---
def test_payment_authorize_success():
    order_id = f"ord_{generate_random_string()}"
    payment_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"}
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is True
    assert auths[0]["orderId"] == order_id

# --- id=592  name='Payment Authorize Decline' ---
def test_payment_authorize_decline():
    order_id = f"ord_{generate_random_string()}"
    payment_req = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"}
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

# --- id=593  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id = f"ord_{generate_random_string()}"
    shipping_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"}
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
    assert resp_get.json()["trackingNumber"] == shipment["trackingNumber"]
