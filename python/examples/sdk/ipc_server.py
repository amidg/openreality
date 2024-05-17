from openreality.sdk.ipc import IPCServer
import time
import zmq

start_time = time.time()
socket = "openreality.example.socket"

server = IPCServer(socket=socket)
server.start()

while time.time() - start_time < 45:
    if server.message_available:
        print(f"Received Message {server.last_message}")

server.stop()
server.join()
