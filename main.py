import multiprocessing
import time
import server
import rest_proxy
import uvicorn

def start_server():
    server.serve()

def start_rest_proxy():
    uvicorn.run("rest_proxy:app", host="127.0.0.1", port=8000, log_level="info")

if __name__ == '__main__':
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()

    time.sleep(2)

    proxy_process = multiprocessing.Process(target=start_rest_proxy)
    proxy_process.start()

    try:
        server_process.join()
        proxy_process.join()
    except KeyboardInterrupt:
        print("Stopping processes...")
        server_process.terminate()
        proxy_process.terminate()