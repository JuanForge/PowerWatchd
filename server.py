import sys
import json
import time
import socket
import argparse
import threading
import traceback
from typing import TypedDict

from src import protocol
from version import __version__, __schemaVersion__
from src.ups import backend0
from src.ups import backend1
from src.ups import backend2

class StatusDict(TypedDict):
    ups_status: str
    battery_charge: str
class UPS:
    def __init__(self, cacheTime: int, backend: int, ups_name: str):
        self.lock = threading.Lock()
        self.cache = {}
        self.timelifecache = cacheTime
        
        if backend == 0:
            self.backend = backend0.session(ups_name=ups_name)
        elif backend == 1:
            self.backend = backend1.session(ups_name=ups_name)
        elif backend == 2:
            self.backend = backend2.session(ups_name=ups_name)
        else:
            raise RuntimeError("Invalid backend number.")
    
    def setTimeLifeCache(self, x: int | float):
        with self.lock:
            self.timelifecache = x
    
    def status(self) -> StatusDict:
        with self.lock:
            if self.cache.get("time", 0) < time.monotonic() - self.timelifecache:
                self.cache["data"] = self._status()
                self.cache["time"] = time.monotonic()
                if self.cache["data"] == None:
                    raise RuntimeError("UPS data stale ( 32 )")
                else:
                    return self.cache["data"]
            else:
                return self.cache["data"]
    

def client(sock: socket.socket, ups: UPS):
    timeoutNoPing = 10
    try:
        sock.settimeout(1.5)
        sesssion = protocol.network(sock)
        start_time: dict = {
                        "init": time.monotonic(),
                        "ping": time.monotonic()
                    }
        while True:
            try:
                data = sesssion.recv()
                
                start_time["ping"] = time.monotonic()
                
                if data["type"] == "ping":
                    pass
                
                data = ups.status()
                if "OB" in data["ups_status"]:
                    sesssion.send({"type": "UPS",
                                    "status": False,
                                    "battery.charge": int(data["battery_charge"])
                                })
                else:
                    sesssion.send({"type": "UPS",
                                    "status": True,
                                    "battery.charge": int(data["battery_charge"])
                                })
                
                time.sleep(1)
            except socket.timeout:
                if time.monotonic() - start_time["ping"] > timeoutNoPing:
                    return
                else:
                    continue
    except Exception as e:
        print(traceback.format_exc())
    finally:
        if sock:
            sock.close()

if __name__ == "__main__":
    with open('config.server.json', 'r') as file:
        JSON:dict = json.load(file)
    
    if JSON["schemaVersion"] != __schemaVersion__:
        sys.exit(109)
    
    parser = argparse.ArgumentParser(
        description="Configuration CLI",
        allow_abbrev=False
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=2152
    )
    
    parser.add_argument(
        "--cacheUPStime",
        type=int,
        default=JSON["cacheUPStime"],
        help=f"Cache uptime (seconds), default : {JSON['cacheUPStime']}"
    )
    
    parser.add_argument(
        "--UPSname",
        help=f"UPS name, default : {JSON['UPSname']}"
    )
    
    parser.add_argument(
        "--UPSbackend",
        type=int,
        default=JSON["UPSbackend"],
        help=f"UPS backend ID, default : {JSON['UPSbackend']}",
        choices=[0, 1, 2]
    )
    args, unknown = parser.parse_known_args()
    
    if unknown:
        print(f"Error: Unrecognized arguments: {', '.join(unknown)}")
        sys.exit(139)
    
    JSON["cacheUPStime"] = args.cacheUPStime
    JSON["UPS"] = args.UPSname
    JSON["UPSbackend"] = args.UPSbackend
    
    try:
        ups = UPS(cacheTime=JSON["cacheUPStime"],
                    backend=JSON.get("UPSbackend", 2),
                    ups_name=JSON["UPSname"])
        
        sock = server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((args.host, args.port))
        sock.listen(20)
        
        while True:
            try:
                conn, addr = sock.accept()
                threading.Thread(target=client, args=(conn, ups), daemon=True).start()
            except Exception as e:
                print(traceback.format_exc())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(traceback.format_exc())