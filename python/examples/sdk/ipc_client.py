from openreality.sdk.ipc import IPCApp
import time
import zmq

start_time = time.time()
socket = "openreality.example.socket"
app = IPCApp(target_req_socket=socket)
app.start()

# create new socket
new_socket = "test1.socket"
try:
    if app.register_socket(new_socket):
        print("Registered new socket")
except ValueError:
    app.stop()
    app.join()
    exit()

while time.time() - start_time < 30:
    try:
        app.send_msg(
            socket=new_socket,
            topic="Hello",
            msg="World"
        )
    except ValueError as e:
        print(e)
    time.sleep(1)

app.stop()
app.join()
