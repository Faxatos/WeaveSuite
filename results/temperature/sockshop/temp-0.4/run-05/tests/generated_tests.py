# Tests generated in iteration 05
# Captured: 2026-06-29T19:04:43
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=326  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    reg_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username
    assert resp_get.json().get("email") == email
    assert "password" not in resp_get.json()

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=327  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@a.com", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_payload = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json().get("city") == "City"
    assert resp_get_addr.json().get("id") == addr_id

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded_addrs = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in embedded_addrs)

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json().get("id") == card_id
    assert resp_get_card.json().get("longNum") == "************3456"

    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    embedded_cards = resp_cust_card.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in embedded_cards)

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

# --- id=328  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0

    item_id = items[0].get("id")
    assert item_id is not None

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json().get("id") == item_id

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

    resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid_nonexistent_id_123"), timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=329  name='Carts Management' ---
def test_carts_management():
    customer_id = random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    assert resp_add.json().get("itemId") == item_id
    assert resp_add.json().get("quantity") == 2

    resp_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    assert any(i.get("itemId") == item_id and i.get("quantity") == 2 for i in resp_items.json())

    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": unit_price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=330  name='Orders End To End Placement' ---
def test_orders_end_to_end_placement():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@a.com", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_payload = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username
    assert len(order_data.get("items", [])) == 1
    assert order_data.get("items")[0].get("itemId") == item_id

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    resp_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_payment.status_code == 200, f"Expected 200, got {resp_payment.status_code}: {resp_payment.text}"
    payments = resp_payment.json()
    assert len(payments) > 0
    assert payments[0].get("orderId") == order_id
    assert payments[0].get("authorised") is True

    resp_shipping = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_shipping.status_code == 200, f"Expected 200, got {resp_shipping.status_code}: {resp_shipping.text}"
    assert resp_shipping.json().get("orderId") == order_id
    assert "carrier" in resp_shipping.json()

# --- id=331  name='Orders Placement Negative Invalid Uri' ---
def test_orders_placement_negative_invalid_uri():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@a.com", "firstName": "A", "lastName": "B"}, timeout=10)

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=332  name='Orders Placement Negative Missing Fields' ---
def test_orders_placement_negative_missing_fields():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@a.com", "firstName": "A", "lastName": "B"}, timeout=10)

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

# --- id=333  name='User Customer Deletion' ---
def test_user_customer_deletion():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@a.com", "firstName": "A", "lastName": "B"}, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=334  name='Payment Http Authorization' ---
def test_payment_http_authorization():
    order_id = str(uuid.uuid4())

    payment_payload = {
        "address": {
            "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "A", "lastName": "B"
        },
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 1
    assert resp_get.json()[0].get("authorised") is True

    payment_payload["amount"] = 150.0
    resp_pay_declined = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay_declined.status_code == 200, f"Expected 200, got {resp_pay_declined.status_code}: {resp_pay_declined.text}"
    assert resp_pay_declined.json().get("authorised") is False

    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert len(resp_get2.json()) == 2
    assert resp_get2.json()[1].get("authorised") is False

# --- id=335  name='Shipping Http Creation' ---
def test_shipping_http_creation():
    order_id = str(uuid.uuid4())

    shipping_payload = {
        "address": {
            "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id
    assert "carrier" in resp_ship.json()
    assert "trackingNumber" in resp_ship.json()

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
    assert resp_get.json().get("carrier") == resp_ship.json().get("carrier")
