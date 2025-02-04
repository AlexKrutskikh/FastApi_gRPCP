import grpc
from concurrent import futures
import generated.api_v2_pb2 as api_v2
import generated.api_v2_pb2_grpc as api_v2_grpc
from google.protobuf.empty_pb2 import Empty
import json

class AppServicer(api_v2_grpc.AppServicer):
    def GetInfo(self, request, context):
        info = {
            "name": "SOFTWARE_NAME",
            "version": "SOFTWARE_VERSION",
            "system": {
                "os": "OPERATING_SYSTEM",
                "cpu": "CENTRAL_PROCESSING_UNIT_INFORMATION",
                "gpu": "GRAPHICS_PROCESSING_UNIT_INFORMATION",
                "ram": "RANDOM_ACCESS_MEMORY_INFORMATION"
            }
        }
        return api_v2.JSON(value=json.dumps(info))

    def GetTasks(self, request, context):
        tasks = [
            api_v2.Task(
                id=api_v2.ID(value="task1"),
                state=api_v2.Task.State.CREATED,
                msg="Task 1 created"
            ),
            api_v2.Task(
                id=api_v2.ID(value="task2"),
                state=api_v2.Task.State.RUNNING,
                msg="Task 2 running"
            )
        ]
        for task in tasks:
            yield task

    def Create(self, request, context):
        task_id = api_v2.ID(value="new_task_id")
        task = api_v2.Task(
            id=task_id,
            state=api_v2.Task.State.CREATED,
            msg=f"Created task with ID {task_id.value}"
        )
        return task

    def Upload(self, request_iterator, context):
        for input_data in request_iterator:
            print(f"Received part {input_data.data.part}")
            if input_data.data.HasField("json"):
                print(f"JSON content: {input_data.data.json.value}")
            elif input_data.data.HasField("buffer"):
                print(f"Buffer size: {len(input_data.data.buffer)} bytes")
        return Empty()

    def Launch(self, request, context):
        print(f"Launching task with ID {request.value}")
        return Empty()

    def Review(self, request, context):
        task_id = request.value
        task = api_v2.Task(
            id=request,
            state=api_v2.Task.State.RUNNING,
            msg=f"Task {task_id} is running"
        )
        return task

    def Pickup(self, request, context):
        data_parts = [
            api_v2.Data(part=1, json=api_v2.JSON(value='{"part": "1", "data": "value1"}')),
            api_v2.Data(part=2, buffer=b'some binary data')
        ]
        for data in data_parts:
            yield data

    def Cancel(self, request, context):
        print(f"Cancelling task with ID {request.value}")
        return Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_v2_grpc.add_AppServicer_to_server(AppServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()