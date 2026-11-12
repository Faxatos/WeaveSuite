"""
Sockshop OpenAPI spec patches — final merged set.

Provenance: derived by reading each service's source and its JAX-RS / MicroProfile
OpenAPI annotations (white-box), then correcting where the generated spec diverges
from the implementation. This is consistent with the white-box validation metrics
(instruction coverage, mutation score — both line-based); the LLM that generates the
tests still sees only the corrected spec (black-box generation).

Every entry is justified two ways, and both are stated in its comment:
  - which criterion it serves, and
  - WHY it is necessary, i.e. the baseline failure that its OMISSION would cause.

Minimality is bounded differently for the two classes:
  CLASS 1 — FIDELITY (a,b,c,d): declare the implementation's actual reachable response
    surface accurately and completely, inventing nothing. Bound = accuracy/completeness,
    not edit size. (This is why the full Order object is declared: the response exists and
    was entirely undocumented; under-declaring a reachable response is itself an (a)/(b) defect.)
  CLASS 2 — NECESSITY (e,f): add a behavioural fact ONLY if a faithful, non-inventing
    generator would otherwise produce a test that FAILS the unmutated baseline or cannot
    exercise the operation. Facts that would only raise mutation score were excluded
    (e.g. the shipping carrier/itemCount rules; see also KubePay's fixed top-up amount).

Excluded by the gate (kept here as a record of the line):
  - addressId/cardId "not the URI identifier" notes: redundant once `id` is correct →
    a faithful model already passes, so not necessary.
  - "use /customers/{id}/... instead" redirects: the real listing endpoints are documented
    on their own; the model can choose correctly without being told → not necessary.
  - shipping carrier/trackingNumber branching on itemCount: pure effectiveness enrichment.
"""
from typing import Any, Dict


# ============================================================================
# USERS  (title substring: "User API")
# Address/Card ARE typed returns (getAddress/getCard), so their schemas exist and we
# narrow to the diverging property. List/create endpoints return raw Response, so their
# bodies are absent and must be declared.
# ============================================================================
USER_PATCHES: Dict[str, Any] = {

    # (a) FIDELITY + (e) PRECONDITION. Generated `id` is an OBJECT (AddressId{user,addressId})
    # because the scanner ignores the JSON-B adapter; the wire value is the composite STRING.
    # Omit -> model treats id as object (can't build URI) or uses addressId "1" -> GET /addresses/1
    # -> AddressId split throws -> baseline failure.
    # CODE: User.addAddress sets addressId="1","2"...; Address.getId()=AddressId(user,addressId);
    #       AddressId.toString()="user:addressId"; AddressId(String) requires exactly 2 ':' parts.
    "components.schemas.Address.properties.id": {
        "type": "string",
        "description": (
            "Composite address identifier '{username}:{addressId}'; the bare addressId is not accepted as the URI identifier. "
        ),
    },

    # (a) FIDELITY + (e) PRECONDITION. Same as Address; VERIFIED in code (not by analogy).
    # Omit -> same composite-id baseline failure on /cards/{id}.
    # CODE: User.addCard sets cardId=last4(); Card.getId()=CardId(user,cardId)->"user:last4".
    "components.schemas.Card.properties.id": {
        "type": "string",
        "description": (
            "Composite card identifier '{username}:{last4}'; the bare last4 (cardId) is not accepted as the URI identifier."
        ),
    },
    # (a) FIDELITY. longNum is returned MASKED; generated description says only "Card number".
    # Omit -> test creates card with longNum X, asserts GET returns X -> baseline failure (masked).
    # CODE: CardsResource.getCard/getCustomerCards return card.mask() (all but last 4 -> '*').
    "components.schemas.Card.properties.longNum.description": (
        "Card number. Returned masked in all responses (every digit except the last four replaced with '*');"
    ),

    # (b) COMPLETENESS. List endpoints return raw Response -> body schema absent.
    # Omit -> test does addresses[0] on a dict -> KeyError -> baseline failure.
    # CODE: JsonHelpers.embed(name,value) -> {"_embedded": {name: value}}.
    "components.schemas.AddressCollection": {
        "type": "object",
        "properties": {"_embedded": {"type": "object", "properties": {
            "address": {"type": "array", "items": {"$ref": "#/components/schemas/Address"}}},
            "required": ["address"]}},
    },
    "components.schemas.CardCollection": {
        "type": "object",
        "properties": {"_embedded": {"type": "object", "properties": {
            "card": {"type": "array", "items": {"$ref": "#/components/schemas/Card"}}},
            "required": ["card"]}},
    },

    # (a)/(b) FIDELITY. POST returns {"id": "<composite>"}; body absent.
    # Omit -> workflow can't recover the new resource's id -> guesses -> baseline failure.
    # CODE: registerAddress/registerCard -> Response.ok(obj().add("id", id.toString())).
    "components.schemas.CreatedResourceId": {
        "type": "object",
        "properties": {"id": {"type": "string", "description": (
            "Composite id of the created resource ('{username}:{sequence}' for addresses, '{username}:{last4}' for cards).")}},
    },

    # (a) FIDELITY. Top-level list endpoints are hardcoded empty.
    # Omit -> test POSTs an address then expects to see it in GET /addresses -> baseline failure.
    # (Redirect clause intentionally dropped: the real listing endpoint is documented below,
    #  so the model can choose it without being told -> redirect is not necessary.)
    # CODE: getAllAddresses/getAllCards return embed(name, Collections.emptyList()) unconditionally.
    "paths./addresses.get.responses.200": {
        "description": "Always returns an empty HAL collection, regardless of stored data or authentication.",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AddressCollection"}}},
    },
    "paths./cards.get.responses.200": {
        "description": "Always returns an empty HAL collection, regardless of stored data or authentication.",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CardCollection"}}},
    },

    # (b) COMPLETENESS. Real listing endpoints return raw Response -> body absent.
    # Omit -> a passing listing test cannot be formed against the actual data.
    "paths./customers/{id}/addresses.get.responses.200": {
        "description": "HAL collection of the customer's addresses.",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AddressCollection"}}},
    },
    "paths./customers/{id}/cards.get.responses.200": {
        "description": "HAL collection of the customer's cards.",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CardCollection"}}},
    },
    # (f) READ CREATES-ON-MISS. getCustomer -> getOrCreate(id): GET /customers/{id} returns 200 for
    # ANY id (a non-existent/deleted id yields a newly created empty customer with only the username),
    # so deletion is NOT observable via this GET.
    # Omit -> a "delete then GET expecting non-200" test gets 200 (empty resurrected customer) -> baseline failure.
    # CODE: CustomersResource.getCustomer -> Response.ok(users.getOrCreate(id)); getOrCreate creates if absent.
    "paths./customers/{id}.get.responses.200.description":
        "The customer. Returned for any id: a non-existent or previously-deleted id yields a newly "
        "created empty customer (only the username is populated), so this endpoint never returns 404 "
        "and deletion is not observable here.",

    # (a)/(b) FIDELITY. deleteCustomer returns 200 with body {"status": <was a user removed>}; raw
    # Response -> body absent. This is the observable that reflects deletion (use it instead of a GET).
    # CODE: deleteCustomer -> Response.ok(obj().add("status", prev != null)) where prev = removeUser(id).
    "paths./customers/{id}.delete.responses.200": {
        "description": "Deletion result: {\"status\": true} if a customer was removed, {\"status\": false} if none existed for this id.",
        "content": {"application/json": {"schema": {"type": "object",
            "properties": {"status": {"type": "boolean"}}}}},
    },
    # (a)/(b) FIDELITY. POST bodies absent; status is 200 (Response.ok).
    "paths./addresses.post.responses.200": {
        "description": "Created; body carries the composite id of the new address.",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreatedResourceId"}}},
    },
    "paths./cards.post.responses.200": {
        "description": "Created; body carries the composite id of the new card.",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreatedResourceId"}}},
    },
}


# ============================================================================
# ORDERS  (title substring: "Order API")
# Every endpoint returns raw Response -> the generated spec has NO response bodies and NO
# Order graph. This is the dominant gap and the reason the Order schema is declared in full.
# ============================================================================
ORDERS_PATCHES: Dict[str, Any] = {

    # (e) PRECONDITION (narrowed to the diverging property descriptions, not the whole schema).
    # Omit -> model builds plausible URIs that fail the prefix checks -> 406 -> baseline failure
    # on a test expecting 201.
    # CODE (OrderResource.newOrder): 406 if any field null OR prefix checks fail:
    #   items startsWith "/carts/" AND endsWith "/items"; address "/addresses/"; card "/cards/";
    #   customer "/customers/". address/card segment must be the composite id for the downstream fetch.
    "components.schemas.NewOrderRequest.properties.customer.description":
        "URI of the customer resource; path must start with '/customers/'.",
    "components.schemas.NewOrderRequest.properties.address.description":
        ("URI of the address resource; path must start with '/addresses/' and the segment after it "
         "must be the composite address id '{username}:{sequence}'."),
    "components.schemas.NewOrderRequest.properties.card.description":
        ("URI of the card resource; path must start with '/cards/' and the segment after it must be "
         "the composite card id '{username}:{last4}'."),
    "components.schemas.NewOrderRequest.properties.items.description":
        ("URI of the cart ITEMS COLLECTION; path must start with '/carts/' and end with '/items'"),

    # (b) COMPLETENESS. The 201 response IS this object; it was entirely undocumented (raw Response).
    # Declared in full because under-declaring a reachable response is itself an (a)/(b) defect;
    # every field is real (from Order.java + nested models), nothing invented.
    "components.schemas.Order": {
        "type": "object",
        "description": "Denormalised order record returned by the orders service.",
        "properties": {
            "id": {"type": "string", "description": "Order identifier (8-char UUID prefix; serialized as 'id')."},
            "customer": {"type": "object", "properties": {
                "username": {"type": "string", "description": "Customer id (serialized as 'username')."},
                "firstName": {"type": "string"}, "lastName": {"type": "string"}, "email": {"type": "string"}}},
            "address": {"type": "object", "properties": {
                "number": {"type": "string"}, "street": {"type": "string"}, "city": {"type": "string"},
                "postcode": {"type": "string"}, "country": {"type": "string"}}},
            "card": {"type": "object", "properties": {
                "longNum": {"type": "string", "description": "Card number (masked, as supplied by the users service)."},
                "expires": {"type": "string"}, "ccv": {"type": "string"}}},
            "date": {"type": "string", "format": "date-time"},
            "total": {"type": "number", "format": "float", "description": "Sum of quantity*unitPrice over items."},
            "items": {"type": "array", "items": {"type": "object", "properties": {
                "itemId": {"type": "string"}, "quantity": {"type": "integer"},
                "unitPrice": {"type": "number", "format": "float"}}}},
            "payment": {"type": "object", "properties": {
                "authorised": {"type": "boolean"}, "message": {"type": "string"}}},
            "shipment": {"type": "object", "properties": {
                "carrier": {"type": "string"}, "trackingNumber": {"type": "string"},
                "deliveryDate": {"type": "string", "format": "date"}}},
            "status": {"type": "string", "enum": [
                "CREATED", "PAID", "SHIPPED", "PAYMENT_FAILED", "SHIPMENT_FAILED"]},
        },
    },

    # (f) COUNTER-INTUITIVE SUCCESS + precondition. A well-formed reference to an address/card that
    # no longer exists is TOLERATED: the order is still created (201) with that nested object empty.
    # Cart must be non-empty with total in (0,100].
    # Omit -> a "delete resource then order" test expects 404 and gets 201 -> baseline failure.
    # CODE: OrderResource.newOrder fetches each ref; a null/empty fetch is not fatal (observed:
    #       address {} on a deleted-address order); payment/shipment still run on the cart total.
    "paths./orders.post.responses.201": {
        "description": (
            "Order created, paid, and shipped; returns the full Order."
            "A referenced address or card that no longer exists is tolerated: "
            "the order is created with that nested object empty. Requires a non-empty cart"),
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Order"}}},
    },
    # (d) ERROR ACCURACY + (e) PRECONDITION. Two triggers, both 406 with body {"message": "..."}:
    # request structure (a field missing/null or a URI failing its prefix), and payment declined.
    # Omit the payment bound -> a cart total > 100, or an empty cart (total 0, e.g. a never-created
    # user), gets 406 -> baseline failure.
    # CODE: newOrder -> 406 on null field / prefix fail; PaymentDeclinedException -> 406;
    #       DefaultPaymentService authorizes only 0 < amount <= 100; total = sum(qty*unitPrice).
    "paths./orders.post.responses.406": {
        "description": (
            "Not Acceptable, body {\"message\": \"...\"}. Returned both when a required field (customer/address/card/items) "
            "is missing or any URI fails its required prefix, and when payment is declined. "),
        "content": {"application/json": {"schema": {"type": "object",
            "properties": {"message": {"type": "string"}}}}},
    },
    # (d) ERROR ACCURACY. 404 is NARROW: only when an address/card URI's id segment is not a
    # syntactically valid composite id and cannot be parsed. A well-formed id for a missing resource
    # does NOT 404 (it is tolerated -> 201, see above).
    # Omit -> a malformed-id test (/addresses/invalid) expects 406 and gets 404 -> baseline failure.
    # CODE: AddressId/CardId(String) require exactly 2 ':'-separated parts; a non-composite segment
    #       fails param conversion -> 404 ("No handler found for path: /addresses/invalid").
    "paths./orders.post.responses.404": {
        "description": (
            "Not Found: a referenced address or card URI's identifier is not a syntactically valid "
            "composite id of the form '{username}:{...}' and cannot be parsed. A well-formed "
            "identifier pointing to a resource that does not exist does not produce 404."),
    },


    # (a) FIDELITY. GET /orders/{id} 200 body absent (404 already declared in annotation).
    "paths./orders/{id}.get.responses.200": {
        "description": "The requested order.",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Order"}}},
    },
    # (a)/(b) FIDELITY. Search endpoint 200 body absent (404 already declared). Same opaque-Response
    # gap as the other order endpoints; included for consistent application of the gate.
    # CODE: OrderResource.wrap -> {"_embedded": {"customerOrders": [...]}}.
    "paths./orders/search/customerId.get.responses.200": {
        "description": "HAL collection of the customer's orders.",
        "content": {"application/json": {"schema": {"type": "object", "properties": {
            "_embedded": {"type": "object", "properties": {
                "customerOrders": {"type": "array", "items": {"$ref": "#/components/schemas/Order"}}}}}}}},
    },
}

PAYMENT_PATCHES: Dict[str, Any] = {

    # (a) FIDELITY. GET returns an ARRAY (body absent — raw Response), holding ALL authorizations
    # recorded for the orderId, sorted by time ascending (oldest first).
    # Omit -> test asserts a single object -> baseline failure (it's a list); and a test that
    # authorizes an order-placed orderId then asserts on auths[0] hits the order's earlier
    # authorization, not the one it just created -> baseline failure.
    # CODE: getOrderAuthorizations -> Response.ok(findAuthorizationsByOrder(orderId));
    #       DefaultPaymentRepository.findAuthorizationsByOrder filters by orderId and
    #       .sorted(Comparator.comparing(Authorization::getTime)).
    "paths./payments/{orderId}.get.responses.200": {
        "description": (
            "Array of all authorizations recorded for this orderId, sorted by time ascending "
            "(oldest first); empty array if none exist. Placing an order records an authorization "
            "under the order's id, so re-authorizing that id appends another entry rather than "
            "replacing it."),
        "content": {"application/json": {"schema": {
            "type": "array", "items": {"$ref": "#/components/schemas/Authorization"}}}},
    },

    # (e) OPERATIONAL SEMANTICS. authorize is append-only and the orderId is an arbitrary
    # identifier; it need not refer to an existing order.
    # Omit -> a decline test builds an order to obtain a "valid" orderId (already authorized
    # -> true by the order flow), then GET returns [order's true, decline] and an auths[0]-is-false
    # assertion hits the order's true authorization -> baseline failure.
    # CODE: PaymentResource.authorize always computes and calls payments.saveAuthorization(auth)
    #       with no existing-check (never replaces/dedups).
    "paths./payments.post.description": (
        "Authorize a payment for the given orderId. The orderId is an arbitrary identifier and "
        "need not refer to an existing order. Each call records a new authorization; it never "
        "replaces or deduplicates existing authorizations for the same orderId."),

    # (e) PRECONDITION on the caller-supplied amount (corrected to include the lower bound).
    # Omit -> test sends amount it believes is valid, asserts authorised=true, but amount<=0 or >100
    # -> authorised=false -> baseline failure.
    # CODE (DefaultPaymentService.authorize): fAuthorized = amount > 0 && amount <= payment.limit (default 100).
    "components.schemas.PaymentRequest.properties.amount.description": (
        "Payment amount. Authorized only when amount is greater than 0 and at most 100. "),

    # (f) COUNTER-INTUITIVE SUCCESS. A declined payment is still HTTP 200 (not a 4xx).
    # Omit -> a test exercising the decline path assumes a 4xx (REST convention) -> baseline failure.
    # CODE: authorize() always returns 200 with an Authorization carrying authorised=false on decline.
    "paths./payments.post.responses.200.description": (
        "Authorization result. A declined payment is also returned as HTTP 200 with authorised=false."),
}


# ============================================================================
# CARTS  (title substring: "Carts API")
# ============================================================================
CARTS_PATCHES: Dict[str, Any] = {

    # (c) UNREACHABLE RESPONSE + (e) IDEMPOTENCY. DELETE always returns 202; the annotation's 404
    # is never produced. Omit the removal -> a test that deletes a nonexistent cart expecting 404
    # gets 202 -> baseline failure. (mergeCarts' 404 IS reachable and is left untouched.)
    # NOTE: this REPLACES the whole 'responses' object to drop the 404 — the patch engine must
    #       replace (not deep-merge) at this key, or the 404 survives and (c) is not satisfied.
    # CODE: CartResource.deleteCart -> carts.deleteCart(id); return Response.accepted();  // always 202.
    "paths./carts/{customerId}.delete.responses": {
        "202": {"description": "Cart deleted. Also returns 202 when no cart existed for this customerId."}
    },
    "paths./carts-async/{customerId}.delete.responses": {
        "202": {"description": "Cart deleted. Also returns 202 when no cart existed for this customerId."}
    },
}


# ============================================================================
# Registry.  Shipping API and Catalog API were audited against source and found
# conformant (typed returns, reachable error codes), so they need no patch — the
# clean parallel to "criterion checked, no violation found."
# ============================================================================
PATCHES_BY_TITLE_SUBSTR: Dict[str, Dict[str, Any]] = {
    "User API": USER_PATCHES,
    "Order API": ORDERS_PATCHES,
    "Payment API": PAYMENT_PATCHES,
    "Carts API": CARTS_PATCHES,
}