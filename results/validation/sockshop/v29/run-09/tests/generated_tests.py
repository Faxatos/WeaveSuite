# Tests generated in iteration 09
# Captured: 2026-06-21T15:18:55
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1348  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data["city"] == "London"
    assert addr_data["country"] == "UK"
    assert addr_data["number"] == "10"
    assert addr_data["postcode"] == "SW1"
    assert addr_data["street"] == "Baker St"
    assert addr_data["id"] == addr_id

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded_addrs = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == addr_id for a in embedded_addrs), "Address not found in customer's addresses"

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data["ccv"] == "123"
    assert card_data["expires"] == "12/25"
    assert card_data["id"] == card_id
    assert "*" in card_data["longNum"]
    assert card_data["longNum"].endswith("3456")

    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    embedded_cards = resp_cust_card.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in embedded_cards), "Card not found in customer's cards"

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

# --- id=1349  name='Cart Item Lifecycle' ---
def test_cart_item_lifecycle():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    assert len(socks) > 0, "Catalogue is empty"
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    username = random_string()

    item_payload = {"itemId": sock_id, "quantity": 2, "unitPrice": sock_price}
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    item_data = resp_get_item.json()
    assert item_data["itemId"] == sock_id
    assert item_data["quantity"] == 2
    assert item_data["unitPrice"] == sock_price

    resp_inc = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock_id, "quantity": 3, "unitPrice": sock_price}, timeout=10)
    assert resp_inc.status_code == 201, f"Expected 201, got {resp_inc.status_code}: {resp_inc.text}"

    resp_get_inc = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_get_inc.status_code == 200, f"Expected 200, got {resp_get_inc.status_code}: {resp_get_inc.text}"
    assert resp_get_inc.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=1350  name='End To End Order Placement' ---
def test_end_to_end_order_placement():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1", "street": "Baker St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]

    sock = requests.get(get_url("catalogue", "/catalogue"), timeout=10).json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]

    assert order_data["customer"]["username"] == username
    assert order_data["address"]["city"] == "London"
    assert order_data["card"]["expires"] == "12/25"
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["itemId"] == sock["id"]
    assert order_data["total"] == sock["price"]

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json()["id"] == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders), "Order not found in customer search"

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auths = resp_pay.json()
    assert len(auths) > 0, "No payment authorizations found"
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data["orderId"] == order_id
    assert "carrier" in ship_data
    assert "trackingNumber" in ship_data

# --- id=1351  name='Order Placement Empty Cart 406' ---
def test_order_placement_empty_cart_406():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1", "street": "Baker St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1352  name='Order Placement Invalid Uri 404' ---
def test_order_placement_invalid_uri_404():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    sock = requests.get(get_url("catalogue", "/catalogue"), timeout=10).json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid-format-no-colon",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=1347  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_data = resp_get.json()
    assert user_data["username"] == username
    assert user_data["email"] == email
    assert user_data["firstName"] == "Test"
    assert user_data["lastName"] == "User"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    resp_reg_fail = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_reg_fail.status_code == 409, f"Expected 409, got {resp_reg_fail.status_code}: {resp_reg_fail.text}"
