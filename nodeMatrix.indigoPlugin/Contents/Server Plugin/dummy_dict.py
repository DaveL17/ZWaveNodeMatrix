import datetime

now = datetime.datetime.now()
REPL_DATE = (now.year, now.month, now.day)

test_file = {
    3: {
        'neighbors': [4, 5, 10, 11, 12, 15, 16, 17, 18, 25, 27, 28, 29, 30, 39, 41, 43],
        'counter': 1,
        'name': u'Master Bedroom - West Bedside Lamp',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(1970, 1, 1, 18, 56, 20),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    4: {
        'neighbors': [
            3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29, 39, 41,
            43, 44
        ],
        'counter': 2,
        'name': u'Foyer - Lamp',
        'lost': True,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 9, 41),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    5: {
        'neighbors': [
            3, 4, 8, 10, 11, 12, 13, 15, 16, 17, 18, 21, 22, 25, 27, 28, 29, 30, 39, 41, 43
        ],
        'counter': 3,
        'name': u'Outdoor - Front Porch Lights',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 21, 33),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    7: {
        'neighbors': [4, 8, 11, 12, 23, 43, 44],
        'counter': 4,
        'name': u'Outdoor - Garage Side Door Light',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 21, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    8: {
        'neighbors': [4, 5, 7, 10, 11, 12, 15, 18, 20, 21, 23, 27, 28, 30, 41, 42, 43, 44],
        'counter': 5,
        'name': u'Garage - Motion',
        'lost': False,
        'battery': True,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 18, 4, 5),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    10: {
        'neighbors': [3, 4, 5, 8, 11, 12, 15, 16, 17, 18, 21, 22, 25, 27, 28, 39, 41, 43, 44],
        'counter': 6,
        'name': u'Living Room - Outlet North',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 9, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    11: {
        'neighbors': [
            3, 4, 5, 7, 8, 10, 12, 13, 15, 16, 17, 18, 20, 21, 22, 27, 28, 29, 39, 41, 42, 43, 44
        ],
        'counter': 7,
        'name': u'Thermostat - Downstairs',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 19, 48, 16),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    12: {
        'neighbors': [
            3, 4, 5, 7, 8, 10, 11, 13, 15, 16, 18, 20, 21, 22, 23, 24, 27, 28, 39, 41, 42, 43
        ],
        'counter': 8,
        'name': u'Basement - Humidifier',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 30, 1),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    14: {
        'neighbors': [3, 4, 7, 8, 11, 12, 15, 16, 17, 20, 21, 22, 24, 27, 28, 29, 39, 41, 43, 44],
        'counter': 9,
        'name': u'Dining Room - Motion',
        'lost': False,
        'battery': True,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 2, 2),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    15: {
        'neighbors': [3, 4, 5, 8, 10, 11, 12, 16, 17, 18, 21, 22, 25, 27, 28, 29, 39, 41, 43, 44],
        'counter': 10,
        'name': u'Living Room - Desk Lamp',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 9, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    16: {
        'neighbors': [3, 4, 5, 10, 11, 12, 13, 15, 17, 18, 22, 25, 27, 28, 29, 39, 41, 43, 44],
        'counter': 11,
        'name': u'Living Room - Vase',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 9, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    17: {
        'neighbors': [3, 5, 10, 13, 15, 16, 22, 39, 41, 43],
        'counter': 12, 'name': u'Living Room - TV',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 18, 57, 33),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    18: {
        'neighbors': [3, 4, 5, 8, 10, 11, 12, 13, 15, 16, 21, 22, 27, 28, 29, 39, 41, 42, 43],
        'counter': 13,
        'name': u'Outdoor - Back Porch Light',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 21, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    20: {
        'neighbors': [8, 11, 21, 24, 43],
        'counter': 14,
        'name': u'Outdoor - Septic Pump',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 53, 28),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    21: {
        'neighbors': [5, 8, 10, 11, 12, 13, 15, 20, 22, 27, 29, 30, 41, 42, 43],
        'counter': 15,
        'name': u'Kitchen - Cabinets North',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 53, 19),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    22: {
        'neighbors': [4, 5, 10, 11, 12, 15, 16, 17, 21, 27, 28, 29, 41, 43],
        'counter': 16,
        'name': u'Kitchen - Cabinets South',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 53, 26),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    23: {
        'neighbors': [7, 8, 12, 20],
        'counter': 17,
        'name': u'Outdoor - Path Lights Rear North',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 21, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    24: {
        'neighbors': [4, 12, 13, 15, 20, 43],
        'counter': 18,
        'name': u'Outdoor - Path Lights Front North',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 21, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    25: {
        'neighbors': [3, 4, 5, 10, 15, 16, 27, 28, 29, 41, 43],
        'counter': 19,
        'name': u'Outdoor - Path Lights Front South',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 21, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    27: {
        'neighbors': [3, 4, 5, 8, 10, 11, 12, 13, 15, 16, 18, 21, 22, 25, 28, 29, 39, 41, 43],
         'counter': 20,
         'name': u'Basement - Energy Meter 1',
         'lost': False,
         'battery': False,
         'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 45, 6),
         'no_node_1': False,
         'invalid_neighbor': False
    },
    28: {
        'neighbors': [3, 4, 5, 8, 10, 11, 12, 13, 15, 16, 17, 18, 22, 25, 27, 29, 39, 41, 42, 43],
         'counter': 21,
         'name': u'Basement - Energy Meter 2',
         'lost': False, 'battery': False,
         'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 49, 23),
         'no_node_1': False,
         'invalid_neighbor': False
    },
    30: {
        'neighbors': [3, 5, 8, 13, 17, 21, 22, 28, 29, 39, 41, 43],
         'counter': 22,
         'name': u'Main Attic - Motion',
         'lost': False,
         'battery': True,
         'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 12, 52, 6),
         'no_node_1': False,
         'invalid_neighbor': False
    },
    31: {
        'neighbors': [3, 4, 5, 8, 10, 15, 16, 17, 18, 21, 22, 27, 28, 29, 30, 39, 41, 43],
        'counter': 23,
        'name': u'Outdoor - Luminance',
        'lost': False,
        'battery': True,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 42, 29),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    32: {
        'neighbors': [
            2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 15, 16, 17, 18, 21, 22, 24, 25, 26, 27, 28, 29, 30
        ],
        'counter': 24,
        'name': u'Foyer - Upstairs Smoke',
        'lost': False,
        'battery': True,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 9, 55, 55),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    33: {
        'neighbors': [
            2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27,
            28, 29, 30
        ],
        'counter': 25,
        'name': u'Foyer - Main Floor Smoke',
        'lost': False,
        'battery': True,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 16, 27, 24),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    34: {
        'neighbors': [
            2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 15, 16, 17, 18, 21, 22, 24, 25, 26, 27, 28, 29
        ],
        'counter': 26,
        'name': u'Basement - Smoke',
        'lost': False,
        'battery': True,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 4, 37, 16),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    37: {
        'neighbors': [4, 7, 8, 11, 15, 23, 43],
        'counter': 27,
        'name': u'Garage - Side Door',
        'lost': False,
        'battery': True,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 35, 24),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    38: {
        'neighbors': [
            2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29,
            30
        ],
        'counter': 28,
        'name': u'Guest Bathroom - Exhaust Fan',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 10, 18, 5),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    39: {
        'neighbors': [3, 4, 5, 10, 11, 12, 13, 15, 16, 18, 27, 28, 29, 41, 43, 44],
        'counter': 29,
        'name': u'Master Bedroom - Star Lamp',
        'lost': False, 'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 9, 34),
        'no_node_1': False,
        'invalid_neighbor': False
    }, 41: {
        'neighbors': [
            3, 4, 5, 8, 10, 11, 12, 13, 15, 16, 17, 18, 21, 22, 25, 27, 28, 29, 30, 39, 43, 44
        ],
        'counter': 30,
        'name': u'Workshop - Fibaro RGBW',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 18, 59, 23),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    42: {
        'neighbors': [8, 11, 12, 13, 21, 43],
        'counter': 31,
        'name': u'Basement - Dehumidifier',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 43, 17),
        'no_node_1': False, 'invalid_neighbor': False
    }, 43: {
        'neighbors': [
            3, 4, 5, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 24, 25, 27, 28, 29, 30, 39,
            41, 42, 44
        ],
        'counter': 32,
        'name': u'Thermostat - Upstairs',
        'lost': False,
        'battery': False,
        'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 40, 47),
        'no_node_1': False,
        'invalid_neighbor': False
    },
    44: {'neighbors': [4, 5, 7, 8, 11, 13, 15, 16, 20, 22, 39, 41, 43],
         'counter': 33,
         'name': u'Outdoor - Garage Driveway Lights',
         'lost': False,
         'battery': False,
         'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 21, 33),
         'no_node_1': False,
         'invalid_neighbor': False
         },
    45: {'neighbors': [3, 4, 13, 15, 28, 41, 43],
         'counter': 34,
         'name': u'Main Attic - Ventilation Fan',
         'lost': False,
         'battery': False,
         'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 0, 37),
         'no_node_1': False,
         'invalid_neighbor': False
         },
    46: {'neighbors': [3, 4, 16, 41, 43],
         'counter': 35,
         'name': u'Basement - Cable Modem',
         'lost': False,
         'battery': False,
         'changed': datetime.datetime(REPL_DATE[0], REPL_DATE[1], REPL_DATE[2], 20, 50, 24),
         'no_node_1': False,
         'invalid_neighbor': False
         }
}  # noqa
