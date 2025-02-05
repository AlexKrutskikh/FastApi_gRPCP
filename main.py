import argparse

import grpc
import uvicorn

import generated.api_v2_pb2_grpc as api_v2_grpc
from rest_proxy import app, get_stub


def setup_grpc_channel(grpc_port: int):
    """
    Создает канал связи с gRPC-сервером.
    :param grpc_port: Порт gRPC-сервера.
    :return: Объект stub.
    """
    channel = grpc.insecure_channel(f"localhost:{grpc_port}")
    stub = api_v2_grpc.AppStub(channel)
    return stub


def run_api(stub):
    """
    Запускает FastAPI-приложение с переданным stub.
    :param stub: Объект stub для gRPC.
    """
    app.dependency_overrides[get_stub] = lambda: stub
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="REST API proxy for gRPC service")
    parser.add_argument(
        "--grpc-port", type=int, required=True, help="Port for gRPC service"
    )
    args = parser.parse_args()

    stub = setup_grpc_channel(args.grpc_port)
    run_api(stub)
