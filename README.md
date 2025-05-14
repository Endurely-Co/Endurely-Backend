# Fitness & Nutrition API

## Introduction

This API provides functionality for managing fitness routines, nutritional meal plans, and user onboarding. It allows users to create accounts, log in, manage meal plans based on nutritional needs, get meal recommendations, create fitness routines, and find suitable exercises.

## Base URL

http://your-api-domain.com/

# FitFocus API

## Introduction

The FitFocus API provides endpoints for managing user onboarding, meal planning, and fitness routines. It allows developers to create user accounts, manage login and logout, generate meal recommendations, and create/manage fitness routines. The API aims to provide a comprehensive solution for fitness and nutritional tracking.

Key resources include:

*   **Users:** User accounts and authentication.
*   **Meals:** Meal plans, recommendations, and nutritional information.
*   **Routines:** Fitness routine management.

## Base URL

The base URL for all API requests is: `https://api.fittrack.com/` (This is an example, replace if different)

## Authentication

The API utilizes JWT (JSON Web Token) for authentication.

1.  **Obtain Credentials:**
    *   Create a user account via the `/onboarding/create-account` endpoint.
    *   Login via the `/onboarding/login` endpoint to receive an access token and refresh token.

2.  **Include Credentials in Requests:**
    *   Include the access token in the `Authorization` header of each request.
    *   Format: `Authorization: Bearer <access_token>`


## Endpoints

### Create Account

*   URL: `/onboarding/create-account`
*   HTTP Method: POST
*   Request:
    *   Parameters: None
    *   Headers:
        *   `Content-Type`: `application/json`
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
            "username": "example_user",
            "password": "secure_password",
            "email": "user@example.com"
        }
        ```
*   Response:
    *   Status Codes:
        *   201 Created: Account created successfully. Returns the user's information.
        *   400 Bad Request: Invalid request format or data.
    *   Headers: None
    *   Body:
        *   Content Type: `application/json`
        *   Example (Success):
        ```json
        {
            "id": 123,
            "username": "example_user",
            "email": "user@example.com"
        }
        ```
        *   Example (Error):
        ```json
        {
            "error": "Username already exists"
        }
        ```

### Login

*   URL: `/onboarding/login`
*   HTTP Method: POST
*   Request:
    *   Parameters: None
    *   Headers:
        *   `Content-Type`: `application/json`
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
            "username": "example_user",
            "password": "secure_password"
        }
        ```
*   Response:
    *   Status Codes:
        *   200 OK: Login successful. Returns the access token and refresh token.
        *   401 Unauthorized: Invalid credentials.
    *   Headers: None
    *   Body:
        *   Content Type: `application/json`
        *   Example (Success):
```json
       {
    "data": {
        "user_id": 18,
        "username": "test05",
        "first_name": "mario",
        "last_name": "warrio",
        "email": "test04@gmail.com",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3MjQzNzY4LCJpYXQiOjE3NDcyNDM0NjgsImp0aSI6Ijg1YThmNTliY2YxZDRmNDViNGY4NmVhMDcwZDI0OGNmIiwidXNlcl9pZCI6MTh9.hByfdo3-6VAPBlZsLdg180cJ-8wsWLlGIv7UCw77U6I",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NzMyOTg2OCwiaWF0IjoxNzQ3MjQzNDY4LCJqdGkiOiI2Y2ZkOTUxM2JjOGU0NTg3OWM3ZGE3ZTMwNzA1ZTNkMiIsInVzZXJfaWQiOjE4fQ.bs0iHyVdefG_r8-lwPU5DVgqRZBJPDeE6z2IArhlhdc"
    }
}
```
```json
*   Example (Error):
{
    "code": 400,
    "message": "Invalid username or password"
}
```

### Logout

*   URL: `/onboarding/logout`
*   HTTP Method: POST
*   Request:
    *   Parameters: None
    *   Headers:
        *   `Authorization`: is Relaxed
    *   Body: None
*   Response:
    *   Status Codes:
        *   204 No Content: Logout successful.
        *   401 Unauthorized: Invalid or missing access token.
    *   Headers: None
    *   Body: None

### Get Nutrient Information

*   URL: `/meal/nutrient`
*   HTTP Method: GET
*   Request:
    *   Parameters: None
    *   Headers:
        *   `Authorization` is Relaxed
    *   Body: None
*   Response:
    *   Status Codes:
        *   200 OK: Returns nutrient information.
        *   401 Unauthorized: Invalid or missing access token.
    *   Headers: None
    *   Body:
        *   Content Type: `application/json`
        *   Example:
```json
{
    "meal":"water and bread,butter",
    "user": 20
}
```

### Get Meal Plan

*   URL: `/meal/plan/<user_id>` (Get meal plan for a specific user)
*   URL: `/meal/plan` (Create new plan, requires user_id in body)
*   HTTP Method: GET, POST
*   Request (GET):
    *   Parameters:
        *   `user_id`: (Path Parameter) ID of the user. Type: Integer. Required: Yes. Example: 123
    *   Headers:
        *   `Authorization`: is Relaxed
    *   Body: None

*   Request (POST):
    *   Parameters:
    *   Headers:
        *   `Authorization`: is Relaxed
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
        "user_id": 1
        }
        ```
*   Response:
    *   Status Codes:
        *   200 OK: Returns meal plan information.
        *   201 Created: Meal plan created successfully.
        *   401 Unauthorized: Invalid or missing access token.
        *   404 Not Found: Meal plan not found for the user.
    *   Headers: None
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
            "meals": [
                {"name": "Breakfast", "calories": 300},
                {"name": "Lunch", "calories": 500}
            ]
        }
        ```

### Get Meal Recommendations

*   URL: `/meal/recommendations`
*   HTTP Method: GET
*   Request:
    *   Parameters: None
    *   Headers:
        *   `Authorization`: is Relaxed
    *   Body: None
*   Response:
    *   Status Codes:
        *   200 OK: Returns meal recommendations.
        *   401 Unauthorized: Invalid or missing access token.
    *   Headers: None
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
            "recommendations": [
                {"name": "Oatmeal with berries", "calories": 250},
                {"name": "Chicken salad", "calories": 400}
            ]
        }
        ```

### Add Meal Recommendations

*   URL: `/meal/recommendations/new`
*   HTTP Method: POST
*   Request:
    *   Parameters: None
    *   Headers:
        *   `Authorization`: is Relaxed
        *   `Content-Type`: `application/json`
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
            "name": "New Meal",
            "calories": 350,
            "ingredients": ["ingredient1", "ingredient2"]
        }
        ```
*   Response:
    *   Status Codes:
        *   201 Created: Recommendation was created.
        *   401 Unauthorized: Invalid or missing access token.
        *   400 Bad Request: Invalid Request.
    *   Headers: None
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
            "success": true,
            "message": "Recommendation was created"
        }
        ```
### Get Exercises

*   URL: `/routines/exercises`
*   HTTP Method: GET
*   Request:
    *   Parameters: None
    *   Headers:
        *   `Authorization`: is Relaxed
    *   Body: None
*   Response:
    *   Status Codes:
        *   200 OK: Returns a list of available exercises.
        *   401 Unauthorized: Invalid or missing access token.
    *   Headers: None
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        [
            {"name": "Push-ups", "type": "Strength"},
            {"name": "Running", "type": "Cardio"}
        ]
        ```

### Add Fitness Routine

*   URL: `/routines/add`
*   HTTP Method: POST
*   Request:
    *   Parameters: None
    *   Headers:
        *   `Authorization`: is Relaxed
        *   `Content-Type`: `application/json`
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
            "user_id": 1,
            "name": "My Routine",
            "exercises": [
                {"name": "Push-ups", "sets": 3, "reps": 10},
                {"name": "Squats", "sets": 3, "reps": 12}
            ]
        }
        ```
*   Response:
    *   Status Codes:
        *   201 Created: Fitness routine added successfully.
        *   400 Bad Request: Invalid request data.
        *   401 Unauthorized: Invalid or missing access token.
    *   Headers: None
    *   Body:
        *   Content Type: `application/json`
        *   Example:
        ```json
        {
            "success": true,
            "message": "Fitness Routine Created!"
        }
        ```

### Get/Delete User Fitness Routines

*   URL: `/routines/user/<pk>` (Get all routines for user)
*   URL: `/routines/<pk>` (Get or Delete a routine)
*   HTTP Method: GET, DELETE
*   Request(GET - All routines):
    *   Parameters:
        *   `pk`: (Path Parameter) User ID. Type: Integer. Required: Yes. Example: 123
    *   Headers:
        *   `Authorization`: is Relaxed
    *   Body: None
*   Request(GET/DELETE - Specific routine):
    *   Parameters:
        *   `pk`: (Path Parameter) Routine ID. Type: Integer. Required: Yes. Example: 456
    *   Headers:
        *   `Authorization`: is Relaxed
    *   Body: None

*   Response(GET - all routines):
    *   Status Codes:
        *   200 OK: Returns the user's fitness routines.
        *   401 Unauthorized: Invalid or missing access token.

        ```json
            {
                "success": true,
                "data": [
                    {
                        "user_id": 1,
                        "name": "Evening",
                        "exercises": [
                            {
                                "name": "push ups",
                                "sets": 1,
                                "reps": 50
                            }
                        ]
                    }
                ]
            }
        ```

*   Response(DELETE - specific routine):
    *   Status Codes:
        *   204 No Content: Fitness routine successfully deleted.
        *   401 Unauthorized: Invalid or missing access token.
        *   404 Not Found: Fitness routine not found.

        ```json
            {
                "success": true,
                "message": "Routine was deleted."
            }
        ```

## Error Handling

Errors are returned as JSON objects with an `error` field. For example:

```json
{
  "error": "Invalid username or password"
}
```

The API also uses standard HTTP status codes to indicate the type of error.

## Rate Limiting

The API is currently not rate limited. This may be implemented in the future.

## Versioning

The API is currently at version 1.

## Changelog

*   **v1.0** (2023-12-20): Initial release.
```