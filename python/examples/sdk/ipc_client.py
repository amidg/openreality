from openreality.sdk.ipc import SocketClient
import time

client = SocketClient(name="openreality.example.socket")
client.start()
timeout = False
start_time = time.time()

for i in range(10):
    msg = {f"{i}": "'hello world'"}
    client.send(msg)
    print(f"Sent message: {msg}")
    while not client.reply_available:
        if time.time() - start_time > 10:
            timeout = True
            break
    if timeout:
        break
    print(client.msg)
# useless here, just demo
client.stop()
client.join()
