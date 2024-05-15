import zmq
from enum import Enum
import threading
import json
from typing import Dict
import collections

"""
    Code below provides basic IPC server that can be used for communication.
    Main idea is to provide "fire-and-forget" communication for the developer
"""
class Server():
    def __init__(self, name: str):
