# Tests generated in iteration 07
# Captured: 2026-06-29T04:44:45
# Count:    28
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=107  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=108  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=109  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("invalid_user", "invalid_pwd"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=110  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("city") == "London"
    assert data.get("country") == "UK"
    assert data.get("number") == "10"
    assert data.get("postcode") == "EC1A 1BB"
    assert data.get("street") == "Baker St"

# --- id=111  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("expires") == "12/25"
    assert data.get("longNum", "").endswith("3456")

# --- id=112  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_again.status_code == 200, f"Expected 200, got {resp_again.status_code}: {resp_again.text}"
    assert resp_again.json().get("status") is False

# --- id=113  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.5
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    assert resp.json().get("itemId") == item_id

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("itemId") == item_id
    assert resp_get.json().get("quantity") == 2
    assert resp_get.json().get("unitPrice") == 15.5

# --- id=114  name='Carts Update Item' ---
def test_carts_update_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.0}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 5
    assert resp_get.json().get("unitPrice") == 10.0

# --- id=115  name='Carts Item' ---
def test_carts_delete_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=116  name='Carts Cart' ---
def test_carts_delete_cart():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

# --- id=117  name='Carts Merge' ---
def test_carts_merge():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    payload = {"itemId": item_id, "quantity": 3, "unitPrice": 12.0}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=payload, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 3

# --- id=118  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"invalid_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=119  name='Catalogue All And Specific' ---
def test_catalogue_get_all_and_specific():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0].get("id")

    resp_specific = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_specific.status_code == 200, f"Expected 200, got {resp_specific.status_code}: {resp_specific.text}"
    assert resp_specific.json().get("id") == item_id

# --- id=120  name='Catalogue Not Found' ---
def test_catalogue_get_not_found():
    item_id = f"invalid_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=121  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=122  name='Catalogue Size' ---
def test_catalogue_get_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

# --- id=123  name='Catalogue Images' ---
def test_catalogue_get_images():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    image_urls = items[0].get("imageUrl", [])
    if image_urls:
        image_path = image_urls[0]
        image_name = image_path.split("/")[-1]
        resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=124  name='Catalogue Images Not Found' ---
def test_catalogue_get_images_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=125  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "John", "lastName": "Doe", "email": "j@d.com"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": 50.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("total") == 100.0

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("id") == order_id
    assert get_data.get("customer", {}).get("username") == username
    assert get_data.get("address", {}).get("city") == "London"
    assert get_data.get("total") == 100.0
    assert len(get_data.get("items", [])) == 1
    assert get_data["items"][0].get("itemId") == item_id

# --- id=126  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=127  name='Orders Create Invalid Composite Id' ---
def test_orders_create_invalid_composite_id():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_not_composite",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=128  name='Orders Create Payment Declined' ---
def test_orders_create_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "L", "country": "UK", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 10, "unitPrice": 15.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=129  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "L", "country": "UK", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    order_id = order_resp.json().get("id")

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders)

# --- id=130  name='Orders Not Found' ---
def test_orders_get_not_found():
    resp = requests.get(get_url("orders", f"/orders/invalid_{uuid.uuid4().hex[:8]}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=131  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId=invalid_{uuid.uuid4().hex[:8]}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=132  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = _setup_order()
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[-1].get("authorised") is True

# --- id=133  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = _setup_order()
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[-1].get("authorised") is False

# --- id=134  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = _setup_order()
    payload = {
        "orderId": order_id,
        "itemCount": 2,
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_shipment = resp_get.json()
    assert get_shipment.get("orderId") == order_id
