QUERY = "QUERY"
TIME = "TIME"
ENTITY = "ENTITY"
LOCATION = "LOCATION"
WHO = "WHO"
COURSE = "COURSE"
DONE = ["Finished!", "Done!", "Okay. Done.", "Dunzo!", "Dont worry about it!"]
VIEW_ALL = """
    #####################################
    _SUBJECT_ => *{subject}*
    _TOTAL LECTS_ => *{totalLects}*
    _PRESENT_ => *{present}*
    _ABS_ => *{abs}*
    _LOA_ => *{loa}*
    -------------------------------------
    ATTENDANCE => *{attendance}*
    -------------------------------------
    #####################################
"""

CURRENT_CLASS = "Your *{course}* class is going on till *{finish}*."
NEXT_CLASS = "Your next class is *{course}* at *{start}*."


NOT_FOUND = [
    "Sorry that didn't work",
    "Please try again",
    "Oops that's a 404"
]

ATTENDANCE = [
    "Your attendance is {}%",
    "That's gonna be {}%",
    "It's {}%",
    "Found it, {}%"
]

TRAIN_DATA = [
    (
        "Where is my next class?",
        {"entities": [
            (0, 5, QUERY),
            (12, 16, TIME),
            (17, 22, ENTITY)
        ]},
    ),
    (
        "When is my next class?",
        {"entities": [
            (0, 4, QUERY),
            (11, 15, TIME),
            (16, 21, ENTITY)
        ]},
    ),
    (
        "Find my next class?",
        {"entities": [
            (0, 4, QUERY),
            (8, 12, TIME),
            (13, 18, ENTITY)
        ]},
    ),
    (
        "When is my R Programming class?",
        {"entities": [
            (0, 4, QUERY),
            (11, 24, COURSE),
            (25, 30, ENTITY)
        ]},
    ),
    (
        "Which class is at 11am?",
        {"entities": [
            (0, 5, QUERY),
            (6, 11, ENTITY),
            (18, 22, TIME)
        ]},
    ),
    (
        "What is my attendace in Secure Coding?",
        {"entities": [
            (0, 4, QUERY),
            (11, 20, ENTITY),
            (24, 37, COURSE)
        ]},
    ),
    (
        "What is my attendace in R Programming?",
        {"entities": [
            (0, 4, QUERY),
            (11, 20, ENTITY),
            (24, 37, COURSE)
        ]},
    ),
    (
        "When is my Java class?",
        {"entities": [
            (0, 4, QUERY),
            (11, 15, COURSE),
            (16, 21, ENTITY)
        ]},
    ),
    (
        "Which class at 12.30pm?",
        {"entities": [
            (0, 5, QUERY),
            (6, 11, ENTITY),
            (15, 22, TIME)
        ]},
    ),
    (
        "Attendace in R Programming?",
        {"entities": [
            (0, 9, ENTITY),
            (13, 26, COURSE)
        ]},
    ),
    (
        "Attendace of Java?",
        {"entities": [
            (0, 9, ENTITY),
            (13, 17, COURSE)
        ]},
    ),
    (
        "What is my attendace in Python?",
        {"entities": [
            (0, 4, QUERY),
            (11, 20, ENTITY),
            (24, 30, COURSE)
        ]},
    ),
    (
        "What is my attendace in C?",
        {"entities": [
            (0, 4, QUERY),
            (11, 20, ENTITY),
            (24, 25, COURSE)
        ]},
    ),
    (
        "What is my attendace in C++?",
        {"entities": [
            (0, 4, QUERY),
            (11, 20, ENTITY),
            (24, 27, COURSE)
        ]},
    ),
    (
        "What is my attendace in CPP",
        {"entities": [
            (0, 4, QUERY),
            (11, 20, ENTITY),
            (24, 30, COURSE)
        ]},
    ),
    (
        "What is my attendace in C",
        {"entities": [
            (0, 4, QUERY),
            (11, 20, ENTITY),
            (24, 25, COURSE)
        ]},
    ),
    (
        "What is my attendace in C++",
        {"entities": [
            (0, 4, QUERY),
            (11, 20, ENTITY),
            (24, 27, COURSE)
        ]},
    ),
    (
        "Show me past year papers",
        {"entities": [
            (0, 4, QUERY),
            (8, 17, TIME),
            (18, 24, ENTITY)
        ]},
    ),
    (
        "Past year paper of R Programming",
        {"entities": [
            (0, 9, TIME),
            (10, 15, ENTITY),
            (19, 32, COURSE)
        ]},
    ),
    (
        "when is Secure Coding class",
        {"entities": [
            (0, 4, QUERY),
            (8, 21, COURSE),
            (22, 27, ENTITY)
        ]},
    ),
    (
        "Past year paper of Java",
        {"entities": [
            (0, 9, TIME),
            (10, 15, ENTITY),
            (19, 23, COURSE)
        ]},
    ),
    (
        "Past year paper of Python course",
        {"entities": [
            (0, 9, TIME),
            (10, 15, ENTITY),
            (19, 32, COURSE)
        ]},
    ),
    (
        "pyp of Java",
        {"entities": [
            (0, 3, ENTITY),
            (7, 11, COURSE)
        ]},
    ),
    (
        "pyp of C",
        {"entities": [
            (0, 3, ENTITY),
            (7, 8, COURSE)
        ]},
    ),
    (
        "pyp of R Programming",
        {"entities": [
            (0, 3, ENTITY),
            (7, 20, COURSE)
        ]},
    )
]
