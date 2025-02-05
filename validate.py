import json

from fastapi import HTTPException

import generated.api_v2_pb2 as api_v2


def validate_task_exists():
    """
    Декоратор для проверки существования задачи.
    Возвращает информацию о задаче для использования в функции.
    """

    def decorator(func):
        def wrapper(task_id, stub):

            try:

                request = api_v2.ID(value=task_id)
                response = stub.Review(request)

                if response.id.value != task_id:
                    raise ValueError(f"Task {task_id} does not exist")

                return func(task_id, stub)
            except Exception as e:
                if "not found" in str(e).lower() or isinstance(e, ValueError):
                    raise HTTPException(
                        status_code=404, detail=f"Task {task_id} does not exist"
                    )
                else:
                    raise HTTPException(
                        status_code=500, detail=f"Error validating task: {str(e)}"
                    )

        return wrapper

    return decorator


def validate_json_description():
    """
    Декоратор для проверки, что description является валидной JSON-строкой.
    """

    def decorator(func):
        def wrapper(description, stub):

            try:

                parsed_json = json.loads(description)
                if not isinstance(parsed_json, dict):
                    raise ValueError("Description must be a JSON object (dictionary)")

                return func(description, stub)

            except json.JSONDecodeError:

                raise HTTPException(
                    status_code=400, detail="Invalid JSON format in 'description'"
                )
            except ValueError as ve:

                raise HTTPException(status_code=400, detail=str(ve))

        return wrapper

    return decorator
