from openreality.sdk.ipc import IPCApp
import time
import zmq

start_time = time.time()
socket = "openreality.example.socket"
app = IPCApp(target_req_socket=socket)
app.start()

# create new socket
sockets = []
for i in range(10):
    sockets.append(f"test{i}.socket")
try:
    for sock in sockets:
        if app.register_socket(sock):
            print(f"Registered new socket: {sock}")
except ValueError:
    app.stop()
    app.join()
    exit()

while time.time() - start_time < 30:
    for sock in sockets:
        try:
            app.send_msg(
                socket=sock,
                topic="Hello",
                msg="World"
            )
            time.sleep(0.1)
        except ValueError as e:
            print(e)
    time.sleep(1)

app.stop()
app.join()
