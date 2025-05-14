```markdown
# FitnessRoutineView Documentation

This document provides detailed information about the `FitnessRoutineView` API view, which handles fitness routine operations, including creation, retrieval, update, and deletion.

## Overview

The `FitnessRoutineView` class is a Django REST Framework API view designed to manage fitness routines associated with users. It provides endpoints for creating new routines, retrieving existing routines (either all routines for a user or a specific routine by ID), updating routines, and deleting routines. The view uses serializers to handle data validation and serialization, ensuring data consistency and proper formatting for API responses.

## Code Snippet

```python
class FitnessRoutineView(AuthenticatedAPIView):
    def get_object(self, pk, routine_id=None):
        try:
            fitness_routine = FitnessRoutine.objects.filter(user=pk)
            return fitness_routine.filter(routine_id=routine_id) if routine_id else fitness_routine
        except FitnessRoutine.DoesNotExist:
            raise Http404

    def post(self, request):
        try:
            exercises_data = request.data.get('exercises', [])
            request.data['routine_id'] = uuid.uuid4().hex

            if not exercises_data:
                return api_error("No exercises provided")

            exercise_ids = [exercise_obj['id'] for exercise_obj in exercises_data]
            exercise_map = {exercise.id: exercise for exercise in Exercise.objects.filter(id__in=exercise_ids)}
            exercises = []

            with transaction.atomic():
                for exercise_obj in exercises_data:
                    exercise = exercise_map.get(exercise_obj['id'])
                    if not exercise:
                        return api_error(f"Exercise with ID {exercise_obj['id']} not found")

                    hours, minutes, seconds = map(int, exercise_obj['duration'].split(":"))
                    user_exercise = UserExercise.objects.create(
                        exercise=exercise,
                        duration=timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    )

                    request.data['exercise'] = user_exercise.id
                    routine_serializer = FitnessRoutineSerializer(data=request.data)

                    if routine_serializer.is_valid():
                        routine_serializer.save()
                        user_exercise_serializer = UserExerciseSerializer(user_exercise).data
                        user_exercise_serializer['exercise'] = GetExercisesSerializer(exercise).data
                        exercises.append(user_exercise_serializer)
                    else:
                        return api_error(routine_serializer.errors)

            request.data.pop('exercise')
            request.data['exercises'] = exercises

            return api_created_success(request.data)
        except (ValidationError, Http404) as e:
            return api_error('Internal server error')

    def get(self, request, pk=0):
        routine_param = request.query_params.get('routine')
        routine_id = routine_param if routine_param else None

        if type(pk) is not int:
            return api_error(f"{pk} not a valid type")

        if pk <= 0:
            return api_error("invalid user id")

        routines = self.get_object(pk=pk, routine_id=routine_id)

        serializer_data = FitnessRoutineSerializer(routines, many=True).data

        in_response = {}
        distinct_exercises = {}

        exercise_ids = {serializer['exercise'] for serializer in serializer_data}
        user_exercises = {ue.pk: ue for ue in UserExercise.objects.filter(pk__in=exercise_ids)}
        exercise_map = {e.id: e for e in
                        Exercise.objects.filter(id__in=[ue.exercise.id for ue in user_exercises.values()])}

        for serializer in serializer_data:
            user_exercise = user_exercises.get(serializer['exercise'])

            if not user_exercise:
                continue

            exercises = [exercise_map.get(user_exercise.exercise.id)]
            exercises_serializer = GetExercisesSerializer(exercises, many=True).data

            user_exercises_serializer = UserExerciseSerializer(user_exercise).data
            user_exercises_serializer['exercise'] = exercises_serializer[0]

            routine_id = serializer['routine_id']

            if routine_id in distinct_exercises:
                distinct_exercises[routine_id].append(user_exercises_serializer)
            else:
                distinct_exercises[routine_id] = [user_exercises_serializer]
                serializer['exercises'] = distinct_exercises[routine_id]
                in_response[routine_id] = serializer

            serializer.pop('exercise')

        return api_success(in_response.values())

    @transaction.atomic()
    def put(self, request, pk, format=None):
        try:
            exercise_list, existing_routine_data = [], {}

            exercises = request.data['exercises']

            existing_routine = None
            del_routine = FitnessRoutine.objects.filter(user=pk) \
                .filter(routine_id=request.data['routine_id'])

            if not del_routine.exists():
                return api_error("Record does not exist")

            mod_routine = del_routine[0]
            del_routine.delete()

            for exercise in exercises:
                ex_key = exercise.get('user_exercise_id')
                exercise_obj = Exercise.objects.get(id=exercise['id'])
                hours, minutes, seconds = map(int, exercise['duration'].split(":"))
                user_exercise, created = UserExercise.objects.update_or_create(
                    id=exercise.get('user_exercise_id'),
                    defaults={"duration": timedelta(minutes=minutes, seconds=seconds, hours=hours),
                              "exercise": exercise_obj, "completed": exercise["completed"]}
                )

                existing_routine, created = FitnessRoutine.objects.update_or_create(
                    user=mod_routine.user,
                    exercise=user_exercise,
                    defaults={
                        "start_date": request.data.get("meal_date_time"),
                        "routine_name": check_none(request.data.get("routine_name"), mod_routine.routine_name),
                        "routine_id": mod_routine.routine_id,
                        "completed": check_none(request.data.get("completed"), mod_routine.completed),
                    }
                )

                exercise_list.append(UserExerciseSerializer(user_exercise).data)

            existing_routine_data = FitnessRoutineSerializer(existing_routine).data
            existing_routine_data['exercises'] = exercise_list
            return api_success(existing_routine_data)
        except (UserExercise.DoesNotExist, Exercise.DoesNotExist, KeyError) as e:
            return api_error(f"{e}")

    def delete(self, request, pk):
        routine_param = request.query_params.get('routine')
        if type(routine_param) is not str:
            return api_error(f"{routine_param} not a valid type")
        snippet = self.get_object(pk, routine_param)

        if len(snippet) <= 0:
            return api_success(f"No routine matching this id: {routine_param}")
        snippet.delete()
        return api_success("Routine was deleted.")
```

## `get_object(self, pk, routine_id=None)`

Retrieves `FitnessRoutine` objects based on user ID and optionally a routine ID.

### Parameters

| Parameter  | Data Type | Description                                                 |
| :--------- | :-------- | :---------------------------------------------------------- |
| `pk`       | `int`     | User ID.                                                    |
| `routine_id` | `str`, optional | Routine ID. Defaults to `None`.                               |

### Returns

`QuerySet`: A queryset of `FitnessRoutine` objects.

### Raises

`Http404`: If no `FitnessRoutine` is found for the given criteria.

## `post(self, request)`

Creates a new fitness routine.

### Parameters

*   `request` (`HttpRequest`): The HTTP request object.  The request data should contain a list of exercises with their IDs and durations. The expected format is a JSON object with an 'exercises' key, where the value is a list of exercise objects. Each exercise object must contain 'id' (exercise id) and 'duration' (exercise duration in HH:MM:SS format).

    ```json
    {
      "exercises": [
        {
          "id": 1,
          "duration": "00:30:00"
        },
        {
          "id": 2,
          "duration": "00:15:00"
        }
      ]
    }
    ```

### Returns

`Response`: An `api_created_success` response containing the created routine data. The response includes the generated `routine_id` and a list of exercises with their details.

### Raises

*   `ValidationError`: If the input data is invalid according to the serializer.
*   `Http404`: If an exercise ID provided in the request data does not exist.

### Usage Example

```python
# Example request data
request_data = {
    "exercises": [
        {"id": 1, "duration": "00:30:00"},
        {"id": 2, "duration": "00:15:00"}
    ]
}

# Assuming the request object is properly set up
response = FitnessRoutineView().post(request)

# Expected successful response
# {
#     "status": "success",
#     "message": "Created Successfully",
#     "data": {
#         "routine_id": "unique_routine_id",
#         "exercises": [
#             {
#                 "id": 1,
#                 "duration": "00:30:00",
#                 "exercise": {
#                     "id": 1,
#                     "name": "Example Exercise 1",
#                     "category": "Strength"
#                 }
#             },
#             {
#                 "id": 2,
#                 "duration": "00:15:00",
#                 "exercise": {
#                     "id": 2,
#                     "name": "Example Exercise 2",
#                     "category": "Cardio"
#                 }
#             }
#         ]
#     }
# }
```

## `get(self, request, pk=0)`

Retrieves fitness routines for a given user, optionally filtered by routine ID.

### Parameters

*   `request` (`HttpRequest`): The HTTP request object.
*   `pk` (`int`): User ID.
*   `routine_id` (`str`, optional): Routine ID. Defaults to `None`.  If provided, only the routine with this ID will be returned. The `routine_id` can be passed as a query parameter named `routine`.

### Returns

`Response`: An `api_success` response containing the serialized routine data. The response is a list of dictionaries, each representing a fitness routine. Each routine dictionary contains the routine details along with a list of exercises included in the routine. Each exercise object contains the exercise details such as name, category, and duration.

### Raises

None.

### Usage Example

```python
# Retrieving all routines for user ID 1
response = FitnessRoutineView().get(request, pk=1)

# Retrieving a specific routine with ID "some_routine_id" for user ID 1
request.query_params = {'routine': 'some_routine_id'}  # Simulate query parameter
response = FitnessRoutineView().get(request, pk=1)

# Expected successful response (example - simplified)
# {
#     "status": "success",
#     "message": "OK",
#     "data": [
#         {
#             "routine_id": "some_routine_id",
#             "routine_name": "My Routine",
#             "exercises": [
#                 {
#                     "id": 1,
#                     "duration": "00:30:00",
#                     "exercise": {
#                         "id": 1,
#                         "name": "Example Exercise 1",
#                         "category": "Strength"
#                     }
#                 },
#                 {
#                     "id": 2,
#                     "duration": "00:15:00",
#                     "exercise": {
#                         "id": 2,
#                         "name": "Example Exercise 2",
#                         "category": "Cardio"
#                     }
#                 }
#             ]
#         }
#     ]
# }
```

## `put(self, request, pk, format=None)`

Updates an existing fitness routine.

### Parameters

*   `request` (`HttpRequest`): The HTTP request object. The request data should contain the updated routine information, including exercises and their durations.
*   `pk` (`int`): The user ID.
*   `format` (`str`, optional): The request format. Defaults to `None`.

### Returns

`Response`: An `api_success` response containing the updated routine data.

### Raises

*   `UserExercise.DoesNotExist`: If a `UserExercise` with the given ID does not exist.
*   `Exercise.DoesNotExist`: If an `Exercise` with the given ID does not exist.
*   `KeyError`: If a required key is missing from the request data.

### Usage Example

```python
# Example request data
request_data = {
    "routine_id": "existing_routine_id",
    "exercises": [
        {"user_exercise_id": 1, "id": 1, "duration": "00:35:00", "completed": True},
        {"user_exercise_id": 2, "id": 2, "duration": "00:20:00", "completed": False}
    ],
    "routine_name": "Updated Routine Name"
}

# Assuming the request object is properly set up and pk is the user ID
response = FitnessRoutineView().put(request, pk=1)

# Expected successful response (example - simplified)
# {
#     "status": "success",
#     "message": "OK",
#     "data": {
#         "routine_id": "existing_routine_id",
#         "routine_name": "Updated Routine Name",
#         "exercises": [
#             {
#                 "id": 1,
#                 "duration": "00:35:00",
#                 "exercise": {
#                     "id": 1,
#                     "name": "Example Exercise 1",
#                     "category": "Strength"
#                 }
#             },
#             {
#                 "id": 2,
#                 "duration": "00:20:00",
#                 "exercise": {
#                     "id": 2,
#                     "name": "Example Exercise 2",
#                     "category": "Cardio"
#                 }
#             }
#         ]
#     }
# }
```

## `delete(self, request, pk)`

Deletes a fitness routine.

### Parameters

*   `request` (`HttpRequest`): The HTTP request object.
*   `pk` (`int`): The user ID.  The routine to be deleted is identified by a 'routine' query parameter.

### Returns

`Response`: An `api_success` response indicating the routine was deleted.

### Raises

None.

### Usage Example

```python
# Deleting a routine with ID "some_routine_id" for user ID 1
request.query_params = {'routine': 'some_routine_id'}  # Simulate query parameter
response = FitnessRoutineView().delete(request, pk=1)

# Expected successful response
# {
#     "status": "success",
#     "message": "Routine was deleted.",
#     "data": null
# }
```
```markdown
# Meal Views Documentation

This document provides detailed information about the different API views related to meal planning and nutrient information. These views allow users to retrieve meal plans, delete meal plans, create meal plans and get nutrient information about food.

## 1. `MealPlanView`

This view handles operations related to `MealPlan` objects, including retrieving, deleting, and creating meal plans for a specific user.

### Description

The `MealPlanView` class provides the following functionalities:

-   **GET**: Retrieves `MealPlan` objects for a specific user, optionally filtered by a `plan_id`.
-   **DELETE**: Deletes a specific `MealPlan` object for a user, identified by `plan_id`.
-   **POST**: Creates `MealPlan` objects for a user based on the provided data.

### Code

```python
class MealPlanView(AuthenticatedAPIView):
    """
    This view handles operations related to MealPlan objects,
    including retrieving, deleting, and creating meal plans.
    """

    def get(self, request, user_id):
        """
        Retrieves MealPlan objects for a specific user.

        Args:
            request: The HTTP request object.
            user_id: The ID of the user whose meal plans are to be retrieved.

        Returns:
            api_success: A list of serialized MealPlan objects with associated food item nutrients.
        """
        meal_plan_id = request.query_params.get('plan_id')
        meal_plan = MealPlan.objects.filter(user=user_id)
        if meal_plan_id:
            meal_plan = meal_plan.filter(meal_plan_id=meal_plan_id)
        meal_plan_data = MealPlanSerializer(meal_plan, many=True).data
        for i in range(len(meal_plan)):
            serialized_food = FoodItemSerializer(meal_plan[i].food_item).data
            if meal_plan_id:
                meal_plan_data[i]["nutrients"] = serialized_food
            else:
                meal_plan_data[i]['other_nutrients'] = serialized_food['other_nutrients']
            # print("food_item", )
        return api_success(meal_plan_data)

    def delete(self, request, user_id):
        """
        Deletes a specific MealPlan object for a user.

        Args:
            request: The HTTP request object.
            user_id: The ID of the user whose meal plan is to be deleted.

        Returns:
            api_success: A success message if the meal plan is deleted.
            api_error: An error message if the plan_id is missing or an exception occurs.
        """
        meal_to_delete = request.query_params.get('plan_id')
        if meal_to_delete:
            try:
                meal_plan = MealPlan.objects.filter(meal_plan_id=meal_to_delete, user=user_id)
                meal_plan.delete()
                return api_success("Meal plan successfully deleted")
            except Exception as err:
                return api_error('Invalid server error')
        return api_error("plan_id is required")

    def post(self, request, *args, **kwargs):
        """
        Creates MealPlan objects for a user.

        Args:
            request: The HTTP request object containing meal plan data.

        Returns:
            api_created_success: A success message if meal plans are created successfully.
            api_error: An error message if there are issues with the input data, user, or food item.
        """
        meal_plans = request.data.get('meal_plans')
        if not meal_plans:
            return api_error("meal_plans is absent")

        if type(meal_plans) is not list:
            return api_error("meal_plans is not valid. Expected: list of meal plans")

        if len(meal_plans) > 4:
            return api_error("meal_plans too many meal plans")
        plan_id = "".join(sorted([str(mp['food_item_id']) for mp in meal_plans]))

        try:
            user = User.objects.get(pk=request.data['user'])
        except User.DoesNotExist:
            return api_error("User does not exist")

        success_msg = []
        with transaction.atomic():
            for plan in meal_plans:
                try:
                    food_item = FoodItem.objects.get(pk=plan['food_item_id'])
                except FoodItem.DoesNotExist:
                    return api_error("food item doesn't exist")

                created = True
                try:
                    meal_plan = MealPlan.objects.get(meal_plan_id=plan['food_item_id'], user=user)
                except MealPlan.DoesNotExist:
                    meal_plan, created = update_or_create_meal_plan(plan_id, user, request.data['meal_date_time'], food_item)

        if created:
            return api_created_success({"message": "Meal plan added successfully"})
        return api_error("Meal plan was not added. Please try again later")
```

### 1.1 `GET` Method

#### Description

Retrieves `MealPlan` objects associated with a specific user. It can also filter the meal plans by a `plan_id` provided as a query parameter. The method returns a list of serialized `MealPlan` objects including nutrients from the associated food items.

#### Parameters

| Name      | Type    | Description                                                 |
| ----------- | ------- | ----------------------------------------------------------- |
| `request` | `HTTPRequest` | The HTTP request object.                                  |
| `user_id`   | `int`   | The ID of the user whose meal plans are to be retrieved. |

#### Query Parameters

| Name      | Type    | Description                                                 |
| ----------- | ------- | ----------------------------------------------------------- |
| `plan_id` | `string`   | (Optional) The ID of the specific meal plan to retrieve. |

#### Returns

-   `api_success`: A list of serialized `MealPlan` objects with associated food item nutrients.

#### Example Usage

```python
# Example of retrieving all meal plans for user with ID 1
GET /meal/plan/1/
```

```python
# Example of retrieving a specific meal plan (plan_id=123) for user with ID 1
GET /meal/plan/1/?plan_id=123
```

### 1.2 `DELETE` Method

#### Description

Deletes a specific `MealPlan` object for a user, identified by the `plan_id` query parameter.

#### Parameters

| Name      | Type    | Description                                                 |
| ----------- | ------- | ----------------------------------------------------------- |
| `request` | `HTTPRequest` | The HTTP request object.                                  |
| `user_id`   | `int`   | The ID of the user whose meal plan is to be deleted.       |

#### Query Parameters

| Name      | Type    | Description                                                 |
| ----------- | ------- | ----------------------------------------------------------- |
| `plan_id` | `string`   | The ID of the meal plan to delete. |

#### Returns

-   `api_success`: A success message if the meal plan is deleted.
-   `api_error`: An error message if the `plan_id` is missing or an exception occurs.

#### Example Usage

```python
# Example of deleting meal plan with ID 123 for user with ID 1
DELETE /meal/plan/1/?plan_id=123
```

### 1.3 `POST` Method

#### Description

Creates `MealPlan` objects for a user based on the provided data in the request body. Expects a list of `meal_plans` in the request data.

#### Parameters

| Name      | Type    | Description                                                |
| ----------- | ------- | ---------------------------------------------------------- |
| `request` | `HTTPRequest` | The HTTP request object containing meal plan data. |

#### Request Body

The request body should contain a JSON object with the following structure:

```json
{
    "user": 1,
    "meal_date_time": "2024-01-01T12:00:00Z",
    "meal_plans": [
        {
            "food_item_id": 1
        },
        {
            "food_item_id": 2
        }
    ]
}
```

#### Returns

-   `api_created_success`: A success message if meal plans are created successfully.
-   `api_error`: An error message if there are issues with the input data, user, or food item.

#### Example Usage

```python
# Example of creating meal plans for user with ID 1
POST /meal/plan/1/
```

Request body:

```json
{
    "user": 1,
    "meal_date_time": "2024-01-01T12:00:00Z",
    "meal_plans": [
        {
            "food_item_id": 1
        },
        {
            "food_item_id": 2
        }
    ]
}
```

## 2. `NutrientView`

This view handles operations related to retrieving nutrient information for food items, either from the database or using the Gemini API.

### Description

The `NutrientView` class provides the following functionalities:

-   **GET**: Retrieves meal plan data with associated nutrient information for a user.
-   **POST**: Retrieves nutrient information for given food items, either from the database or using the Gemini API.  Creates `FoodItem` objects if they don't exist in the database.

### Code

```python
class NutrientView(AuthenticatedAPIView):
    """
    This view handles operations related to retrieving nutrient information
    and fetching nutrient data for food items using Gemini API.
    """

    def __init__(self, **kwargs):
        """
        Initializes the NutrientView with a GeminiApi instance.
        """
        super().__init__(**kwargs)
        self.gemini = GeminiApi()

    def get(self, _, user_id):
        """
        Retrieves meal plan data with associated nutrient information for a user.

        Args:
            _: The HTTP request object (not used).
            user_id: The ID of the user.

        Returns:
            api_success: Meal plan data with 'other_nutrients' from the associated food items.
        """
        meal_plan = MealPlan.objects.filter(user=user_id)
        meal_plan_data = MealPlanSerializer(meal_plan, many=True).data
        for i in range(len(meal_plan)):
            serialized_food = FoodItemSerializer(meal_plan[i].food_item).data
            meal_plan_data[i]['other_nutrients'] = serialized_food['other_nutrients']
            # meal_plan_data[i]["nutrients"] = serialized_food
            # print("food_item", )
        return api_success(meal_plan_data)

    def post(self, request):
        """
        Retrieves nutrient information for given food items, either from the database
        or using the Gemini API.  Creates FoodItem objects if they don't exist in the database.

        Args:
            request: The HTTP request object containing the user ID and meal (food items).

        Returns:
            api_created_success:  Nutrient information for the food items.
            api_error: An error message if input is invalid or an issue occurs during processing.
        """
        if not request.data.get('meal') or not request.data.get('user'):
            return api_error("user and meal are required")

        foods = request.data.get('meal').lower().strip()

        if not foods or len(foods) <= 2:
            return api_error("Food/drink is invalid. Try again!")

        food_items = [item for item in foods.split(',')]

        if len(food_items) > 2:
            return api_error("Maximum of two food/drink is allowed!")

        try:
            user = User.objects.get(pk=request.data.get('user'))
            response_obj = {
                "user": user.id
            }
        except User.DoesNotExist:
            return api_error("User does not exist")

        # Look in the db
        food_item_query = FoodItem.objects.filter(item=food_items[0]) if len(food_items) < 2 \
            else FoodItem.objects.filter(item__in=[food_items[0], food_items[1]])
        food_exist = food_item_query.exists()
        if food_exist:
            if len(food_item_query) >= len(food_items):
                response_obj["nutrients"] = FoodItemSerializer(food_item_query, many=True).data
                return api_created_success(response_obj)
            else:
                for food in food_items:
                    if food not in [f.item for f in food_item_query]:
                        foods = food

        # Get results from gemini API
        gemini_results = self.gemini.nutrients_from_food(foods)['results']

        food_objects = []

        for result in gemini_results:
            if result.get('error'):
                return api_error(result['error'])

            nutrients = result['nutrients']
            food_obj = FoodItem(
                item=result['item'],
                valid=result['valid'],
                macronutrients=nutrients.get('macronutrients', []),
                vitamins=nutrients.get('vitamins', []),
                minerals=nutrients.get('minerals', []),
                other_nutrients=nutrients.get('other_nutrients', ''),
            )
            food_objects.append(food_obj)
        with transaction.atomic():
            # Bulk insert all food items
            created_foods = FoodItem.objects.bulk_create(food_objects)

        if food_exist:
            # We have one existing food in the db
            created_foods.extend(food_item_query)

        response_obj["nutrients"] = FoodItemSerializer(created_foods, many=True).data
        return api_created_success(response_obj)
```

### 2.1 `GET` Method

#### Description

Retrieves meal plan data with associated nutrient information for a specific user. This method returns meal plan data along with the `other_nutrients` field from the associated food items.

#### Parameters

| Name      | Type    | Description                                  |
| ----------- | ------- | -------------------------------------------- |
| `_`       | `HTTPRequest` | The HTTP request object (not used).          |
| `user_id`   | `int`   | The ID of the user to retrieve meal plans for. |

#### Returns

-   `api_success`: Meal plan data with `other_nutrients` from the associated food items.

#### Example Usage

```python
# Example of retrieving meal plan data for user with ID 1
GET /meal/nutrient/1/
```

### 2.2 `POST` Method

#### Description

Retrieves nutrient information for given food items. It first checks the database for existing `FoodItem` objects. If the food item is not found, it uses the Gemini API to fetch nutrient data and creates new `FoodItem` objects.

#### Parameters

| Name      | Type    | Description                                                 |
| ----------- | ------- | ----------------------------------------------------------- |
| `request` | `HTTPRequest` | The HTTP request object containing the user ID and meal (food items). |

#### Request Body

The request body should contain a JSON object with the following structure:

```json
{
    "user": 1,
    "meal": "apple, banana"
}
```

#### Returns

-   `api_created_success`:  Nutrient information for the food items.
-   `api_error`: An error message if input is invalid or an issue occurs during processing.

#### Example Usage

```python
# Example of retrieving nutrient information for "apple" and "banana" for user with ID 1
POST /meal/nutrient/
```

Request body:

```json
{
    "user": 1,
    "meal": "apple, banana"
}
```
```markdown
# User Authentication and Account Management API

This document describes the API endpoints for user account creation, login, and logout.  It details the functionality of each view, their parameters, return values, and potential exceptions.

## 1. Create Account View (`CreateAccountView`)

This view provides an endpoint for registering new user accounts.  It validates user input, creates a new user in the database, and returns user details upon successful registration.

```python
class CreateAccountView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        if type(request.data) is not dict:
            return api_error("Invalid request type")
        try:
            if validate_email(request.data['email']) \
                    and validate_username(request.data['username']):
                first_name = check_name(request.data['first_name'])
                last_name = check_name(request.data['last_name'])

                user = User.objects.create_user(email=request.data['email'],
                                                password=check_password(request.data['password']),
                                                username=request.data['username'])

                user.first_name = first_name
                user.last_name = last_name
                user.acct_type = AccountType.unverify
                user.save()

                return api_created_success({
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "acct_type": user.acct_type
                })
            else:
                return api_error("Invalid email or username")
        except IntegrityError:
            return api_error("Username already exist. Please try again")
        except KeyError as keyErr:
            return api_error('{} is missing'.format(keyErr.__str__()))
        except (WeakPasswordError, InvalidNameException, TypeError) as error:
            return api_error(error.__str__())
```

### 1.1. `POST` Request Handling

Handles the creation of a new user account.

#### Parameters

| Parameter    | Type     | Description                                                                                                                                                                             |
| :----------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `request`    | `Request`| The request object containing user data in the body.  The body should be a dictionary.                                                                                              |
| `*args`      |          | Additional positional arguments (not used).                                                                                                                                            |
| `**kwargs`   |          | Additional keyword arguments (not used).                                                                                                                                               |
| `email`      | `string` | The email address of the new user. Must be a valid email format.                                                                                                                       |
| `username`   | `string` | The username of the new user. Must be a valid username format.                                                                                                                    |
| `password`   | `string` | The password for the new user.  Must meet complexity requirements.                                                                                                                      |
| `first_name` | `string` | The first name of the new user.  Must be a valid name format.                                                                                                                               |
| `last_name`  | `string` | The last name of the new user. Must be a valid name format.                                                                                                                         |

#### Returns

`Response`: A JSON response indicating success or failure.

*   **Success:** Returns a JSON object with the created user's `username`, `first_name`, `last_name`, `email`, and `acct_type`.  The HTTP status code is 201 (Created).
*   **Failure:** Returns a JSON object with an error message and an appropriate HTTP status code (e.g., 400 Bad Request).

#### Exceptions

*   `IntegrityError`: Raised if the username already exists in the database.
*   `KeyError`: Raised if any of the required fields (`email`, `username`, `password`, `first_name`, `last_name`) are missing from the request data.
*   `WeakPasswordError`: Raised if the provided password does not meet the required complexity criteria.
*   `InvalidNameException`: Raised if the provided first or last name is invalid.
*   `TypeError`: Raised if the request data is not a dictionary.

#### Usage Example

```
POST /api/create_account/

{
    "username": "newuser",
    "password": "SecurePassword123",
    "email": "newuser@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

## 2. Get Tokens For User (`get_tokens_for_user`)

This function generates JWT (JSON Web Token) refresh and access tokens for a given user.

```python
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
```

### 2.1. Parameters

| Parameter | Type   | Description                                      |
| :-------- | :----- | :----------------------------------------------- |
| `user`    | `User` | The user object for whom to generate the tokens. |

### 2.2. Returns

`dict`: A dictionary containing the `refresh` and `access` tokens.

*   `refresh`: The refresh token (used to obtain a new access token).
*   `access`: The access token (used for authentication).

### 2.3. Usage Example

```python
user = User.objects.get(username='existinguser')
tokens = get_tokens_for_user(user)
print(tokens)
# Expected Output (example):
# {'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...', 'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'}
```

## 3. Login View (`LoginView`)

This view handles user login. It authenticates the user based on the provided username and password and returns JWT tokens upon successful authentication.

```python
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return api_error("Username and password are required")

        user = authenticate(username=username, password=password)
        if user:
            tokens = get_tokens_for_user(user)
            return api_created_success({
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "token": tokens['access'],
                "refresh_token": tokens['refresh'],
            })
        return api_error("Invalid username or password")
```

### 3.1. `POST` Request Handling

Handles the user login request.

#### Parameters

| Parameter  | Type     | Description                                                                 |
| :--------- | :------- | :-------------------------------------------------------------------------- |
| `request`  | `Request`| The request object containing the username and password in the request body.|
| `username` | `string` | The username of the user attempting to log in.                            |
| `password` | `string` | The password of the user attempting to log in.                            |

#### Returns

`Response`: A JSON response containing user details and tokens upon successful login, or an error message upon failure.

*   **Success:** Returns a JSON object with the user's `user_id`, `username`, `first_name`, `last_name`, `email`, `token` (access token), and `refresh_token`. The HTTP status code is 201 (Created).
*   **Failure:** Returns a JSON object with an error message indicating invalid credentials or missing parameters. The HTTP status code is 400 (Bad Request) or 401 (Unauthorized).

#### Usage Example

```
POST /api/login/

{
    "username": "existinguser",
    "password": "correctpassword"
}
```

## 4. Logout View (`Logout`)

This view handles user logout. It invalidates the user's session.

```python
class Logout(APIView):
    def get(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)
```

### 4.1. `GET` Request Handling

Handles the user logout request.

#### Parameters

| Parameter | Type     | Description                                   |
| :-------- | :------- | :-------------------------------------------- |
| `request` | `Request`| The request object.                           |

#### Returns

`Response`: A 200 OK response indicating successful logout.

#### Usage Example

```
GET /api/logout/
```
