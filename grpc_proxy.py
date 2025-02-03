import grpc
import api_v2_pb2
import api_v2_pb2_grpc
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from google.protobuf.empty_pb2 import Empty
import json

# Инициализация FastAPI
app = FastAPI(title="REST API Proxy to gRPC", description="Проксирование REST API в gRPC")

# Устанавливаем соединение с gRPC-сервером
channel = grpc.insecure_channel("localhost:50051")
grpc_client = api_v2_pb2_grpc.AppStub(channel)


# Модель для создания задачи
class CreateTaskRequest(BaseModel):
    description: str
    metadata: dict


@app.get("/info", summary="Получить информацию о сервере")
async def get_info():
    response = grpc_client.GetInfo(Empty())
    return json.loads(response.data)


@app.get("/tasks", summary="Получить список задач")
async def get_tasks():
    tasks = []
    for task in grpc_client.GetTasks(Empty()):
        tasks.append({"id": task.id, "description": task.description})
    return tasks


@app.post("/tasks", summary="Создать задачу")
async def create_task(request: CreateTaskRequest):
    response = grpc_client.Create(api_v2_pb2.Task(
        id="", description=request.description
    ))
    return {"id": response.id, "description": response.description}


@app.post("/tasks/{task_id}/launch", summary="Запустить задачу")
async def launch_task(task_id: str):
    grpc_client.Launch(api_v2_pb2.TaskRequest(id=task_id))
    return {"message": f"Задача {task_id} запущена"}


@app.post("/tasks/{task_id}/cancel", summary="Отменить задачу")
async def cancel_task(task_id: str):
    grpc_client.Cancel(api_v2_pb2.TaskRequest(id=task_id))
    return {"message": f"Задача {task_id} отменена"}


@app.post("/tasks/{task_id}/upload", summary="Загрузить файл в задачу")
async def upload_file(task_id: str, file: UploadFile = File(...)):
    file_data = await file.read()

    response = grpc_client.UploadData(api_v2_pb2.FileUploadRequest(
        task_id=task_id,
        filename=file.filename,
        content=file_data
    ))

    return {"message": "Файл загружен", "task_id": task_id, "filename": file.filename}
