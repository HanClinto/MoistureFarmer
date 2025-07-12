document.addEventListener('DOMContentLoaded', function () {
    // Loop through all elements and find those with the 'draggable' class
    const draggableElements = document.querySelectorAll('.draggable');
    draggableElements.forEach(el => draggableElement(el));

    // Loop through all elements and ensure all windows are bringable to the front
    const windows = document.querySelectorAll('.window');
    windows.forEach(el => bringableToFront(el));

    // Loop through all elements and find those with the 'resizeable' class
    const resizeableElements = document.querySelectorAll('.resizeable');
    resizeableElements.forEach(el => resizeableElement(el));

//    dragElement(document.getElementById('main-window'));
//    resizeElement(document.getElementById('main-window'));

    test_json = {
  "entities": {
    "GX1_Vaporator_1": {
      "id": "GX1_Vaporator_1",
      "type": "GX1_Vaporator",
      "logs": [],
      "name": null,
      "description": "A device used to extract moisture from the air, typically used in arid environments.",
      "location": {
        "x": 0,
        "y": 0
      },
      "model": "GX-1",
      "health": 100,
      "slots": {
        "power_pack": {
          "accepts": "PowerPack",
          "component": {
            "id": "SmallPowerPack_1",
            "type": "SmallPowerPack",
            "logs": [
              {
                "msg": "Component SmallPowerPack_1 installed in chassis GX1_Vaporator_1.",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909033"
              }
            ],
            "name": null,
            "description": null,
            "durability": 100
          }
        },
        "condenser": {
          "accepts": "CondenserUnit",
          "component": {
            "id": "CondenserUnit_1",
            "type": "CondenserUnit",
            "logs": [
              {
                "msg": "Component CondenserUnit_1 installed in chassis GX1_Vaporator_1.",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909121"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909321"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909368"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909440"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909504"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909547"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909585"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909622"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909657"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909698"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909735"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909770"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909805"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909840"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909879"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909921"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909956"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909991"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910025"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910058"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910091"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910124"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910157"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910190"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910222"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910255"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910288"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910320"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910353"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910385"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910418"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910451"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910483"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910516"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910552"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910585"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910618"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910651"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910684"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910716"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910749"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910781"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910814"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910846"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910879"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910912"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910944"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.910977"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911010"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911049"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911080"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911111"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911121"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911147"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911156"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911181"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911191"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911216"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911226"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911251"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911261"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911286"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911296"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911322"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911331"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911356"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911366"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911391"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911400"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911425"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911434"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911459"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911468"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911493"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911503"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911528"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911537"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911562"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911572"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911597"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911606"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911631"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911640"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911665"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911675"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911699"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911709"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911734"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911743"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911769"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911778"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911804"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911819"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911846"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911856"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911882"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911892"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911918"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911928"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911953"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.911963"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.911988"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912001"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912027"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912037"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912063"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912073"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912100"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912110"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912137"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912146"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912172"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912181"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912208"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912217"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912249"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912258"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912285"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912295"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912321"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912330"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912356"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912365"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912390"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912399"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912426"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912435"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912460"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912470"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912498"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912507"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912533"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912543"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912569"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912583"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912610"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912619"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912646"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912656"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912682"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912692"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912717"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912727"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912751"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912761"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912786"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912795"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912820"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912829"
              },
              {
                "msg": "Tick: 1 water per charge",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.912854"
              },
              {
                "msg": "Water tank is full. CondenserUnit cannot condense more water.",
                "level": 1,
                "timestamp": "2025-07-12T03:02:55.912864"
              }
            ],
            "name": null,
            "description": null,
            "durability": 100
          }
        },
        "water_tank": {
          "accepts": "WaterTank",
          "component": {
            "id": "SmallWaterTank_1",
            "type": "SmallWaterTank",
            "logs": [
              {
                "msg": "Component SmallWaterTank_1 installed in chassis GX1_Vaporator_1.",
                "level": 0,
                "timestamp": "2025-07-12T03:02:55.909141"
              }
            ],
            "name": null,
            "description": null,
            "durability": 100
          }
        }
      }
    }
  }
}

    const html = jsonToHtml(test_json, 'Entities', 'entities');
    const windowBodyEntities = document.getElementById('window-body-entities');
    windowBodyEntities.innerHTML = html;

});

function jsonToHtml(json, title, id_path, depth = 0) {
// Take JSON data and convert it to HTML in the following format:

/* Output style:
<ul class="tree-view">
  <li>Table of Contents</li>
  <li>What is web development?</li>
  <li>
    CSS
    <ul>
      <li>Selectors</li>
      <li>Specificity</li>
      <li>Properties</li>
    </ul>
  </li>
  <li>
    <details open>
      <summary>JavaScript</summary>
      <ul>
        <li>Avoid at all costs</li>
        <li>
          <details>
            <summary>Unless</summary>
            <ul>
              <li>Avoid</li>
              <li>
                <details>
                  <summary>At</summary>
                  <ul>
                    <li>Avoid</li>
                    <li>At</li>
                    <li>All</li>
                    <li>Cost</li>
                  </ul>
                </details>
              </li>
              <li>All</li>
              <li>Cost</li>
            </ul>
          </details>
        </li>
      </ul>
    </details>
  </li>
  <li>HTML</li>
  <li>Special Thanks</li>
</ul>
*/

    // If a value is an object or an array, it should be displayed as a nested list
    // If a nested list has more than two items, it should be displayed as a details element with a summary
    // If a value is a string or number, it should be displayed as a list item with the key and value
    // If a value is a boolean, it should be displayed as a list item with the key and value
    let added_details = false;
    let html = '';
    if (json && (typeof json === 'object' || Array.isArray(json))) {
        added_details = true;
        html += '<details><summary>' + title + '</summary>';
    }
    html += depth === 0 ? '<ul class="tree-view">' : '<ul>';
    for (const key in json) {
        if (json.hasOwnProperty(key)) {
            if (typeof json[key] === 'object' || Array.isArray(json[key])) {
                html += `<li id="${id_path + '.' + key}">${jsonToHtml(json[key], key, id_path + '.' + key, depth + 1)}</li>`;
            } else {
                html += `<li id="${id_path + '.' + key}">${key}: ${json[key]}</li>`;
            }
        }
    }
    html += '</ul>';
    if (added_details) {
        html += '</details>';
    }
    return html;
}