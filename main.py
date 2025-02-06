import argparse

import grpc
import uvicorn

from generated.api_v2_pb2_grpc import AppStub
from rest_proxy import app, get_stub

"""
Главная функция для запуска REST API-прокси для gRPC-сервиса.

Описание:
    1. Парсит аргументы командной строки для получения порта gRPC-сервера.
    2. Создает канал связи с gRPC-сервером и инициализирует stub для взаимодействия.
    3. Настройка FastAPI для использования созданного stub через механизм dependency overrides.
    4. Запускает FastAPI-приложение с помощью Uvicorn на указанном хосте и порту.

Аргументы:
    Данная функция не принимает внешних аргументов. Аргументы командной строки парсятся внутри функции.

Возвращает:
    None. Функция запускает сервер и работает бесконечно до остановки процесса.
"""


def main():

    parser = argparse.ArgumentParser(description="REST API proxy for gRPC service")
    parser.add_argument(
        "--grpc-port", type=int, required=True, help="Port for gRPC service"
    )
    args = parser.parse_args()

    channel = grpc.insecure_channel(f"localhost:{args.grpc_port}")
    stub = AppStub(channel)

    app.dependency_overrides[get_stub] = lambda: stub

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
