from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from google.protobuf.json_format import MessageToJson
import api_v2_pb2  # Импортируем сгенерированный модуль

app = FastAPI()

# Пример POST запроса для создания задачи
@app.post("/create-task/")
async def create_task(
    task_input: dict = Form(...),  # Получаем данные для задачи в формате JSON
    file: UploadFile = File(...),  # Загружаем файл
):
    # Преобразуем входные данные JSON в объект protobuf
    task = api_v2_pb2.Task()
    task.id.value = task_input.get("id", "")  # ID
    task.state = api_v2_pb2.Task.State.QUEUED  # Состояние задачи, например
    task.msg = task_input.get("msg", "")  # Сообщение задачи

    # Чтение загруженного файла
    file_content = await file.read()

    # Преобразуем объект Task в JSON для отправки ответа
    task_json = MessageToJson(task)

    return JSONResponse(content={
        "task": task_json,  # JSON-сообщение задачи
        "file_size": len(file_content),  # Размер загруженного файла
        "filename": file.filename  # Имя файла
    })
