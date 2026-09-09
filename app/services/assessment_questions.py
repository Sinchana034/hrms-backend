QUESTION_BANK = {
    "python": [
        {
            "question": "Which keyword is used to define a function in Python?",
            "options": [
                "function",
                "def",
                "func",
                "define"
            ],
            "answer": "def",
        },
        {
            "question": "Which data type is immutable in Python?",
            "options": [
                "List",
                "Dictionary",
                "Set",
                "Tuple"
            ],
            "answer": "Tuple",
        },
        {
            "question": "What does len() return?",
            "options": [
                "The memory size",
                "The number of elements",
                "The data type",
                "The index"
            ],
            "answer": "The number of elements",
        },
        {
            "question": "Which keyword is used to handle exceptions?",
            "options": [
                "catch",
                "error",
                "try",
                "excepted"
            ],
            "answer": "try",
        },
    ],

    "django": [
        {
            "question": "Which file normally contains Django project settings?",
            "options": [
                "models.py",
                "views.py",
                "settings.py",
                "urls.html"
            ],
            "answer": "settings.py",
        },
        {
            "question": "Which command starts the Django development server?",
            "options": [
                "django start",
                "python manage.py runserver",
                "django server",
                "python django start"
            ],
            "answer": "python manage.py runserver",
        },
        {
            "question": "Which Django component is used to define database structure?",
            "options": [
                "Views",
                "Models",
                "Templates",
                "URLs"
            ],
            "answer": "Models",
        },
    ],

    "fastapi": [
        {
            "question": "Which Python framework is used to build FastAPI applications?",
            "options": [
                "FastAPI",
                "Flask",
                "Django",
                "FastAPI is a Python framework"
            ],
            "answer": "FastAPI is a Python framework",
        },
        {
            "question": "Which HTTP method is commonly used to create a resource?",
            "options": [
                "GET",
                "POST",
                "DELETE",
                "HEAD"
            ],
            "answer": "POST",
        },
    ],

    "sql": [
        {
            "question": "Which SQL command is used to retrieve data?",
            "options": [
                "GET",
                "SELECT",
                "FETCH DATA",
                "READ"
            ],
            "answer": "SELECT",
        },
        {
            "question": "Which clause is used to filter rows?",
            "options": [
                "ORDER BY",
                "GROUP BY",
                "WHERE",
                "FILTER"
            ],
            "answer": "WHERE",
        },
        {
            "question": "Which SQL command is used to modify existing records?",
            "options": [
                "CHANGE",
                "MODIFY",
                "UPDATE",
                "EDIT"
            ],
            "answer": "UPDATE",
        },
    ],

    "git": [
        {
            "question": "Which command creates a new Git repository?",
            "options": [
                "git create",
                "git init",
                "git new",
                "git start"
            ],
            "answer": "git init",
        },
        {
            "question": "Which command uploads local commits to a remote repository?",
            "options": [
                "git upload",
                "git send",
                "git push",
                "git commit"
            ],
            "answer": "git push",
        },
    ],

    "javascript": [
        {
            "question": "Which keyword declares a block-scoped variable that can be reassigned?",
            "options": [
                "var",
                "let",
                "const",
                "define"
            ],
            "answer": "let",
        },
        {
            "question": "Which method converts JSON text into a JavaScript object?",
            "options": [
                "JSON.parse()",
                "JSON.object()",
                "JSON.convert()",
                "JSON.toObject()"
            ],
            "answer": "JSON.parse()",
        },
    ],

    "react": [
        {
            "question": "Which hook is used to manage state in a React function component?",
            "options": [
                "useEffect",
                "useState",
                "useContext",
                "useRef"
            ],
            "answer": "useState",
        },
        {
            "question": "Which prop is commonly used to uniquely identify items rendered in a React list?",
            "options": [
                "id",
                "index",
                "key",
                "unique"
            ],
            "answer": "key",
        },
    ],

    "angular": [
        {
            "question": "Which language is primarily used to develop Angular applications?",
            "options": [
                "Python",
                "Java",
                "TypeScript",
                "C++"
            ],
            "answer": "TypeScript",
        },
        {
            "question": "Which decorator is used to define an Angular component?",
            "options": [
                "@Component",
                "@Service",
                "@Angular",
                "@Module"
            ],
            "answer": "@Component",
        },
    ],
}


def normalize_skill(skill):
    """
    Normalize a skill name so that
    Python, python, and PYTHON are treated the same.
    """
    return str(skill).strip().lower()


def select_questions(skills):
    """
    Select assessment questions based on candidate skills.
    """

    questions = []

    for skill in skills:
        normalized_skill = normalize_skill(skill)

        if normalized_skill in QUESTION_BANK:
            questions.extend(QUESTION_BANK[normalized_skill])

    return questions