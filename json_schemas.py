schema_user = {
    "type" : "object",
    "required" : ["fullName", "email", "phone", "birthDate", "document", "address"],
    "properties" : {
        "id" : {"type" : "string"},
        "fullName" : {"type" : "string", "minLength": 1},
        "email" : {"type" : "string", "minLength": 1},
        "phone" : {"type" : "string", "minLength": 12},
        "birthDate" : {"type" : "string", "minLength": 1},
        "document" : {"type" : "string", "minLength": 11},
        "address" : {"type" : "object", "minProperties": 6}
    }
}

schema_address = {
    "type" : "object",
    "required" : ["street", "neighborhood", "city", "state", "country", "zipcode"],
    "properties" : {
        "street" : {"type" : "string", "minLength": 1},
        "streetNumber" : {"type" : "integer"},
        "complement" : {"type" : "string"},
        "neighborhood" : {"type" : "string", "minLength": 1},
        "city" : {"type" : "string", "minLength": 1},
        "state" : {"type" : "string", "minLength": 1, "maxLength": 2},
        "country" : {"type" : "string", "minLength": 1, "maxLength": 4},
        "zipcode" : {"type" : "string", "minLength": 1}
    }
}