# Tests generated in iteration 10
# Captured: 2026-06-21T01:03:07
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1066  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if socks:
        sock_id = socks[0]["id"]
        url_id = get_url("catalogue", f"/catalogue/{sock_id}")
        resp_id = requests.get(url_id, timeout=10)
        assert resp_id.status_code == 200, f"Expected 200, got {resp_id.status_code}: {resp_id.text}"
        assert resp_id.json()["id"] == sock_id

# --- id=1067  name='Catalogue Sock Not Found' ---
def test_catalogue_get_sock_not_found():
    url = get_url("catalogue", "/catalogue/non-existent-id-12345")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1068  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    email = f"{username}@example.com"

    url = get_url("user", "/register")
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    cust_data = cust_resp.json()
    assert cust_data.get("username") == username
    assert cust_data.get("email") == email
    assert "password" not in cust_data or cust_data["password"] != password

# --- id=1069  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "F",
        "lastName": "L"
    }
    url = get_url("user", "/register")
    resp1 = requests.post(url, json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(url, json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1070  name='User Add Address' ---
def test_user_add_address():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    addr_url = get_url("user", "/addresses")
    resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    addr_id = resp.json().get("id")
    assert addr_id is not None

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    get_resp = requests.get(get_addr_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    addr_data = get_resp.json()
    assert addr_data.get("city") == "City"
    assert addr_data.get("id") == addr_id

# --- id=1071  name='User Add Card' ---
def test_user_add_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_url = get_url("user", "/cards")
    resp = requests.post(card_url, json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    card_id = resp.json().get("id")
    assert card_id is not None

    get_card_url = get_url("user", f"/cards/{card_id}")
    get_resp = requests.get(get_card_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    card_data = get_resp.json()
    assert card_data.get("id") == card_id
    assert card_data.get("longNum", "").endswith("3456")
    assert "1234567890" not in card_data.get("longNum", "")

# --- id=1072  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "John"}, timeout=10)

    del_url = get_url("user", f"/customers/{username}")
    del_resp = requests.delete(del_url, timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
    assert del_resp.json().get("status") is True

    get_url_cust = get_url("user", f"/customers/{username}")
    get_resp = requests.get(get_url_cust, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("username") == username
    assert not get_resp.json().get("firstName")

# --- id=1073  name='Carts Add And Item' ---
def test_carts_add_and_get_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp = requests.get(get_url_item, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    item_data = get_resp.json()
    assert item_data.get("itemId") == item_id
    assert item_data.get("quantity") == 2
    assert item_data.get("unitPrice") == 10.5

# --- id=1074  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    url = get_url("carts", f"/carts/{customer_id}/items")
    requests.post(url, json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    patch_resp = requests.patch(url, json={"itemId": item_id, "quantity": 5, "unitPrice": 10.0}, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("quantity") == 5

# --- id=1075  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    url = get_url("carts", f"/carts/{customer_id}/items")
    requests.post(url, json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    del_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    del_resp = requests.delete(del_url, timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(del_url, timeout=10)
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

# --- id=1076  name='Carts Merge Carts' ---
def test_carts_merge_carts():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id, "quantity": 3, "unitPrice": 5.0}, timeout=10)

    merge_url = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    merge_resp = requests.get(merge_url, timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("quantity") == 3

# --- id=1077  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    merge_url = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    merge_resp = requests.get(merge_url, timeout=10)
    assert merge_resp.status_code == 404, f"Expected 404, got {merge_resp.status_code}: {merge_resp.text}"

# --- id=1078  name='Orders Create Order' ---
def test_orders_create_order():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "O", "lastName": "O"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    item_id = f"item_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": 15.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    order_url = get_url("orders", "/orders")
    resp = requests.post(order_url, json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_data = resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username
    assert order_data.get("total") == 30.0

    get_order_url = get_url("orders", f"/orders/{order_id}")
    get_resp = requests.get(get_order_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("id") == order_id

# --- id=1079  name='Orders Create Order Missing Cart' ---
def test_orders_create_order_missing_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    order_url = get_url("orders", "/orders")
    resp = requests.post(order_url, json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1080  name='Orders Create Order Invalid Address Uri' ---
def test_orders_create_order_invalid_address_uri():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    resp = requests.post(order_url, json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1081  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    url = get_url("payment-http", "/payments")
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    get_resp = requests.get(get_url_pay, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id
    assert auths[-1].get("authorised") is True

# --- id=1082  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    url = get_url("payment-http", "/payments")
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    get_resp = requests.get(get_url_pay, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id
    assert auths[-1].get("authorised") is False

# --- id=1083  name='Shipping Ship Order' ---
def test_shipping_ship_order():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    url = get_url("shipping-http", "/shipping")
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id
    assert shipment.get("carrier") is not None

    get_url_ship = get_url("shipping-http", f"/shipping/{order_id}")
    get_resp = requests.get(get_url_ship, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("orderId") == order_id
