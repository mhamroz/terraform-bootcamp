class Rule:
    id = "101"
    description = "Verify Inventory references in underlay.yaml"
    severity = "HIGH"

    @classmethod
    def match(cls, data):
        results = []
        keys = []
        for obj in data["fabric"]["inventory"]:
            names = data["fabric"]["inventory"][obj]
            for name in names:
                keys.append(name['name'])

        refs_list = ['loopbacks','ethernets']
        underlay = data["fabric"]["underlay"]
        for v in underlay:
            if v in refs_list:
                for dev in underlay[v]:
                    if dev['device'] not in keys:
                        results.append(f"device {dev['device']} not found in inventory.yaml")
        return results
