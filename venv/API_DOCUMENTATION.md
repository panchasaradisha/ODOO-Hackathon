
---

## Authentication

- **Signup**

  - `POST /signup`
  - **Request Body:**
    ```json
    {
      "email": "user@example.com",
      "password": "password123",
      "name": "John Doe"
    }
    ```
  - **Response:**
    ```
    {
      "message": "User created successfully"
    }
    ```

- **Login**

  - `POST /login`
  - **Request Body:**
    ```json
    {
      "email": "user@example.com",
      "password": "password123"
    }
    ```
  - **Response:**
    ```json
    {
      "access_token": "<JWT_TOKEN>",
      "token_type": "bearer"
    }
    ```

- **Authentication Type:** HTTP Bearer
  - In Swagger UI **Authorize**, paste the `access_token` as the token value.
  - Example:
    ```
    Bearer eyJhbGciOiJIUzI1NiIs...
    ```

---

## User

- **Get Profile**

  - `GET /profile`
  - **Authentication:** Bearer token required
  - **Response:**
    ```json
    {
      "email": "user@example.com",
      "name": "John Doe",
      "points": 0
    }
    ```

---

## Items

- **List All Items**

  - `GET /items`
  - **Response:**
    ```json
    [
      {
        "_id": "...",
        "title": "Blue Jacket",
        "description": "Gently used denim jacket",
        "category": "Outerwear",
        "type": "Swap",
        "size": "M",
        "condition": "Good",
        "tags": ["denim", "blue"],
        "images": ["https://..."],
        "owner_id": "...",
        "status": "available",
        "swap_requests": []
      },
      ...
    ]
    ```

- **Get Single Item**

  - `GET /items/{item_id}`
  - **Response:**
    ```json
    {
      "_id": "...",
      "title": "...",
      "description": "...",
      ...
    }
    ```

- **Create Item**

  - `POST /items`
  - **Authentication:** Bearer token required
  - **Request Body:**
    ```json
    {
      "title": "Blue Jacket",
      "description": "Gently used denim jacket",
      "category": "Outerwear",
      "type": "Swap",
      "size": "M",
      "condition": "Good",
      "tags": ["denim", "blue"],
      "images": ["https://..."]
    }
    ```
  - **Response:**
    ```json
    {
      "message": "Item created",
      "item_id": "..."
    }
    ```

- **Update Item Status**

  - `PATCH /items/{item_id}/status`
  - **Authentication:** Bearer token required
  - **Request Body:**
    ```json
    {
      "status": "swapped"
    }
    ```
  - **Response:**
    ```json
    {
      "message": "Status updated",
      "status": "swapped"
    }
    ```

- **Request Swap**

  - `POST /items/{item_id}/request_swap`
  - **Authentication:** Bearer token required
  - **Response:**
    ```json
    {
      "message": "Swap request submitted"
    }
    ```

- **Redeem Item**

  - `POST /items/{item_id}/redeem`
  - **Authentication:** Bearer token required
  - **Response:**
    ```json
    {
      "message": "Item redeemed successfully",
      "points_deducted": 10
    }
    ```

- **Delete Item (Admin)**

  - `DELETE /admin/items/{item_id}`
  - **Authentication:** Bearer token required
  - *(Note: You can enhance this by adding admin role checks)*
  - **Response:**
    ```json
    {
      "message": "Item deleted successfully"
    }
    ```

---

## Notes

- All endpoints that require authentication **must** include the Bearer token in the `Authorization` header.
- To get a token, login via `/login`.
- Points deduction for redeeming items is currently hard-coded (10 points).
- Item status values can be:
  - `available`
  - `swapped`
  - `redeemed`

---

## Example Usage Flow

1. **Sign up a user**
2. **Log in to get a token**
3. **Authorize in Swagger UI with Bearer token**
4. **Create items**
5. **View items**
6. **Request swaps or redeem items**
7. **Check profile points**

