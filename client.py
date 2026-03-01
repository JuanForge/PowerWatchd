import os
import sys
import time
import json
import socket
import threading
import traceback

from pathlib import Path
from pydbus import SystemBus

from src import buzzer
from src import systemd
from src import protocol
from version import __version__, __schemaVersion__

def keepalive(session: protocol.network):
    try:
        while True:
            session.send({"type": "ping"})
            time.sleep(5)
    except:
        print(f"KEEP ALIVE : {traceback.format_exc()}")

def AntiBoucle(tasks):
    seen = set()
    
    def visit(task_name, path):
        if task_name in path:
            print(f"⚠️ Loop detected : {' -> '.join(path + [task_name])}")
            return False
        if task_name in seen:
            return True
        seen.add(task_name)
        task = next((t for t in tasks if t["name"] == task_name), None)
        if not task:
            return True
        for dep in task.get("dependency", []):
            result = visit(dep, path + [task_name])
            if result is False:
                return False
        return True
    
    for task in tasks:
        result = visit(task['name'], [])
        if result is False:
            return False
    
    print("Aucun cycle détecté.")
    return True

def audio(STOP):
    while STOP[0] == False:
        buzzer.beep(2000, 500)
        time.sleep(2)
    else:
        return True

def shutdown(bus: SystemBus):
    time.sleep(2)
    login1 = bus.get(".login1")
    login1.PowerOff(False)
    return True

def unit(percent: int, task: dict, bus: SystemBus, tasks: list):
    for tache in tasks:
        if task['name'] in tache.get('dependency', []):
            status = systemd.status(tache['name'], bus=bus)
            if isinstance(status, dict):
                if not status['status'] in ('inactive', 'failed', 'deactivating'):
                    print(f"[WARNING] : {task['name']} ask by {tache['name']}")
    
    if percent <= task.get('percent', 100):
        print(f"[WARNING] : STOP : {task['name']}")
        systemd.service.stop(task['name'], bus=bus)
        return True
    else:
        return False

class main:
    def __init__(self, JSON, save: dict = None,):
        if save == None:
            self.data = {}
        else:
            self.data = save
        
        self.JSON = JSON
        self.bus = SystemBus()
        self.threadbeep = None
        self.threadbeepSTOP = [False]
        self.oldstatus = None
        self.threads = None
        self.service_table = []
    
    def update(self, status: bool, charge: int):
        if status == False:
            print("Battery-powered server.")
            if self.threadbeep == None:
                self.threadbeep = threading.Thread(target=audio, args=(self.threadbeepSTOP,), daemon=True)
                self.threadbeep.start()
            
            if self.oldstatus == True:
                for task in tasks:
                    status = systemd.status(task['name'], bus=self.bus)
                    if isinstance(status, dict):
                        if status['status'] in ('active',):
                            self.service_table.append({"name": task['name'], "status": status['status'], "dependency": task.get('dependency', [])})
            
            for task in tasks:
                unit(charge, task, bus=self.bus, tasks=tasks)
            
            if charge <= JSON["OnBattery"]["shutdown"]["percent"]:
                print("SHUTDOWN")
                shutdown(bus=self.bus)
        
        elif status == True:
            if self.oldstatus == False:
                print("Server on mains power.")
            
            if self.threadbeep != None:
                self.threadbeepSTOP[0] = True
                self.threadbeep.join()
                self.threadbeep = None
                self.threadbeepSTOP[0] = False
                
                for task in self.service_table:
                    def __load__(tache: str):
                        current = next((t for t in self.service_table if t['name'] == tache), None)
                        if not current:
                            print(f"[WARNING] : Unknown task : {tache}")
                            return
                        for dep in current.get('dependency', []):
                            __load__(dep)
                        
                        print(f"[DEBUG] : Start : {tache}")
                        
                        systemd.service.start(tache, bus=self.bus)
                    if task['status'] == 'active':
                        __load__(task['name'])
                self.service_table = []
        self.oldstatus = status
    
    def save(self) -> list: return []

if __name__ == "__main__":
    buzzer.beep(2000, 500)
    os.chdir(Path(__file__).resolve().parent)
    
    with open('config.client.json', 'r') as file:
        JSON = json.load(file)
    
    if JSON["schemaVersion"] != __schemaVersion__:
        sys.exit(153)
    
    tasks = JSON['OnBattery']['StopTask']
    if not AntiBoucle(tasks):
        sys.exit(157)
    
    app = main(JSON)
    
    try:
        i = 0
        while i != JSON["offlineServer"]["retry"]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(JSON["offlineServer"]["tcpTimeoutSec"])
                print(f"Connect ( try: {i+1})...")
                sock.connect(("127.0.0.1", 2152))
                print("Connect : OK")
                break
            except Exception as e:
                print(str(e))
                i += 1
                time.sleep(JSON["offlineServer"]["retryIntervalSec"])
        else:
            if JSON["offlineServer"]["shutdown"] == True:
                shutdown(SystemBus())
                sys.exit(178)
            else:
                sys.exit(180)
        
        sock.settimeout(1)
        
        session = protocol.network(sock)
        
        threading.Thread(target=keepalive, args=(session,), daemon=True).start()
        
        while True:
            try:
                data = session.recv()
                if data["type"] == "UPS":
                    app.update(data["status"], data["battery.charge"])
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(traceback.format_exc())
    finally:
        with open("session.client.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(app.save(), indent=4))
        
        if sock:
            sock.close()