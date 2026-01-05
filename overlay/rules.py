PHASE_LABELS = {
    "prep": "PREP – Vorbereitung",
    "pop": "POP – Absprung",
    "air": "AIR – Flugphase",
    "land": "LAND – Landung"
}

KNEE_ANGLE_RULES = {
    "prep": {
        "green":  (140, 180),
        "yellow": (120, 140)
    },
    "pop": {
        "green":  (150, 180),
        "yellow": (130, 150)
    },
    "air": {
        "green":  (110, 160),
        "yellow": (90, 110)
    },
    "land": {
        "green":  (130, 170),
        "yellow": (110, 130)
    }
}

JOINT_ARROW_RULES = {
    "LEFT_KNEE":  {"dx": 0,   "dy": 80,  "text": "Mehr beugen"},
    "RIGHT_KNEE": {"dx": 0,   "dy": 80,  "text": "Mehr beugen"},

    "LEFT_ELBOW":  {"dx": -80, "dy": 0,  "text": "Arm lockern"},
    "RIGHT_ELBOW": {"dx": 80,  "dy": 0,  "text": "Arm lockern"},

    "LEFT_SHOULDER":  {"dx": -60, "dy": -40, "text": "Schulter entspannen"},
    "RIGHT_SHOULDER": {"dx": 60,  "dy": -40, "text": "Schulter entspannen"},

    "LEFT_ANKLE":  {"dx": 0,   "dy": -80, "text": "Fuß aktiver"},
    "RIGHT_ANKLE": {"dx": 0,   "dy": -80, "text": "Fuß aktiver"},
}


