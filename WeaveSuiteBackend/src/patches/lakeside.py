from typing import Any, Dict


CUSTOMER_CORE_PATCHES: Dict[str, Any] = {

    # (e) precondition. Static API key as an HTTP Bearer token in Authorization, required on every endpoint.
    # CODE: WebSecurityConfiguration anyRequest().authenticated(); APIKeyAuthenticationManager requires "Bearer ", strips it, checks the remainder against apikey.validkeys.
    "components.securitySchemes.bearerApiKey": {
        "type": "http",
        "scheme": "bearer",
        "description": (
            "Static API key supplied as a Bearer token in the Authorization header "
            "(Authorization: Bearer <key>). Required on every endpoint. "
            "Valid keys: b318ad736c6c844b, 999ab497f8ec1052, 9b93ebe19e16bbbd."
        ),
    },

    # (f) counter-intuitive asymmetry (+ pins the GET schema). GET /customers/{ids} returns a wrapper {"customers":[{...}]}; POST and PUT return the customer flat. A flat read of the GET (resp["firstname"]) yields null/KeyError.
    # CODE: CustomerInformationHolder.getCustomer -> CustomersResponseDto; create/update -> flat CustomerResponseDto.
    "components.schemas.CustomersResponseDto": {
        "type": "object",
        "properties": {
            "customers": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/CustomerResponseDto"},
                "description": "Matched customers; a single-id lookup returns a one-element array.",
            },
        },
        "description": (
            "Wrapper object. The customer fields (customerId, firstname, lastname, "
            "streetAddress, city, email, phoneNumber, ...) are not at the top level: they "
            "are nested inside customers[0]. A single-id GET still returns this wrapper, "
            "so read the customer as response['customers'][0]."
        ),
    },
    "paths./customers/{ids}.get.responses.200.content.application/json.schema": {
        "$ref": "#/components/schemas/CustomersResponseDto"
    },
    "paths./customers/{ids}.get.description": (
        "Returns a CustomersResponseDto wrapper even for a single id: the matched "
        "customers are in the customers array, so the customer is response.customers[0], "
        "not the top-level object. (POST /customers and PUT /customers/{id} instead return "
        "the flat customer directly.) The path accepts a comma-separated list of ids."
    ),
    "paths./customers/{customerId}.put.responses.200.content.application/json.schema": {
        "$ref": "#/components/schemas/CustomerResponseDto"
    },

    # (a) fidelity. phoneNumber is reparsed and reformatted (libphonenumber) on input, so the returned value differs from the submitted one.
    # CODE: CustomerFactory.formatPhoneNumber (create + update).
    "components.schemas.CustomerResponseDto.properties.phoneNumber.description": (
        "Telephone number, reformatted by the service on input: it is reparsed and re-"
        "emitted in a normalized form (libphonenumber), so the returned string almost "
        "always differs from the submitted one (e.g. submitted '555-8889' is returned as "
        "'5558889'; '+41791234567' as '079 123 45 67'). The exact normalized form is not "
        "derivable from the contract."
    ),

    # (a)/(e) fidelity. phoneNumber is listed optional but is mandatory in practice: create/update without it -> 500.
    # CODE: CustomerProfileUpdateRequestDto (create/update body); CustomerFactory.
    "components.schemas.CustomerProfileUpdateRequestDto.required": [
        "firstname", "lastname", "streetAddress", "postalCode", "city", "email", "phoneNumber"
    ],
    "components.schemas.CustomerProfileUpdateRequestDto.properties.phoneNumber.description": (
        "Required field: the service raises an internal error (500) on create "
        "or update if it is absent."
    ),
}

SELF_SERVICE_PATCHES: Dict[str, Any] = {

    # (e) precondition, for @PreAuthorize operations. Raw JWT in the X-Auth-Token header.
    # CODE: token.header=X-Auth-Token; AuthenticationTokenFilter; @EnableMethodSecurity + @PreAuthorize("isAuthenticated()") on the protected handlers.
    "components.securitySchemes.tokenAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-Auth-Token",
        "description": (
            "JWT obtained from POST /auth (login). It must be sent in the 'X-Auth-Token' "
            "request header as the raw token value. Do not place it in the 'Authorization' "
            "header: this service does not read 'Authorization', so an 'Authorization: "
            "Bearer <token>' request is treated as unauthenticated and rejected (401)."
        ),
    },

    # (a) fidelity. status is a constrained enum, not a free string: an unrecognized value is a silent no-op (200); a valid value from the wrong state (REQUEST_SUBMITTED) is an illegal transition.
    # CODE: respondToInsuranceQuote matches QUOTE_ACCEPTED/QUOTE_REJECTED; acceptQuote guarded by RequestStatus.canTransitionTo.
    "components.schemas.InsuranceQuoteResponseDto.properties.status": {
        "type": "string",
        "enum": ["QUOTE_ACCEPTED", "QUOTE_REJECTED"],
        "description": (
            "Customer decision on a drafted quote; must be 'QUOTE_ACCEPTED' or "
            "'QUOTE_REJECTED'. An unrecognised status string is ignored (the request is "
            "returned unchanged, 200). This is different from sending a recognised status "
            "from the wrong state: 'QUOTE_ACCEPTED'/'QUOTE_REJECTED' are only valid once "
            "the request is in QUOTE_RECEIVED (see the operation precondition); sending "
            "them from REQUEST_SUBMITTED is an illegal transition that the server rejects "
            "with HTTP 401 (an artifact of the deployed error handling), not a 200 no-op "
            "and not a 400."
        ),
    },

    # (e) identity precondition. The quote's customerInfo.customerId must be the logged-in user's own registered customer (POST /customers first).
    # CODE: createInsuranceQuoteRequest/respondToInsuranceQuote: loggedInCustomerId null, or != supplied customerId -> 401.
    "components.schemas.CustomerInfoDto.properties.customerId.description": (
        "The authenticated customer's own id, obtained from POST /customers (registration) "
        "in the same session; it is not an arbitrary value. A quote request or response "
        "whose customerId is not the logged-in user's own customer id is rejected (401), "
        "as is a session that has not yet registered a customer."
    ),

    # (a) FIDELITY. POST /auth/signup returns UserResponseDto with customerId = null, and the
    # service serializes with spring.jackson.default-property-inclusion=NON_NULL, so the field is
    # omitted from the signup response entirely (verified: keys == ['email']). A test that reads
    # response['customerId'] after signup raises KeyError. The customerId is assigned by
    # POST /customers (registration) and returned there.
    # CODE: AuthenticationController.signupUser -> new UserResponseDto(email, null);
    #       application.properties: spring.jackson.default-property-inclusion=NON_NULL.
    "components.schemas.UserResponseDto.properties.customerId.description": (
        "The id of the customer registered by this user via POST /customers. It is assigned "
        "only at registration: before then the user has no customer, and the property is "
        "omitted from the response rather than returned as null. It is therefore absent from "
        "the POST /auth/signup response and from GET /user until the customer is registered."
    ),
    "paths./auth/signup.post.responses.200.description": (
        "The newly created user. Only the email is returned: no customer exists yet, so the "
        "customerId property is omitted. Obtain the customerId from the response of POST "
        "/customers (registration), not from this response."
    ),


    # (e) cross-service + asynchronous precondition. Accept/reject requires QUOTE_RECEIVED, set when policy-management drafts a response and delivered to self-service over the message bus; from REQUEST_SUBMITTED the transition is illegal. A faithful test reaches QUOTE_RECEIVED first (and must poll for the asynchronous propagation before drafting/accepting).
    # CODE: acceptQuote -> RequestStatus.canTransitionTo; QUOTE_RECEIVED produced by policy-management respondToInsuranceQuoteRequest -> CustomerSelfServiceMessageProducer (ActiveMQ).
    "paths./insurance-quote-requests/{id}.patch.description": (
        "Accept or reject a drafted quote. Precondition: the request must already be in "
        "QUOTE_RECEIVED state, which Lakeside Mutual sets when it drafts a quote response "
        "(an operation on the policy-management back office). That status change reaches "
        "this service asynchronously over message bus, so after the back-office drafting "
        "step poll GET /insurance-quote-requests/{id} on this service until QUOTE_RECEIVED "
        "appears in statusHistory before accepting or rejecting (not visible immediately)."
        "Until then the request is in REQUEST_SUBMITTED; sending QUOTE_ACCEPTED or "
        "QUOTE_REJECTED in that state is an illegal status transition and the server "
        "responds with HTTP 401 (not a 200 no-op and not a 400). Reach QUOTE_RECEIVED "
        "first via the back-office drafting step before accepting or rejecting."
    ),
}

POLICY_PATCHES: Dict[str, Any] = {

    # (a) fidelity. Date fields accept ISO-8601 'Z' input but serialize in Jackson's default format (.000+00:00), so the returned string differs from the submitted one. Applies to every Date field; compare instants, not strings.
    # CODE: PolicyPeriodDto/PolicyDto use java.util.Date with no @JsonFormat.
    "components.schemas.PolicyPeriodDto.description": (
        "Date fields are returned in the service's default JSON date format; input "
        "may use the trailing-'Z' ISO form, but the returned value is reformatted, "
        "so the response date string will differ from the submitted string even "
        "when they denote the same instant. Compare instants, not raw strings."
    ),

    # (a) fidelity. PolicyDto.customer is generated as {"type":"object"} but the service returns a STRING (the customerId); it is an expandable reference (full object only with ?expand=customer).
    # CODE: PolicyDto serializes the customer link as the id unless expanded.
    "components.schemas.PolicyDto.properties.customer": {
        "type": "string",
        "description": (
            "The associated customer's id (a string equal to the policy's customerId), "
            "not a nested object. It is an expandable reference: by default the response "
            "contains the id string; pass the 'expand' query parameter (expand=customer) "
            "to receive a full customer object instead. Read it as policy['customer'], "
            "not policy['customer']['customerId']."
        ),
    },

    # (a)+(c) accuracy. DELETE -> 204 (noContent); the generated default 200 is never produced. Replaces the whole 'responses' object.
    # CODE: PolicyInformationHolder.deletePolicy -> ResponseEntity.noContent().build().
    "paths./policies/{policyId}.delete.responses": {
        "204": {"description": "Policy deleted successfully (no content)."}
    },

    # (e) cross-service provenance + (d) error accuracy. customerId must reference a customer that already exists in customer-core; createPolicy returns 424 (Failed Dependency) otherwise.
    # CODE: createPolicy -> customerCoreRemoteProxy.getCustomersById; empty -> UnknownCustomerException (@ResponseStatus FAILED_DEPENDENCY).
    "components.schemas.CreatePolicyRequestDto.properties.customerId.description": (
        "Identifier of an existing customer that must be created beforehand via the "
        "customer-core Service API; policy creation fails with 424 (Failed Dependency) "
        "if no such customer exists."
    ),

    # (e) asynchronous cross-service precondition. Quote requests are created on customer-self-service and arrive here over the message bus, so a just-submitted request
    # may not exist here yet and the drafting PATCH 404s until it propagates. Draft with
    # status QUOTE_RECEIVED (+ the quote fields) or reject with REQUEST_REJECTED.
    # CODE: policy-management quote-request message consumer;
    #       InsuranceQuoteRequestProcessingResource.respondToInsuranceQuoteRequest.
    "paths./insurance-quote-requests/{id}.patch.description": (
        "Draft a response for an insurance quote request. Quote requests are created on the "
        "customer-self-service backend and arrive at this service asynchronously over the "
        "message bus, so a just-submitted request may not exist here yet: poll GET "
        "/insurance-quote-requests/{id} on this service until it returns 200 before "
        "drafting. Sending status 'QUOTE_RECEIVED' together with expirationDate, "
        "insurancePremium and policyLimit drafts the quote (the resulting QUOTE_RECEIVED "
        "status is propagated back to the self-service backend asynchronously); sending "
        "'REQUEST_REJECTED' rejects the request. The expirationDate must lie in the future "
        "customer's acceptance of it results in QUOTE_EXPIRED instead of a created policy."
    ),

    # (e) precondition on the drafted quote's validity window. A quote whose expirationDate has
    # passed is expired: when the customer accepts it, the back office marks it QUOTE_EXPIRED and
    # emits an expiry event instead of creating a policy (verified: drafting with 2024-01-01 and
    # accepting yields ... QUOTE_ACCEPTED, QUOTE_EXPIRED). A scheduled job expires quotes independently.
    # Omit -> a test drafts with an arbitrary (past) date, accepts, and asserts QUOTE_ACCEPTED is the
    # resulting state -> baseline failure.
    # CODE: CustomerDecisionMessageConsumer: isQuoteAccepted && hasQuoteExpired(decisionDate) ->
    #       markQuoteAsExpired + sendInsuranceQuoteExpiredEvent; else createPolicy + finalizeQuote.
    #       ExpirationCheckerJob (@Scheduled) also expires quotes whose expirationDate has passed.
    "components.schemas.InsuranceQuoteResponseDto.properties.expirationDate.description": (
        "Date until which the drafted quote remains valid. It must lie in the future: a quote "
        "whose expirationDate has already passed is expired, and accepting it leads to the "
        "QUOTE_EXPIRED state rather than to a created policy. Quotes are also expired "
        "automatically once this date passes."
    ),

 
    # (a) fidelity. The drafting status values differ from the self-service accept enum.
    # CODE: respondToInsuranceQuoteRequest matches QUOTE_RECEIVED (draft) / REQUEST_REJECTED (reject).
    "components.schemas.InsuranceQuoteResponseDto.properties.status": {
        "type": "string",
        "enum": ["QUOTE_RECEIVED", "REQUEST_REJECTED"],
        "description": (
            "Back-office decision on the request; must be 'QUOTE_RECEIVED' (draft a quote, "
            "supplying expirationDate, insurancePremium and policyLimit) or 'REQUEST_REJECTED' "
            "(reject the request)."
        ),
    },
 
    # (b)/(d) error completeness. The 404 is reachable and undocumented on PATCH and GET,
    # including for a request that has not yet propagated from the self-service backend.
    # CODE: respondToInsuranceQuoteRequest / getInsuranceQuoteRequest -> InsuranceQuoteRequestNotFoundException (@404).
    "paths./insurance-quote-requests/{id}.patch.responses.404": {
        "description": (
            "No insurance quote request with this id is known to this service (including a "
            "request submitted moments ago that has not yet propagated from the self-service "
            "backend); retry after polling GET until it returns 200."
        )
    },
    "paths./insurance-quote-requests/{id}.get.responses.404": {
        "description": (
            "No insurance quote request with this id is known to this service yet; a "
            "just-submitted request arrives asynchronously, so poll until 200 before acting on it."
        )
    },
}

CUSTOMER_MGMT_PATCHES: Dict[str, Any] = {

    # (e)/(d) VALIDATION PRECONDITION + error order. lastAcknowledgedInteractionId is @NotEmpty and
    # the body is @Valid, so an empty value fails validation and returns 400 BEFORE the not-found
    # check ever runs. springdoc marks the field 'required' (present) but WITHOUT minLength, so a
    # faithful not-found test sent "" (present but empty) and hit 400 instead of 404. Add minLength:1
    # to convey non-empty.
    # CODE: InteractionAcknowledgementDto.lastAcknowledgedInteractionId @NotEmpty;
    #       InteractionLogInformationHolder.acknowledgeInteractions -> findById absent -> InteractionLogNotFoundException(404).
    "components.schemas.InteractionAcknowledgementDto.properties.lastAcknowledgedInteractionId": {
        "type": "string",
        "minLength": 1,
        "description": (
            "Id of the newest acknowledged interaction; required and must be non-empty. "
            "An empty value is rejected with 400 (validation) before any not-found check."
        ),
    },


    # (f) GET/PATCH asymmetry + precondition + error order. GET /interaction-logs/{id}
    # returns an empty log (200) for any id; PATCH (acknowledge) requires an already-persisted log
    # (404 otherwise), but only reaches that check once the body passes validation (empty -> 400).
    # Logs are created only by a customer message (not via REST).
    # CODE: getInteractionLog -> empty log when findById empty; acknowledgeInteractions ->
    #       InteractionLogNotFoundException (404); logs created by CustomerMessageController.
    "paths./interaction-logs/{customerId}.patch.description": (
        "Acknowledge a customer's interactions. The body's lastAcknowledgedInteractionId is "
        "required and must be non-empty; an empty value is rejected with 400 before any "
        "further processing. When the body is valid, the operation requires an interaction "
        "log that already exists for the customer (a log is persisted once the customer has "
        "received interactions) and returns 404 if none exists, even for a requested real "
        "customer that has no logs. Note GET on the same path "
        "instead returns an empty log (200) for a customer with no log yet, so a GET-able "
        "log does not imply this operation will succeed."
    ),


    # (d) error completeness. Make the two error outcomes explicit and distinct so the generator
    # does not conflate them: 400 is the body-validation failure (empty/missing id) and is
    # returned first; 404 is the no-log case, reachable only once the body is valid.
    "paths./interaction-logs/{customerId}.patch.responses.400": {
        "description": (
            "Invalid request body: lastAcknowledgedInteractionId is missing or empty. This "
            "validation failure is returned before any check for an existing interaction log, "
            "so it precedes and is distinct from the 404 no-log case."
        )
    },
    "paths./interaction-logs/{customerId}.patch.responses.404": {
        "description": (
            "No interaction log exists for this customer (reached only when the body is valid, "
            "i.e. a non-empty lastAcknowledgedInteractionId). A customer with no log yet still "
            "returns 200 on GET, so use this operation, not GET, to observe the absence of a log."
        )
    },

}

PATCHES_BY_TITLE_SUBSTR: Dict[str, Dict[str, Any]] = {
    "Customer Core API": CUSTOMER_CORE_PATCHES,
    "Customer Self-Service API": SELF_SERVICE_PATCHES,
    "PolicyManagement API": POLICY_PATCHES,
    "Customer Management API": CUSTOMER_MGMT_PATCHES,
}