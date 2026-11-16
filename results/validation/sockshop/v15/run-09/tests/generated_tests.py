# Tests generated in iteration 09
# Captured: 2026-06-07T07:44:11
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1326  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1327  name='User Register Duplicate' ---
def test_user_register_duplicate():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp_get1 = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"

    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1328  name='User Login Invalid' ---
def test_user_login_invalid():
    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth("invalid_user", "wrong_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1329  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "London", f"Expected city London, got {resp_addr_get.text}"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    resp_addr_list = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_list.status_code == 200, f"Expected 200, got {resp_addr_list.status_code}: {resp_addr_list.text}"
    addresses = resp_addr_list.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses), "Address should be deleted"

    resp_card_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

    resp_card_list = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_list.status_code == 200, f"Expected 200, got {resp_card_list.status_code}: {resp_card_list.text}"
    cards = resp_card_list.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards), "Card should be deleted"

# --- id=1330  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        sock_id = items[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=1331  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-sock-id-123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1332  name='Carts Add Items Cumulative' ---
def test_carts_add_items_cumulative():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_payload_1 = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_1, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json().get("quantity") == 2, f"Expected quantity 2, got {resp_get1.text}"

    item_payload_2 = {"itemId": item_id, "quantity": 3, "unitPrice": 10.5}
    resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_2, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5, f"Expected quantity 5, got {resp_get2.text}"

    item_payload_3 = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}
    resp3 = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_3, timeout=10)
    assert resp3.status_code == 202, f"Expected 202, got {resp3.status_code}: {resp3.text}"

    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert resp_get3.json().get("quantity") == 1, f"Expected quantity 1, got {resp_get3.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get4.status_code == 404, f"Expected 404, got {resp_get4.status_code}: {resp_get4.text}"

# --- id=1333  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    resp_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 5.0}, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_add_get = requests.get(get_url("carts", f"/carts/{session_id}/items/{item_id}"), timeout=10)
    assert resp_add_get.status_code == 200, f"Expected 200, got {resp_add_get.status_code}: {resp_add_get.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=1334  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1335  name='Orders Create Success' ---
def test_orders_create_success():
    username = f"user_{generate_random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "sock1", "quantity": 2, "unitPrice": 10.0}, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/sock1"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

# --- id=1336  name='Orders Create Payment Declined' ---
def test_orders_create_payment_declined():
    username = f"user_{generate_random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "sock1", "quantity": 1, "unitPrice": 150.0}, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/sock1"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1337  name='Orders Not Found' ---
def test_orders_not_found():
    resp = requests.get(get_url("orders", "/orders/invalid-order-id-123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1338  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True, f"Expected authorised True, got {resp.text}"

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=1339  name='Shipping Ship' ---
def test_shipping_ship():
    order_id = f"order_{generate_random_string()}"
    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St"},
        "itemCount": 2,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
