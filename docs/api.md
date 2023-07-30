# API Documentation

## GET /users

Retrieves a list of all users.

### Parameters

None.

### Responses

`200 OK`

Returns an array of users.

Example:

```json
[
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    },
    {
        "id": 2,
        "name": "Jane Doe",
        "email": "jane@example.com"
    }
]
