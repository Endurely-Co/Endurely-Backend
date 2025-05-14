## FitnessRoutineView

### Overview

The `FitnessRoutineView` is an API view designed to handle fitness routine operations. It inherits from `AuthenticatedAPIView`, providing authentication for its endpoints. It supports creating, retrieving, updating, and deleting fitness routines.

```python
class FitnessRoutineView(AuthenticatedAPIView):
    ...
```

### Methods

#### get_object

```python
def get_object(self, pk, routine_id=None):
    ...
```

Retrieves `FitnessRoutine` objects based on user ID and optionally a routine ID.

##### Parameters

| Name       | Type   | Description                                  |
|------------|--------|----------------------------------------------|
| `pk`       | `int`  | User ID.                                     |
| `routine_id` | `str, optional` | Routine ID. Defaults to `None`.            |

##### Returns

`QuerySet`: A queryset of `FitnessRoutine` objects.

##### Raises

`Http404`: If no `FitnessRoutine` is found for the given criteria.

#### post

```python
def post(self, request):
    ...
```

Creates a new fitness routine.

##### Parameters

| Name      | Type          | Description                                                                                                                                                                                                                            |
|-----------|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `request` | `HttpRequest` | The HTTP request object. The request data should contain a list of exercises with their IDs and durations. The expected format for exercises is a list of dictionaries, where each dictionary has keys 'id' and 'duration'. |

##### Returns

`Response`: An `api_created_success` response containing the created routine data. The exercises are included in the response.

##### Example Request Body

```json
{
  "exercises": [
    {
      "id": 1,
      "duration": "00:15:00"
    },
    {
      "id": 2,
      "duration": "00:20:00"
    }
  ]
}
```

#### get

```python
def get(self, request, pk=0):
    ...
```

Retrieves fitness routines for a given user, optionally filtered by routine ID.

##### Parameters

| Name      | Type          | Description                                |
|-----------|---------------|--------------------------------------------|
| `request` | `HttpRequest` | The HTTP request object.                   |
| `pk`      | `int`         | User ID.                                   |
| `routine_id`| `str, optional`| Routine ID. Defaults to `None`.           |

##### Query Parameters

*   `routine` (optional): Routine ID to filter results.

##### Returns

`Response`: An `api_success` response containing the serialized routine data.

#### put

```python
@transaction.atomic()
def put(self, request, pk, format=None):
    ...
```

Updates an existing fitness routine. This method uses a transaction to ensure atomicity.

##### Parameters

| Name      | Type          | Description                                                                                                               |
|-----------|---------------|---------------------------------------------------------------------------------------------------------------------------|
| `request` | `HttpRequest` | The HTTP request object. The request data should contain the updated routine information, including exercises and durations. |
| `pk`      | `int`         | The user ID.                                                                                                              |
| `format`  | `str, optional` | The request format. Defaults to `None`.                                                                                  |

##### Request Body Example

```json
{
    "routine_id": "existing_routine_id",
    "exercises": [
        {
            "user_exercise_id": 1,
            "id": 1,
            "duration": "00:20:00",
            "completed": true
        },
        {
            "id": 2,
            "duration": "00:25:00",
            "completed": false
        }
    ],
    "routine_name": "Updated Routine Name",
    "completed": true,
    "meal_date_time": "2024-01-01T12:00:00Z"
}
```

##### Returns

`Response`: An `api_success` response containing the updated routine data.

##### Raises

| Exception                  | Condition                                                                                                              |
|----------------------------|------------------------------------------------------------------------------------------------------------------------|
| `UserExercise.DoesNotExist`| If a `UserExercise` with the given ID does not exist.                                                              |
| `Exercise.DoesNotExist`    | If an `Exercise` with the given ID does not exist.                                                                    |
| `KeyError`                 | If a required key (e.g., 'exercises', 'id', 'duration') is missing from the request data.                               |

#### delete

```python
def delete(self, request, pk):
    ...
```

Deletes a fitness routine.

##### Parameters

| Name      | Type          | Description              |
|-----------|---------------|--------------------------|
| `request` | `HttpRequest` | The HTTP request object. |
| `pk`      | `int`         | The user ID.             |

##### Query Parameters

*   `routine` (required): Routine ID to delete.

##### Returns

`Response`: An `api_success` response indicating the routine was deleted.

# `MealRecommendationView`

This view is deprecated and should not be used. It was intended to retrieve and create `MealInfo` objects.

```python
class MealRecommendationView(AuthenticatedAPIView):
    ...

    def get(self, _):
        ...

    def post(self, request, *args, **kwargs):
        ...
```

## `get` Method

Retrieves all `MealInfo` objects.

**Returns:**

*   `api_success`: A list of serialized `MealInfo` objects if successful.
*   `api_error`: An error message if an exception occurs.

## `post` Method

Creates a new `MealInfo` object.

**Parameters:**

| Name      | Type                       | Description                                               |
| ----------- | -------------------------- | --------------------------------------------------------- |
| `request` | `The HTTP request object` | The HTTP request object containing the `MealInfo` data. |

**Returns:**

*   `api_created_success`: The serialized `MealInfo` object if creation is successful.
*   `api_error`: An error message if the data is invalid.

---

# `MealPlanView`

This view handles operations related to `MealPlan` objects, including retrieving, deleting, and creating meal plans.

```python
class MealPlanView(AuthenticatedAPIView):
    ...

    def get(self, request, user_id):
        ...

    def delete(self, request, user_id):
        ...

    def post(self, request, *args, **kwargs):
        ...
```

## `get` Method

Retrieves `MealPlan` objects for a specific user.

**Parameters:**

| Name        | Type                       | Description                                                       |
| ----------- | -------------------------- | ----------------------------------------------------------------- |
| `request`   | `The HTTP request object` | The HTTP request object.                                          |
| `user_id` | `int`                      | The ID of the user whose meal plans are to be retrieved.         |

**Returns:**

*   `api_success`: A list of serialized `MealPlan` objects with associated food item nutrients.

## `delete` Method

Deletes a specific `MealPlan` object for a user.

**Parameters:**

| Name      | Type                       | Description                                                       |
| ----------- | -------------------------- | ----------------------------------------------------------------- |
| `request`   | `The HTTP request object` | The HTTP request object.                                          |
| `user_id` | `int`                      | The ID of the user whose meal plan is to be deleted.         |

**Returns:**

*   `api_success`: A success message if the meal plan is deleted.
*   `api_error`: An error message if the `plan_id` is missing or an exception occurs.

## `post` Method

Creates `MealPlan` objects for a user.

**Parameters:**

| Name      | Type                       | Description                                                       |
| ----------- | -------------------------- | ----------------------------------------------------------------- |
| `request`   | `The HTTP request object` | The HTTP request object containing meal plan data.           |

**Returns:**

*   `api_created_success`: A success message if meal plans are created successfully.
*   `api_error`: An error message if there are issues with the input data, user, or food item.

---

# `NutrientView`

This view handles operations related to retrieving nutrient information and fetching nutrient data for food items using Gemini API.

```python
class NutrientView(AuthenticatedAPIView):
    ...

    def __init__(self, **kwargs):
        ...

    def get(self, _, user_id):
        ...

    def post(self, request):
        ...
```

## `__init__` Method

Initializes the `NutrientView` with a `GeminiApi` instance.

## `get` Method

Retrieves meal plan data with associated nutrient information for a user.

**Parameters:**

| Name      | Type                       | Description                                                       |
| ----------- | -------------------------- | ----------------------------------------------------------------- |
| `_`   | `The HTTP request object` | The HTTP request object (not used).                                          |
| `user_id` | `int`                      | The ID of the user.         |

**Returns:**

*   `api_success`: Meal plan data with `other_nutrients` from the associated food items.

## `post` Method

Retrieves nutrient information for given food items, either from the database or using the Gemini API. Creates `FoodItem` objects if they don't exist in the database.

**Parameters:**

| Name      | Type                       | Description                                                       |
| ----------- | -------------------------- | ----------------------------------------------------------------- |
| `request`   | `The HTTP request object` | The HTTP request object containing the user ID and meal (food items).                                          |

**Returns:**

*   `api_created_success`: Nutrient information for the food items.
*   `api_error`: An error message if input is invalid or an issue occurs during processing.

# Account Management API Documentation

This document provides detailed information about the account management API endpoints, including user creation, login, and logout.

## 1. CreateAccountView

### 1.1. Overview

`CreateAccountView` is an API view designed to handle the creation of new user accounts. It validates user input, including email, username, first name, last name, and password, before creating a new user in the database.  It inherits from `generics.CreateAPIView`.

### 1.2. Code

```python
class CreateAccountView(generics.CreateAPIView):
    ...
```

### 1.3. Attributes

*   `serializer_class`:  Specifies the serializer class used for validating and deserializing input data. In this case, it's `CreateUserSerializer`.

### 1.4. HTTP POST

#### 1.4.1. Purpose

Handles the POST request to create a new user account.

#### 1.4.2. Parameters

*   `request` (Request): The request object containing user data.

    The request body should be a JSON object with the following fields:

    | Field        | Type   | Description                               |
    |--------------|--------|-------------------------------------------|
    | `username`   | string | The desired username for the new account. |
    | `password`   | string | The password for the new account.         |
    | `email`      | string | The email address for the new account.    |
    | `first_name` | string | The first name of the user.               |
    | `last_name`  | string | The last name of the user.                |

#### 1.4.3. Returns

*   `Response`: A JSON response indicating success or failure.

    *   **Success (201 Created):** Returns a JSON object containing the user's details:

        ```json
        {
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "acct_type": 0
        }
        ```

    *   **Error (400 Bad Request):** Returns a JSON object with an error message if validation fails or if any required fields are missing.  Possible error messages include:

        *   `"Invalid request type"`: If the request data is not a dictionary.
        *   `"Invalid email or username"`: If the email or username format is invalid.
        *   `"Username already exist. Please try again"`: If the username is already taken.
        *   `"{field_name} is missing"`: If a required field is missing in the request.
        *   Error messages from custom exceptions like `WeakPasswordError` or `InvalidNameException`.

#### 1.4.4. Exceptions

*   `IntegrityError`: Raised if the username already exists in the database.
*   `KeyError`: Raised if a required field (e.g., email, username, password) is missing from the request data.
*   `WeakPasswordError`: Raised if the provided password does not meet the required complexity criteria.
*   `InvalidNameException`: Raised if the first or last name contains invalid characters or does not meet the required format.
*   `TypeError`: Raised if there is a type mismatch during data validation or processing.

#### 1.4.5. Usage Example

```python
import requests
import json

url = "your_api_endpoint/create/"
payload = json.dumps({
    "username": "testuser",
    "password": "StrongPassword123!",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

## 2. get_tokens_for_user

### 2.1. Overview

`get_tokens_for_user` generates JSON Web Tokens (JWTs), specifically refresh and access tokens, for a given user. These tokens are used for authentication and authorization.

### 2.2. Code

```python
def get_tokens_for_user(user):
    ...
```

### 2.3. Parameters

*   `user` (User): The user object for whom to generate tokens.  This should be an instance of Django's `User` model.

### 2.4. Returns

*   `dict`: A dictionary containing the refresh and access tokens.

    ```json
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4ODczMzEwNywiaWF0IjoxNjg4NjQ2NzA3LCJqdGkiOiI4ZDQ3MjM4MzQ1NjU0OTlhYThkOTk5ZTg4MzkyYzYyZiIsInVzZXJfaWQiOjF9.Y0o8Z3U3RjJvWk41bXJKMkV5bXN4V09xNTRRV256aWl0bG9wclZOWQ",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg4NjQ3MzA3LCJpYXQiOjE2ODg2NDY3MDcsImp0aSI6ImU4YjM0NjlkMmZlODQ0NmM5ZjI1ZmUyZTcxMmRmMTU2IiwidXNlcl9pZCI6MX0.L2t789a7T98IU-vhZlS5f44czQ_1lRjW9_v53FBl_as"
    }
    ```

    *   `refresh`: The refresh token, used to obtain new access tokens when the current access token expires.
    *   `access`: The access token, used to authenticate requests to protected resources.

### 2.5. Usage Example

```python
from django.contrib.auth.models import User

user = User.objects.get(username='testuser')  # Assuming a user exists
tokens = get_tokens_for_user(user)
print(tokens)
```

## 3. LoginView

### 3.1. Overview

`LoginView` is an API view that handles user login and generates JWT tokens upon successful authentication. It authenticates users based on their username and password. It inherits from `APIView`.

### 3.2. Code

```python
class LoginView(APIView):
    ...
```

### 3.3. HTTP POST

#### 3.3.1. Purpose

Handles the POST request for user login.

#### 3.3.2. Parameters

*   `request` (Request): The request object containing username and password.

    The request body should be a JSON object with the following fields:

    | Field      | Type   | Description                |
    |------------|--------|----------------------------|
    | `username` | string | The user's username.       |
    | `password` | string | The user's password.       |

#### 3.3.3. Returns

*   `Response`: A JSON response containing user details and tokens upon successful login, or an error message upon failure.

    *   **Success (201 Created):** Returns a JSON object containing the user's details and tokens:

        ```json
        {
            "user_id": 1,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
        ```

    *   **Error (400 Bad Request):** Returns a JSON object with an error message if authentication fails or if username/password are missing.  Possible error messages include:

        *   `"Username and password are required"`: If either username or password is not provided.
        *   `"Invalid username or password"`: If the provided credentials are incorrect.

#### 3.3.4. Usage Example

```python
import requests
import json

url = "your_api_endpoint/login/"
payload = json.dumps({
    "username": "testuser",
    "password": "StrongPassword123!"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

## 4. Logout

### 4.1. Overview

`Logout` is an API view designed to handle user logout.  It invalidates the user's session. It inherits from `APIView`.

### 4.2. Code

```python
class Logout(APIView):
    ...
```

### 4.3. HTTP GET

#### 4.3.1. Purpose

Handles the GET request for user logout.

#### 4.3.2. Parameters

*   `request` (Request): The request object.

#### 4.3.3. Returns

*   `Response`: A 200 OK response indicating successful logout.  The response body is empty.

#### 4.3.4. Usage Example

```python
import requests

url = "your_api_endpoint/logout/"
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers)

print(response.status_code)  # Should print 200
```
