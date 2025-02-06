from fastapi import HTTPException
from google.protobuf.empty_pb2 import Empty

import generated.api_v2_pb2 as api_v2
from validate import validate_json_description, validate_task_exists


# Функция для получения информации о сервере
def get_server_info(stub):
    try:
        response = stub.GetInfo(Empty())
        return {"info": response.value}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching server info: {str(e)}"
        )


# Функция для получения списка задач
def get_task_list(stub):
    try:
        tasks = stub.GetTasks(Empty())
        task_list = []
        for task in tasks:
            state_name = api_v2.Task.State.Name(task.state)
            task_list.append(
                {"task_id": task.id.value, "state": state_name, "message": task.msg}
            )
        return task_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


# Функция для создания новой задачи с декоратором для валидации
@validate_json_description()
def create_new_task(description, stub):
    try:
        request = api_v2.JSON(value=description)
        response = stub.Create(request)
        state_name = api_v2.Task.State.Name(response.state)
        return {
            "task_id": response.id.value,
            "state": state_name,
            "message": response.msg,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


# Функция принимает поток данных
def upload_task_data(task_id, buffer_data, stub):
    try:

        data = api_v2.Data(part=1, buffer=buffer_data)

        input_data = api_v2.Input(id=api_v2.ID(value=task_id), data=data)

        def generate_input_stream():
            yield input_data

        stub.Upload(generate_input_stream())
        return {"status": "Data uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading data: {str(e)}")


# Функция для запуска задачи с декоратором для валидации
@validate_task_exists()
def launch_task(task_id, stub):
    try:
        request = api_v2.ID(value=task_id)
        stub.Launch(request)
        return {"status": f"Task {task_id} launched"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error launching task: {str(e)}")


# Функция для проверки статуса задачи с декоратором для валидации
@validate_task_exists()
def review_task(task_id, stub):
    try:
        request = api_v2.ID(value=task_id)
        response = stub.Review(request)
        state_name = api_v2.Task.State.Name(response.state)
        return {
            "task_id": response.id.value,
            "state": state_name,
            "message": response.msg,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reviewing task: {str(e)}")


# Функция для получения данных задачи с декоратором для валидации
@validate_task_exists()
def pickup_task_data(task_id, stub):
    try:
        request = api_v2.ID(value=task_id)
        data_stream = stub.Pickup(request)
        data_parts = []
        for data in data_stream:
            if data.HasField("json"):
                data_parts.append(
                    {"part": data.part, "content": "JSON", "value": data.json.value}
                )
            elif data.HasField("buffer"):
                data_parts.append(
                    {"part": data.part, "content": "BUFFER", "size": len(data.buffer)}
                )
        return data_parts
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error picking up task data: {str(e)}"
        )


# Функция для отмены задачи с декоратором для валидации
@validate_task_exists()
def cancel_task(task_id, stub):
    try:
        request = api_v2.ID(value=task_id)
        stub.Cancel(request)
        return {"status": f"Task {task_id} cancelled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error canceling task: {str(e)}")
