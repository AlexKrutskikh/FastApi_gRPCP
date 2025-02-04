import grpc
import generated.api_v2_pb2 as api_v2
import generated.api_v2_pb2_grpc as api_v2_grpc
from google.protobuf.empty_pb2 import Empty

channel = grpc.insecure_channel('localhost:50051')
stub = api_v2_grpc.AppStub(channel)

def get_info():
    response = stub.GetInfo(Empty())
    print("Server Info:", response.value)

def get_tasks():
    tasks = stub.GetTasks(Empty())
    for task in tasks:
        print(f"Task ID: {task.id.value}, State: {api_v2.Task.State.Name(task.state)}, Message: {task.msg}")

def create_task(description):
    request = api_v2.JSON(value=description)
    response = stub.Create(request)
    print(f"Created Task ID: {response.id.value}, State: {api_v2.Task.State.Name(response.state)}, Message: {response.msg}")

def launch_task(task_id):
    request = api_v2.ID(value=task_id)
    stub.Launch(request)
    print(f"Task {task_id} launched")

def review_task(task_id):
    request = api_v2.ID(value=task_id)
    response = stub.Review(request)
    print(f"Task ID: {response.id.value}, State: {api_v2.Task.State.Name(response.state)}, Message: {response.msg}")

def pickup_task_data(task_id):
    request = api_v2.ID(value=task_id)
    data_stream = stub.Pickup(request)
    for data in data_stream:
        if data.HasField("json"):
            print(f"Part {data.part}: JSON Content: {data.json.value}")
        elif data.HasField("buffer"):
            print(f"Part {data.part}: Buffer Size: {len(data.buffer)} bytes")

def cancel_task(task_id):
    request = api_v2.ID(value=task_id)
    stub.Cancel(request)
    print(f"Task {task_id} cancelled")