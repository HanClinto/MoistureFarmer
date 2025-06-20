import json

class Simulation:
    def __init__(self):
        self.gonky = {
            "object_id": "eg6_gonky",
            "type": "droid",
            "subtype": "power droid",
            "name": "Gonky",
            "model": "EG-6",
            "description": "EG-6 power droid",
            "location": {"x": 0, "y": 0},
            "battery_level": 30
        }
        self.equipment = [
            self.gonky,
            {"object_id": "vaporator_1", "type": "vaporator", "model": "GX-8", "location": {"x": 10, "y": 15}, "battery_level": 50},
            {"object_id": "power_station_1", "type": "power station", "subtype": "medium fusion reactor power generator", "model": "MFCR-200", "location": {"x": 5, "y": 5}, "battery_level": 100}
        ]

    def _obj_by_id(self, obj_id):
        for obj in self.equipment:
            if obj["object_id"] == obj_id:
                return obj
        return None

    def _distance_between(self, obj1, obj2):
        if "location" in obj1 and "location" in obj2:
            return abs(obj1["location"]["x"] - obj2["location"]["x"]) + abs(obj1["location"]["y"] - obj2["location"]["y"])
        return float('inf')

    def populate_distance_from_self(self):
        objs = json.loads(json.dumps(self.equipment))
        for obj in objs:
            if obj["object_id"] == self.gonky["object_id"]:
                continue
            if "location" in obj:
                obj["distance_from_self"] = self._distance_between(obj, self.gonky)
        return objs

    def charge_equipment(self, params):
        equipment_obj = self._obj_by_id(params["object_id"])
        if equipment_obj and self.gonky["battery_level"] >= 10 and self._distance_between(equipment_obj, self.gonky) <= 1:
            charge_need = 100 - equipment_obj["battery_level"]
            charge_amount = min(self.gonky["battery_level"] - 10, charge_need)
            self.gonky["battery_level"] -= charge_amount
            equipment_obj["battery_level"] += charge_amount
            return f"Charged {equipment_obj['object_id']} to {equipment_obj['battery_level']}%", False
        else:
            return "Cannot charge equipment. Either too far away or not enough battery.", False

    def recharge_self(self, params):
        power_station = self._obj_by_id("power_station_1")
        if power_station and self._distance_between(power_station, self.gonky) <= 1:
            self.gonky["battery_level"] = 100
            return "Recharged self to 100%", False
        else:
            return "Cannot recharge self. Either too far away, or unable to find power station.", False

    def move_to_location(self, params):
        self.gonky["location"]["x"] = params["x"]
        self.gonky["location"]["y"] = params["y"]
        return f"Moved to location ({self.gonky['location']['x']}, {self.gonky['location']['y']})", False

    def move_to_object(self, params):
        target_obj = self._obj_by_id(params["object_id"])
        if target_obj:
            self.gonky["location"]["x"] = target_obj["location"]["x"]
            self.gonky["location"]["y"] = target_obj["location"]["y"]
            return f"Moved to object {target_obj['object_id']} at location ({self.gonky['location']['x']}, {self.gonky['location']['y']})", False
        else:
            return f"Cannot move to object. Unable to find object {params['object_id']}.", False

    def switch_self_off(self, params):
        return "Switched self off.", True
