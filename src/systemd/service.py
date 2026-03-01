import time
import traceback

from pydbus import SystemBus

def start(name, bus: SystemBus) -> bool:
    try:
        systemd1 = bus.get(".systemd1")
        full_unit_name = f"{name}.service"
        
        job_path = systemd1.StartUnit(full_unit_name, "replace")
        
        unit_path = systemd1.GetUnit(full_unit_name)
        unit = bus.get(".systemd1", unit_path)
        
        while True:
            state = unit.ActiveState
            if state == "active":
                break
            elif state == "failed":
                break
            time.sleep(0.5)
        return True
    except Exception as e:
        print(f"{name} : [ERREUR] Impossible de démarrer le service : {traceback.format_exc()}")
        return False

def stop(name, bus: SystemBus) -> bool:
        try:
            systemd1 = bus.get(".systemd1")
            full_unit_name = f"{name}.service"
            
            job_path = systemd1.StopUnit(full_unit_name, "replace")
            
            unit_path = systemd1.GetUnit(full_unit_name)
            unit = bus.get(".systemd1", unit_path)
            
            while True:
                state = unit.ActiveState
                if state == "inactive":
                    break
                elif state == "failed":
                    break
                time.sleep(0.5)
            return True
        except Exception as e:
            print(f"{name} : [ERREUR] Impossible d'arrêter le service : {traceback.format_exc()}")
            return False