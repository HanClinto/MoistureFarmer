tools = [
    {
        "type":"function",
        "function":{
            "name":"charge_equipment",
            "description":"Charge the batteries of a piece of equipment. Requires the id of the equipment. Must be within 1 meter distance. Must have at least 10% charge in self to charge other equipment.",
            "parameters":{
                "type":"object",
                "properties":{
                    "object_id":{
                        "type":"string",
                        "description":"The ID of the equipment to charge. Distance away must be 1 meter or less."
                    }
                },
                "required":["object_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"recharge_self",
            "description":"Recharge your own batteries at a power station. No parameters required.",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"move_to_location",
            "description":"Move to a specific location on the farm.",
            "parameters":{
                "type":"object",
                "properties":{
                    "x":{
                        "type":"integer",
                        "description":"The x coordinate to move to."
                    },
                    "y":{
                        "type":"integer",
                        "description":"The y coordinate to move to."
                    }
                },
                "required":["x", "y"],
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"move_to_object",
            "description":"Move adjacent to the location of a specific object.",
            "parameters":{
                "type":"object",
                "properties":{
                    "object_id":{
                        "type":"string",
                        "description":"The ID of the object to move to."
                    }
                },
                "required":["object_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"switch_self_off",
            "description":"Switch yourself off. Use at the end of the day when all work is done and we're back at the power station. No parameters required.",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
                "additionalProperties": False
            }
        }    }
]
