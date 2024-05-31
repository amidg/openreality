import zmq
import threading
from typing import Dict
import collections

# global variables
"""
    Sockets should be placed to the /var/run in according to Linux spec:
    https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s15.html
    However, because this code runs in user space, for now sockets are placed in /tmp
"""
SOCKET_ROOT = "ipc:///tmp" # this is usable on Linux only

class StandardMessages():
    STOP = "STOP"
    DONE = "DONE"
    REG_SOCK = "REG_SOCK"
    SEND_MSG = "SEND_MSG"


"""
    IPC class provides PyZMQ based implementation of the Unix Sockets.
    Exchange messages with OpenReality components.
"""
# TODO: make this inherited from the common IPC class
class IPCServer(threading.Thread):
    def __init__(self, socket: str, buffer_size=100):
        # thread
        super().__init__()
        self._is_busy = False
        self._events = {
            StandardMessages.STOP: threading.Event(),
            StandardMessages.REG_SOCK: threading.Event(),
            StandardMessages.SEND_MSG: threading.Event()
        }

        # sockets
        self._context = zmq.Context()
        self._socket = f"{SOCKET_ROOT}/{socket}" # this is socket used for core app requests
        self._system_socket = self._context.socket(zmq.REP)
        self._system_socket.bind(self._socket)

        # registered sockets
        self._registered_sockets = {}
        self._poller = zmq.Poller()
        self._poller.register(self._system_socket, zmq.POLLIN)
        
        # messages
        self._buffer = collections.deque(maxlen=buffer_size)

    @property
    def socket(self):
        return self._socket

    @property
    def message_available(self) -> bool:
        return len(self._buffer) > 0

    @property
    def last_message(self) -> Dict[str, str]:
        # TODO: add error handling
        return self._buffer.popleft() # returns dict

    def run(self):
        while not self._events[StandardMessages.STOP].is_set():
            # events will be empty if nothing to receive
            self._is_busy = False
            # register event
            events = dict(self._poller.poll(1000)) # 1 sec block only
            if events:
                print(f"New message available {events}")
                self._is_busy = True
                # register new socket request
                if events.get(self._system_socket) == zmq.POLLIN:
                    print("Requested socket add")
                    msg = self._system_socket.recv_json()
                    if StandardMessages.REG_SOCK in msg:
                        # register new socket
                        new_socket = msg[StandardMessages.REG_SOCK]
                        if new_socket not in self._registered_sockets:
                            self._registered_sockets[new_socket] = self._context.socket(zmq.PULL)
                            self._registered_sockets[new_socket].connect(f"{SOCKET_ROOT}/{new_socket}")
                            self._poller.register(self._registered_sockets[new_socket], zmq.POLLIN)
                        # reply
                        self._system_socket.send_json(
                            {new_socket: StandardMessages.DONE},
                            zmq.NOBLOCK
                        )
                        print(f"New Socket added: {new_socket}")
                        continue # do I need this?
                # other polls
                for name, socket in self._registered_sockets.items():
                    if events.get(socket) == zmq.POLLIN:
                        print(f"Received message on socket {name}")
                        # {socket_name: {}}
                        self._buffer.append({name: socket.recv_json()})

    def stop(self):
        self._events[StandardMessages.STOP].set()


class IPCApp(threading.Thread):
    def __init__(self, target_req_socket: str):
        # thread
        super().__init__()
        self._is_busy = False
        self._events = {
            StandardMessages.STOP: threading.Event(),
            StandardMessages.REG_SOCK: threading.Event(),
            StandardMessages.SEND_MSG: threading.Event()
        }

        # server negotiation
        self._context = zmq.Context() # zmq.sugar.context.Context
        self._socket = f"{SOCKET_ROOT}/{target_req_socket}" # this is socket used for core app requests
        self._system_socket = self._context.socket(zmq.REQ)
        self._system_socket.connect(self._socket) # this is used for the comms with the system app
        self._system_socket_last_reply =  None

        # new sockets
        self._new_socket_to_register = None
        self._push_sockets = {}

        # messaging
        self._msg = None
        self._msg_topic = None
        self._msg_socket = None

    @property
    def socket(self):
        return self._socket

    def register_socket(self, socket: str):
        """
            This function allows to register socket with the core app
        """
        if self._events[StandardMessages.REG_SOCK].is_set():
            raise ValueError("Socket is busy, try later")
            return False
        self._new_socket_to_register = socket
        self._events[StandardMessages.REG_SOCK].set()
        while self._events[StandardMessages.REG_SOCK].is_set():
            # when event is clear we are good to proceed
            pass
        return True

    def send_msg(self, socket: str, topic: str, msg: str):
        """
            Send message
        """
        # check if socket is registered
        if socket not in self._push_sockets:
            # TODO: add software check via OS module or communication to the core app
            raise ValueError(f"Socket {socket} is not registered, please, register it before sending message")
            return
        
        # check if we are busy sending a message
        if self._events[StandardMessages.SEND_MSG].is_set():
            raise ValueError("Socket is busy, try later")
            return
        # if all good, send message
        self._msg_socket = socket
        self._msg_topic = topic
        self._msg = msg
        self._events[StandardMessages.SEND_MSG].set()

    def run(self):
        while not self._events[StandardMessages.STOP].is_set():
            # register new socket
            self._is_busy = False
            if self._events[StandardMessages.REG_SOCK].is_set():
                self._is_busy = True
                # register new socket
                self._push_sockets[self._new_socket_to_register] = self._context.socket(zmq.PUSH)
                self._push_sockets[self._new_socket_to_register].bind(f"{SOCKET_ROOT}/{self._new_socket_to_register}")
                # negotiate new socket with the system app
                self._system_socket.send_json(
                    {StandardMessages.REG_SOCK: self._new_socket_to_register},
                    zmq.NOBLOCK
                )
                self._system_socket_last_reply = self._system_socket.recv_json(10) # 10 seconds timeout
                # TODO: how to evaluate success?
                self._events[StandardMessages.REG_SOCK].clear()
            elif self._events[StandardMessages.SEND_MSG].is_set():
                self._is_busy = True
                # send message
                msg = {self._msg_topic: self._msg}
                print(f"Sending message {msg} to {self._msg_socket}")
                self._push_sockets[self._msg_socket].send_json(msg)
                self._events[StandardMessages.SEND_MSG].clear()

    def stop(self):
        self._events[StandardMessages.STOP].set()
