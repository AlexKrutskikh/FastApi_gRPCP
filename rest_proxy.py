from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import grpc
import generated.api_v2_pb2 as api_v2
import generated.api_v2_pb2_grpc as api_v2_grpc
from google.protobuf.empty_pb2 import Empty  # Импортируем Empty из google.protobuf
from google.protobuf.json_format import MessageToDict, ParseDict
from typing import List

app = FastAPI(
    title="gRPC to REST Proxy",
    description="Прокси для преобразования REST API в gRPC",
    version="1.0.0"
)

grpc_channel = grpc.insecure_channel("localhost:50051")
grpc_stub = api_v2_grpc.AppStub(grpc_channel)

class CreateTaskRequest(BaseModel):
    description: str

@app.get("/info", summary="Получить информацию о сервере")
async def get_info():
    try:
        response = grpc_stub.GetInfo(Empty())  # Используем Empty()
        return MessageToDict(response)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

@app.get("/tasks", summary="Получить список задач", response_model=List[dict])
async def get_tasks():
    try:
        tasks = []
        for task in grpc_stub.GetTasks(Empty()):  # Используем Empty()
            tasks.append(MessageToDict(task))
        return tasks
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

@app.post("/tasks", summary="Создать задачу", response_model=dict)
async def create_task(request: CreateTaskRequest):
    try:
        grpc_request = ParseDict({"value": request.description}, api_v2.JSON())
        response = grpc_stub.Create(grpc_request)
        return MessageToDict(response)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

@app.post("/tasks/{task_id}/upload", summary="Загрузить файл для задачи", response_model=dict)
async def upload_file(task_id: str, file: UploadFile = File(...)):
    try:
        def generate_inputs():
            part = 1
            while True:
                content = file.file.read(1024)  # Синхронное чтение
                if not content:
                    break
                yield api_v2.Input(
                    id=api_v2.ID(value=task_id),
                    data=api_v2.Data(part=part, buffer=content)
                )
                part += 1

        grpc_stub.Upload(generate_inputs())  # Передаем синхронный генератор
        return {"message": f"File uploaded successfully for task {task_id}"}

    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

    finally:
        await file.close()
