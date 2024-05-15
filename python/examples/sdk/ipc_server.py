from openreality.sdk.ipc import SocketServer
import time

# server
server = SocketServer(name="openreality.example.socket")
server.start()

start_time = time.time()
while time.time() - start_time < 30: # 30 seconds
    if server.msg_available:
        msg = server.msg
        print(msg)
        for key, value in msg.items():
            server.reply({f"server": f"Received {value} from {key}"})
server.stop()
server.join()
