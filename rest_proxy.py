from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from client_def import (cancel_task, create_new_task, get_server_info,
                        get_task_list, launch_task, pickup_task_data,
                        review_task, upload_task_data)

app = FastAPI()


# Зависимость для получения stub
def get_stub():
    # Эта функция будет переопределена через dependency_overrides
    raise NotImplementedError("Stub dependency not overridden!")


# Эндпоинт для получения информации о сервере
@app.get("/server-info")
async def server_info(stub=Depends(get_stub)):
    try:
        result = get_server_info(stub)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching server info: {str(e)}"
        )


# Эндпоинт для получения списка задач
@app.get("/tasks")
async def list_tasks(stub=Depends(get_stub)):
    try:
        result = get_task_list(stub)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


# Эндпоинт для создания новой задачи
@app.post("/tasks/create")
async def create_task(description: str, stub=Depends(get_stub)):
    try:
        result = create_new_task(description, stub)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


# Эндпоинт для загрузки данных задачи
@app.post("/tasks/{task_id}/upload")
async def upload_task(
    task_id: str, file: UploadFile = File(...), stub=Depends(get_stub)
):
    try:
        buffer_data = await file.read()
        result = upload_task_data(task_id, buffer_data, stub)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading data: {str(e)}")


# Эндпоинт для запуска задачи
@app.post("/tasks/{task_id}/launch")
async def launch_task_endpoint(task_id: str, stub=Depends(get_stub)):
    try:
        result = launch_task(task_id, stub)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error launching task: {str(e)}")


# Эндпоинт для проверки статуса задачи
@app.get("/tasks/{task_id}/status")
async def review_task_endpoint(task_id: str, stub=Depends(get_stub)):
    try:
        result = review_task(task_id, stub)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reviewing task: {str(e)}")


# Эндпоинт для получения данных задачи
@app.get("/tasks/{task_id}/data")
async def pickup_task_data_endpoint(task_id: str, stub=Depends(get_stub)):
    try:
        result = pickup_task_data(task_id, stub)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error picking up task data: {str(e)}"
        )


# Эндпоинт для отмены задачи
@app.delete("/tasks/{task_id}/cancel")
async def cancel_task_endpoint(task_id: str, stub=Depends(get_stub)):
    try:
        result = cancel_task(task_id, stub)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error canceling task: {str(e)}")
