import sys
import json
import time
import socket
import threading
import traceback
import subprocess
from typing import TypedDict

from src import protocol
from version import __version__, __schemaVersion__

class StatusDict(TypedDict):
    ups_status: str
    battery_charge: str
class UPS:
    def __init__(self, cacheTime: int):
        self.lock = threading.Lock()
        self.cache = {}
        self.timelifecache = cacheTime
    
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
    
    def _status(self, ups_name='ecoEaton', host='localhost'):
        try:
            result = subprocess.run(
                ['upsc', f'{ups_name}@{host}'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                print("Erreur: Impossible d'interroger l'UPS.")
                print(result.stderr.strip())
                return None
            
            info = {}
            for line in result.stdout.splitlines():
                if ':' in line:
                    key, val = line.split(':', 1)
                    info[key.strip().replace('.', '_')] = val.strip()
            
            return info
        except Exception as e:
            print(f"Exception lors de la vérification UPS : {e}")
            print(traceback.format_exc())
            return None

def client(sock: socket.socket, ups: UPS):
    timeoutNoPing = 20
    try:
        sock.settimeout(2)
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
        JSON = json.load(file)
    
    if JSON["schemaVersion"] != __schemaVersion__:
        sys.exit(109)
    
    def test(JSON):
        JSON["cacheUPStime"]
    
    test(JSON)
    
    try:
        ups = UPS(cacheTime=JSON["cacheUPStime"])
        sock = server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 2152))
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