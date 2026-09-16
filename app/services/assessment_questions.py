import random


QUESTION_BANK = {

    # =========================================================
    # PYTHON — 20 QUESTIONS
    # =========================================================

    "python": [

        {
            "question": "Which keyword is used to define a function in Python?",
            "options": ["function", "def", "func", "define"],
            "answer": "def",
        },
        {
            "question": "Which data type is immutable in Python?",
            "options": ["List", "Dictionary", "Set", "Tuple"],
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
            "options": ["catch", "error", "try", "excepted"],
            "answer": "try",
        },
        {
            "question": "What is the output of len([10, 20, 30])?",
            "options": ["2", "3", "4", "0"],
            "answer": "3",
        },
        {
            "question": "Which symbol is used to create a comment in Python?",
            "options": ["//", "/*", "#", "--"],
            "answer": "#",
        },
        {
            "question": "Which Python data structure stores key-value pairs?",
            "options": ["List", "Tuple", "Dictionary", "Set"],
            "answer": "Dictionary",
        },
        {
            "question": "What is the purpose of a Python virtual environment?",
            "options": [
                "To execute JavaScript",
                "To isolate project dependencies",
                "To increase internet speed",
                "To compile Python into Java"
            ],
            "answer": "To isolate project dependencies",
        },
        {
            "question": "Which keyword is used to create a class in Python?",
            "options": ["object", "class", "struct", "define"],
            "answer": "class",
        },
        {
            "question": "What does the __init__ method typically do in a Python class?",
            "options": [
                "Deletes an object",
                "Initializes an object",
                "Imports a module",
                "Starts a server"
            ],
            "answer": "Initializes an object",
        },
        {
            "question": "Which collection type does not allow duplicate elements?",
            "options": ["List", "Tuple", "Set", "Dictionary"],
            "answer": "Set",
        },
        {
            "question": "Which keyword is used to return a value from a function?",
            "options": ["send", "return", "output", "yield"],
            "answer": "return",
        },
        {
            "question": "What is a list comprehension used for?",
            "options": [
                "Creating lists concisely",
                "Creating database tables",
                "Handling exceptions only",
                "Defining classes"
            ],
            "answer": "Creating lists concisely",
        },
        {
            "question": "What is the output of `3 == 3.0` in Python?",
            "options": ["True", "False", "Error", "None"],
            "answer": "True",
        },
        {
            "question": "Which keyword is used to create a generator function?",
            "options": ["generate", "yield", "generator", "return"],
            "answer": "yield",
        },
        {
            "question": "What does `*args` allow a function to accept?",
            "options": [
                "Multiple positional arguments",
                "Only one argument",
                "Only keyword arguments",
                "Only strings"
            ],
            "answer": "Multiple positional arguments",
        },
        {
            "question": "What does `**kwargs` allow a function to accept?",
            "options": [
                "Multiple positional arguments",
                "Multiple keyword arguments",
                "Only integers",
                "Only lists"
            ],
            "answer": "Multiple keyword arguments",
        },
        {
            "question": "Which keyword is used to import a module?",
            "options": ["include", "require", "import", "using"],
            "answer": "import",
        },
        {
            "question": "What is inheritance in Python?",
            "options": [
                "A class acquiring properties and methods from another class",
                "Deleting a class",
                "Converting Python to Java",
                "Creating a database"
            ],
            "answer": "A class acquiring properties and methods from another class",
        },
        {
            "question": "Which Python library is commonly used for working with JSON?",
            "options": ["json", "jsonlib", "pyjsonx", "datajson"],
            "answer": "json",
        },
    ],


    # =========================================================
    # DJANGO — 20 QUESTIONS
    # =========================================================

    "django": [

        {
            "question": "Which file normally contains Django project settings?",
            "options": ["models.py", "views.py", "settings.py", "urls.html"],
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
            "options": ["Views", "Models", "Templates", "URLs"],
            "answer": "Models",
        },
        {
            "question": "Which command creates database migration files?",
            "options": [
                "python manage.py migrate",
                "python manage.py makemigrations",
                "django make migration",
                "python manage.py database"
            ],
            "answer": "python manage.py makemigrations",
        },
        {
            "question": "Which command applies Django migrations to the database?",
            "options": [
                "python manage.py migrate",
                "python manage.py apply",
                "python manage.py makemigrations",
                "django migrate-db"
            ],
            "answer": "python manage.py migrate",
        },
        {
            "question": "Which Django file commonly defines URL routes?",
            "options": ["models.py", "views.py", "urls.py", "admin.py"],
            "answer": "urls.py",
        },
        {
            "question": "What is Django ORM used for?",
            "options": [
                "Creating CSS",
                "Interacting with databases using Python objects",
                "Managing Git repositories",
                "Creating JavaScript bundles"
            ],
            "answer": "Interacting with databases using Python objects",
        },
        {
            "question": "Which decorator can restrict a Django view to authenticated users?",
            "options": [
                "@login_required",
                "@authenticated_only",
                "@user_required",
                "@auth"
            ],
            "answer": "@login_required",
        },
        {
            "question": "Which Django component handles HTTP requests and returns responses?",
            "options": ["Models", "Views", "Migrations", "Admin"],
            "answer": "Views",
        },
        {
            "question": "Which command opens the Django interactive shell?",
            "options": [
                "python manage.py shell",
                "python manage.py console",
                "django shell",
                "python django shell"
            ],
            "answer": "python manage.py shell",
        },
        {
            "question": "Which file is commonly used to register models with Django admin?",
            "options": ["admin.py", "register.py", "models_admin.py", "dashboard.py"],
            "answer": "admin.py",
        },
        {
            "question": "Which Django feature is commonly used to protect against CSRF attacks?",
            "options": [
                "CSRF middleware and tokens",
                "SQL joins",
                "Git hooks",
                "URL namespaces"
            ],
            "answer": "CSRF middleware and tokens",
        },
        {
            "question": "What does a ForeignKey represent in a Django model?",
            "options": [
                "A one-to-many relationship",
                "A CSS class",
                "A Python function",
                "A database backup"
            ],
            "answer": "A one-to-many relationship",
        },
        {
            "question": "What does `__str__()` commonly define in a Django model?",
            "options": [
                "The object's human-readable string representation",
                "A database migration",
                "A URL route",
                "A template"
            ],
            "answer": "The object's human-readable string representation",
        },
        {
            "question": "Which Django command collects static files for deployment?",
            "options": [
                "python manage.py collectstatic",
                "python manage.py static",
                "django collect",
                "python manage.py assets"
            ],
            "answer": "python manage.py collectstatic",
        },
        {
            "question": "What is a Django template primarily used for?",
            "options": [
                "Generating HTML dynamically",
                "Creating database indexes",
                "Managing Git branches",
                "Running migrations"
            ],
            "answer": "Generating HTML dynamically",
        },
        {
            "question": "Which Django component provides reusable application configuration?",
            "options": ["AppConfig", "AppSettings", "DjangoConfig", "ProjectConfig"],
            "answer": "AppConfig",
        },
        {
            "question": "Which HTTP status code commonly represents a successful Django response?",
            "options": ["200", "301", "404", "500"],
            "answer": "200",
        },
        {
            "question": "What is the purpose of Django middleware?",
            "options": [
                "Process requests and responses globally",
                "Create database tables only",
                "Compile JavaScript",
                "Manage Git repositories"
            ],
            "answer": "Process requests and responses globally",
        },
        {
            "question": "Which Django ORM method is commonly used to retrieve one object matching a condition?",
            "options": ["filter()", "get()", "find()", "one()"],
            "answer": "get()",
        },
    ],


    # =========================================================
    # FASTAPI — 20 QUESTIONS
    # =========================================================

    "fastapi": [

        {
            "question": "What is FastAPI?",
            "options": [
                "A Python web framework",
                "A database",
                "A JavaScript library",
                "A Linux distribution"
            ],
            "answer": "A Python web framework",
        },
        {
            "question": "Which HTTP method is commonly used to create a resource?",
            "options": ["GET", "POST", "DELETE", "HEAD"],
            "answer": "POST",
        },
        {
            "question": "Which library does FastAPI commonly use for data validation?",
            "options": ["Pydantic", "NumPy", "Pandas", "Matplotlib"],
            "answer": "Pydantic",
        },
        {
            "question": "Which command commonly starts a FastAPI application using Uvicorn?",
            "options": [
                "uvicorn main:app --reload",
                "fastapi start",
                "python fastapi server",
                "fastapi runserver"
            ],
            "answer": "uvicorn main:app --reload",
        },
        {
            "question": "Which decorator is commonly used for a GET endpoint in FastAPI?",
            "options": [
                "@app.get()",
                "@app.fetch()",
                "@get.route()",
                "@route.get()"
            ],
            "answer": "@app.get()",
        },
        {
            "question": "Which HTTP status code usually represents a successful request?",
            "options": ["200", "404", "500", "401"],
            "answer": "200",
        },
        {
            "question": "Which HTTP status code indicates that a requested resource was not found?",
            "options": ["200", "201", "404", "500"],
            "answer": "404",
        },
        {
            "question": "How can FastAPI automatically provide interactive API documentation?",
            "options": [
                "Using built-in OpenAPI support",
                "Using Git",
                "Using NumPy",
                "Using Docker only"
            ],
            "answer": "Using built-in OpenAPI support",
        },
        {
            "question": "Which keyword is commonly used for asynchronous FastAPI endpoint functions?",
            "options": ["async", "awaited", "future", "thread"],
            "answer": "async",
        },
        {
            "question": "Which HTTP method is commonly used to partially update a resource?",
            "options": ["GET", "PATCH", "HEAD", "OPTIONS"],
            "answer": "PATCH",
        },
        {
            "question": "Which decorator is commonly used to define a POST endpoint?",
            "options": ["@app.post()", "@app.create()", "@post()", "@api.postroute()"],
            "answer": "@app.post()",
        },
        {
            "question": "Which class is commonly used to define request schemas in FastAPI?",
            "options": ["Pydantic BaseModel", "FastModel", "RequestSchema", "APIModel"],
            "answer": "Pydantic BaseModel",
        },
        {
            "question": "Which FastAPI feature is used to inject dependencies into endpoints?",
            "options": ["Depends", "Inject", "Provide", "Dependency"],
            "answer": "Depends",
        },
        {
            "question": "Which HTTP status code commonly represents an unauthorized request?",
            "options": ["200", "401", "403", "500"],
            "answer": "401",
        },
        {
            "question": "Which HTTP status code commonly represents a forbidden request?",
            "options": ["401", "403", "404", "201"],
            "answer": "403",
        },
        {
            "question": "What is `response_model` used for in FastAPI?",
            "options": [
                "Defining and validating the response schema",
                "Starting the server",
                "Creating a database",
                "Encrypting passwords"
            ],
            "answer": "Defining and validating the response schema",
        },
        {
            "question": "Which HTTP method is normally used to retrieve data?",
            "options": ["GET", "POST", "PUT", "DELETE"],
            "answer": "GET",
        },
        {
            "question": "Which HTTP method is commonly used to completely replace a resource?",
            "options": ["PUT", "GET", "PATCH", "HEAD"],
            "answer": "PUT",
        },
        {
            "question": "What does `HTTPException` allow a FastAPI endpoint to do?",
            "options": [
                "Return an HTTP error response",
                "Create a database table",
                "Start Uvicorn",
                "Install packages"
            ],
            "answer": "Return an HTTP error response",
        },
        {
            "question": "Which documentation interface is commonly available at `/docs` in FastAPI?",
            "options": ["Swagger UI", "Django Admin", "React DevTools", "Jupyter"],
            "answer": "Swagger UI",
        },
    ],


    # =========================================================
    # SQL — 20 QUESTIONS
    # =========================================================

    "sql": [

        {
            "question": "Which SQL command is used to retrieve data?",
            "options": ["GET", "SELECT", "FETCH DATA", "READ"],
            "answer": "SELECT",
        },
        {
            "question": "Which clause is used to filter rows?",
            "options": ["ORDER BY", "GROUP BY", "WHERE", "FILTER"],
            "answer": "WHERE",
        },
        {
            "question": "Which SQL command is used to modify existing records?",
            "options": ["CHANGE", "MODIFY", "UPDATE", "EDIT"],
            "answer": "UPDATE",
        },
        {
            "question": "Which SQL command is used to add a new record?",
            "options": ["ADD", "INSERT", "CREATE", "APPEND"],
            "answer": "INSERT",
        },
        {
            "question": "Which SQL command removes records from a table?",
            "options": ["REMOVE", "DELETE", "DROP", "CLEAR"],
            "answer": "DELETE",
        },
        {
            "question": "Which clause is used to sort query results?",
            "options": ["SORT BY", "ORDER BY", "GROUP BY", "ARRANGE"],
            "answer": "ORDER BY",
        },
        {
            "question": "Which SQL function counts rows?",
            "options": ["SUM()", "COUNT()", "TOTAL()", "ROWS()"],
            "answer": "COUNT()",
        },
        {
            "question": "Which keyword removes duplicate results?",
            "options": ["UNIQUE", "DISTINCT", "REMOVE DUPLICATES", "SINGLE"],
            "answer": "DISTINCT",
        },
        {
            "question": "Which SQL operation combines rows from related tables?",
            "options": ["JOIN", "MERGE ROW", "CONNECT", "LINK"],
            "answer": "JOIN",
        },
        {
            "question": "Which constraint uniquely identifies each row in a table?",
            "options": ["FOREIGN KEY", "PRIMARY KEY", "UNIQUE ROW", "INDEX KEY"],
            "answer": "PRIMARY KEY",
        },
        {
            "question": "Which clause groups rows with the same values?",
            "options": ["GROUP BY", "ORDER BY", "WHERE", "COLLECT BY"],
            "answer": "GROUP BY",
        },
        {
            "question": "Which clause filters grouped results?",
            "options": ["WHERE", "HAVING", "FILTER GROUP", "GROUP WHERE"],
            "answer": "HAVING",
        },
        {
            "question": "Which SQL command creates a table?",
            "options": ["MAKE TABLE", "CREATE TABLE", "NEW TABLE", "ADD TABLE"],
            "answer": "CREATE TABLE",
        },
        {
            "question": "What is a foreign key used for?",
            "options": [
                "Linking related tables",
                "Sorting rows",
                "Deleting duplicates",
                "Encrypting data"
            ],
            "answer": "Linking related tables",
        },
        {
            "question": "Which JOIN returns matching rows from both tables?",
            "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"],
            "answer": "INNER JOIN",
        },
        {
            "question": "Which function calculates the total of numeric values?",
            "options": ["COUNT()", "SUM()", "TOTAL_ROWS()", "ADD()"],
            "answer": "SUM()",
        },
        {
            "question": "Which function calculates the average of numeric values?",
            "options": ["AVG()", "MEAN()", "AVERAGE()", "MID()"],
            "answer": "AVG()",
        },
        {
            "question": "What is an SQL index mainly used for?",
            "options": [
                "Improving query lookup performance",
                "Deleting rows",
                "Creating passwords",
                "Formatting output"
            ],
            "answer": "Improving query lookup performance",
        },
        {
            "question": "Which command permanently removes a table and its structure?",
            "options": ["DELETE TABLE", "DROP TABLE", "REMOVE TABLE", "CLEAR TABLE"],
            "answer": "DROP TABLE",
        },
        {
            "question": "Which operator is commonly used for pattern matching in SQL?",
            "options": ["LIKE", "MATCHES", "PATTERN", "SEARCH"],
            "answer": "LIKE",
        },
    ],


    # =========================================================
    # GIT — 20 QUESTIONS
    # =========================================================

    "git": [

        {
            "question": "Which command creates a new Git repository?",
            "options": ["git create", "git init", "git new", "git start"],
            "answer": "git init",
        },
        {
            "question": "Which command uploads local commits to a remote repository?",
            "options": ["git upload", "git send", "git push", "git commit"],
            "answer": "git push",
        },
        {
            "question": "Which command downloads changes from a remote repository and merges them?",
            "options": ["git pull", "git download", "git fetch-all", "git sync"],
            "answer": "git pull",
        },
        {
            "question": "Which command records staged changes in Git?",
            "options": ["git save", "git commit", "git record", "git store"],
            "answer": "git commit",
        },
        {
            "question": "Which command shows the current working tree status?",
            "options": ["git check", "git status", "git state", "git info"],
            "answer": "git status",
        },
        {
            "question": "Which command creates a new branch?",
            "options": [
                "git branch branch-name",
                "git new branch-name",
                "git create branch-name",
                "git make branch-name"
            ],
            "answer": "git branch branch-name",
        },
        {
            "question": "Which command switches to another Git branch?",
            "options": [
                "git switch branch-name",
                "git move branch-name",
                "git change branch-name",
                "git select branch-name"
            ],
            "answer": "git switch branch-name",
        },
        {
            "question": "Which command displays the commit history?",
            "options": ["git history", "git commits", "git log", "git timeline"],
            "answer": "git log",
        },
        {
            "question": "What is a Git branch mainly used for?",
            "options": [
                "Separating development work",
                "Deleting repositories",
                "Installing packages",
                "Creating databases"
            ],
            "answer": "Separating development work",
        },
        {
            "question": "Which command stages a specific file?",
            "options": ["git stage file", "git add file", "git commit file", "git prepare file"],
            "answer": "git add file",
        },
        {
            "question": "Which command downloads remote changes without merging them?",
            "options": ["git fetch", "git pull", "git download", "git remote"],
            "answer": "git fetch",
        },
        {
            "question": "Which command shows differences between files or commits?",
            "options": ["git compare", "git diff", "git difference", "git changes"],
            "answer": "git diff",
        },
        {
            "question": "Which command can be used to combine one branch into another?",
            "options": ["git join", "git merge", "git combine", "git attach"],
            "answer": "git merge",
        },
        {
            "question": "What is a merge conflict?",
            "options": [
                "When Git cannot automatically combine changes",
                "When GitHub is offline",
                "When a repository is deleted",
                "When a branch is renamed"
            ],
            "answer": "When Git cannot automatically combine changes",
        },
        {
            "question": "Which command creates a copy of a remote repository locally?",
            "options": ["git copy", "git clone", "git download-repo", "git fork"],
            "answer": "git clone",
        },
        {
            "question": "Which command can undo the latest commit while keeping changes staged?",
            "options": ["git reset --soft HEAD~1", "git delete", "git remove HEAD", "git undo"],
            "answer": "git reset --soft HEAD~1",
        },
        {
            "question": "What is `.gitignore` used for?",
            "options": [
                "Specifying files Git should ignore",
                "Deleting Git history",
                "Creating branches",
                "Connecting to GitHub"
            ],
            "answer": "Specifying files Git should ignore",
        },
        {
            "question": "What does `git remote -v` show?",
            "options": [
                "Remote repository URLs",
                "Local branches only",
                "Commit history",
                "Untracked files"
            ],
            "answer": "Remote repository URLs",
        },
        {
            "question": "Which command lists local Git branches?",
            "options": ["git branch", "git branches --all-only", "git list", "git show-branches"],
            "answer": "git branch",
        },
        {
            "question": "What is a Git commit?",
            "options": [
                "A saved snapshot of changes",
                "A remote server",
                "A branch name",
                "A database table"
            ],
            "answer": "A saved snapshot of changes",
        },
    ],


    # =========================================================
    # JAVASCRIPT — 20 QUESTIONS
    # =========================================================

    "javascript": [

        {
            "question": "Which keyword declares a block-scoped variable that can be reassigned?",
            "options": ["var", "let", "const", "define"],
            "answer": "let",
        },
        {
            "question": "Which method converts JSON text into a JavaScript object?",
            "options": ["JSON.parse()", "JSON.object()", "JSON.convert()", "JSON.toObject()"],
            "answer": "JSON.parse()",
        },
        {
            "question": "Which keyword declares a variable that cannot be reassigned?",
            "options": ["var", "let", "const", "static"],
            "answer": "const",
        },
        {
            "question": "Which method creates a new array by transforming each element?",
            "options": ["filter()", "map()", "find()", "reduceOnly()"],
            "answer": "map()",
        },
        {
            "question": "Which method returns elements that satisfy a condition?",
            "options": ["map()", "filter()", "push()", "join()"],
            "answer": "filter()",
        },
        {
            "question": "Which operator checks both value and type equality?",
            "options": ["=", "==", "===", "!="],
            "answer": "===",
        },
        {
            "question": "Which method adds an element to the end of an array?",
            "options": ["append()", "push()", "add()", "insert()"],
            "answer": "push()",
        },
        {
            "question": "What does typeof return?",
            "options": [
                "The value",
                "The data type as a string",
                "The variable name",
                "The memory address"
            ],
            "answer": "The data type as a string",
        },
        {
            "question": "Which keyword is used to define a JavaScript function?",
            "options": ["function", "def", "func", "method"],
            "answer": "function",
        },
        {
            "question": "Which JavaScript feature is commonly used to handle asynchronous operations?",
            "options": ["Promises", "Pointers", "Structs", "Header files"],
            "answer": "Promises",
        },
        {
            "question": "Which method removes the last element from an array?",
            "options": ["pop()", "remove()", "deleteLast()", "shiftLast()"],
            "answer": "pop()",
        },
        {
            "question": "Which method removes the first element from an array?",
            "options": ["shift()", "pop()", "removeFirst()", "delete()"],
            "answer": "shift()",
        },
        {
            "question": "Which method converts a JavaScript object into JSON text?",
            "options": [
                "JSON.stringify()",
                "JSON.parse()",
                "JSON.convert()",
                "JSON.text()"
            ],
            "answer": "JSON.stringify()",
        },
        {
            "question": "What does `===` compare in JavaScript?",
            "options": [
                "Only values",
                "Only types",
                "Value and type",
                "Variable names"
            ],
            "answer": "Value and type",
        },
        {
            "question": "Which method executes a function for every array element?",
            "options": ["forEach()", "each()", "iterate()", "loop()"],
            "answer": "forEach()",
        },
        {
            "question": "Which method combines array elements into a string?",
            "options": ["join()", "combine()", "concatString()", "merge()"],
            "answer": "join()",
        },
        {
            "question": "What does `NaN` represent in JavaScript?",
            "options": [
                "Not a Number",
                "Null and None",
                "New Array Number",
                "Negative Number"
            ],
            "answer": "Not a Number",
        },
        {
            "question": "Which statement is used to handle exceptions in JavaScript?",
            "options": ["try...catch", "handle...error", "catchError", "exception"],
            "answer": "try...catch",
        },
        {
            "question": "Which object represents a promise that is currently completed successfully?",
            "options": ["fulfilled", "resolvedOnly", "completed", "success"],
            "answer": "fulfilled",
        },
        {
            "question": "Which operator is commonly used for optional property access?",
            "options": ["?.", "??", "::", "=>"],
            "answer": "?.",
        },
    ],


    # =========================================================
    # REACT — 20 QUESTIONS
    # =========================================================

    "react": [

        {
            "question": "Which hook is used to manage state in a React function component?",
            "options": ["useEffect", "useState", "useContext", "useRef"],
            "answer": "useState",
        },
        {
            "question": "Which prop is commonly used to uniquely identify items rendered in a React list?",
            "options": ["id", "index", "key", "unique"],
            "answer": "key",
        },
        {
            "question": "What is JSX?",
            "options": [
                "A database language",
                "A syntax extension for JavaScript",
                "A CSS framework",
                "A backend server"
            ],
            "answer": "A syntax extension for JavaScript",
        },
        {
            "question": "Which hook is commonly used for side effects in React?",
            "options": ["useState", "useEffect", "useMemo", "useKey"],
            "answer": "useEffect",
        },
        {
            "question": "What is a React component?",
            "options": [
                "A reusable UI building block",
                "A database table",
                "A CSS property",
                "A Git branch"
            ],
            "answer": "A reusable UI building block",
        },
        {
            "question": "How can data be passed from a parent component to a child component?",
            "options": ["Through props", "Through SQL", "Through Git", "Through CSS only"],
            "answer": "Through props",
        },
        {
            "question": "Which command is commonly used to create a React project with Vite?",
            "options": [
                "npm create vite@latest",
                "npm react create",
                "react init vite",
                "npm start-react"
            ],
            "answer": "npm create vite@latest",
        },
        {
            "question": "What happens when React state changes?",
            "options": [
                "The component can re-render",
                "The database is automatically deleted",
                "The browser closes",
                "Git creates a commit"
            ],
            "answer": "The component can re-render",
        },
        {
            "question": "Which hook can be used to access a DOM element directly?",
            "options": ["useRef", "useState", "useEffectOnly", "useDOM"],
            "answer": "useRef",
        },
        {
            "question": "Why are keys used when rendering lists in React?",
            "options": [
                "To help React identify list elements",
                "To encrypt data",
                "To connect to SQL",
                "To create API routes"
            ],
            "answer": "To help React identify list elements",
        },
        {
            "question": "What is the purpose of useContext?",
            "options": [
                "Access shared context data",
                "Create database tables",
                "Handle HTTP requests only",
                "Compile JSX"
            ],
            "answer": "Access shared context data",
        },
        {
            "question": "Which hook can memoize an expensive calculated value?",
            "options": ["useMemo", "useState", "useFetch", "useValue"],
            "answer": "useMemo",
        },
        {
            "question": "Which hook can memoize a function reference?",
            "options": ["useCallback", "useFunction", "useMemoOnly", "useHandler"],
            "answer": "useCallback",
        },
        {
            "question": "What is a controlled component in React?",
            "options": [
                "A form element whose value is controlled by React state",
                "A component controlled by CSS",
                "A backend component",
                "A database model"
            ],
            "answer": "A form element whose value is controlled by React state",
        },
        {
            "question": "What is conditional rendering in React?",
            "options": [
                "Rendering UI based on a condition",
                "Creating SQL queries",
                "Changing Git branches",
                "Installing dependencies"
            ],
            "answer": "Rendering UI based on a condition",
        },
        {
            "question": "What is the purpose of React.Fragment?",
            "options": [
                "Group elements without adding an extra DOM element",
                "Create API endpoints",
                "Manage state",
                "Fetch data"
            ],
            "answer": "Group elements without adding an extra DOM element",
        },
        {
            "question": "Which file commonly contains dependencies and scripts in a React project?",
            "options": ["package.json", "react.json", "project.json", "dependencies.js"],
            "answer": "package.json",
        },
        {
            "question": "What does lifting state up mean in React?",
            "options": [
                "Moving shared state to a common parent",
                "Deleting component state",
                "Moving state to the database",
                "Creating a new React project"
            ],
            "answer": "Moving shared state to a common parent",
        },
        {
            "question": "Which syntax is commonly used to render a JavaScript expression inside JSX?",
            "options": ["{}", "[]", "()", "<>"],
            "answer": "{}",
        },
        {
            "question": "What is React Router commonly used for?",
            "options": [
                "Client-side navigation between views",
                "Database management",
                "Python execution",
                "Git version control"
            ],
            "answer": "Client-side navigation between views",
        },
    ],


    # =========================================================
    # ANGULAR — 20 QUESTIONS
    # =========================================================

    "angular": [

        {
            "question": "Which language is primarily used to develop Angular applications?",
            "options": ["Python", "Java", "TypeScript", "C++"],
            "answer": "TypeScript",
        },
        {
            "question": "Which decorator is used to define an Angular component?",
            "options": ["@Component", "@Service", "@Angular", "@Module"],
            "answer": "@Component",
        },
        {
            "question": "What is Angular?",
            "options": [
                "A TypeScript-based web framework",
                "A database",
                "A Python library",
                "A Git tool"
            ],
            "answer": "A TypeScript-based web framework",
        },
        {
            "question": "Which command is commonly used to create a new Angular application?",
            "options": [
                "ng new app-name",
                "angular create app-name",
                "npm angular-new",
                "ng create-project"
            ],
            "answer": "ng new app-name",
        },
        {
            "question": "Which decorator is commonly used to define an Angular service?",
            "options": ["@Service", "@Injectable", "@Provider", "@AngularService"],
            "answer": "@Injectable",
        },
        {
            "question": "Which Angular feature is commonly used for dependency injection?",
            "options": [
                "Dependency Injection",
                "DOM Injection",
                "CSS Injection",
                "HTML Injection"
            ],
            "answer": "Dependency Injection",
        },
        {
            "question": "Which Angular directive is commonly used for conditional rendering?",
            "options": ["*ngIf", "*ngFor", "*ngSwitchOnly", "*condition"],
            "answer": "*ngIf",
        },
        {
            "question": "Which Angular directive is commonly used to iterate over a list?",
            "options": ["*ngIf", "*ngFor", "*ngLoop", "*forEach"],
            "answer": "*ngFor",
        },
        {
            "question": "What is an Angular service commonly used for?",
            "options": [
                "Sharing reusable application logic",
                "Creating database tables",
                "Managing Git branches",
                "Compiling Python"
            ],
            "answer": "Sharing reusable application logic",
        },
        {
            "question": "Which command is commonly used to start an Angular development server?",
            "options": ["ng serve", "angular start", "npm angular-run", "ng server-start"],
            "answer": "ng serve",
        },
        {
            "question": "Which decorator defines an Angular module in traditional NgModule-based applications?",
            "options": ["@NgModule", "@Module", "@AngularModule", "@AppModule"],
            "answer": "@NgModule",
        },
        {
            "question": "Which Angular feature is commonly used for navigating between views?",
            "options": ["Angular Router", "Angular Navigator", "RouteManager", "ViewRouter"],
            "answer": "Angular Router",
        },
        {
            "question": "Which symbol is commonly used for property binding in Angular templates?",
            "options": ["[]", "()", "{}", "<>"],
            "answer": "[]",
        },
        {
            "question": "Which syntax is commonly used for event binding in Angular?",
            "options": ["()", "[]", "{}", "<>"],
            "answer": "()",
        },
        {
            "question": "Which Angular service is commonly used to make HTTP requests?",
            "options": ["HttpClient", "HttpService", "ApiClientOnly", "RequestClient"],
            "answer": "HttpClient",
        },
        {
            "question": "Which RxJS type commonly represents a stream of asynchronous values in Angular?",
            "options": ["Observable", "StreamOnly", "AsyncList", "PromiseArray"],
            "answer": "Observable",
        },
        {
            "question": "What is two-way data binding commonly represented by in Angular?",
            "options": ["[(ngModel)]", "[ngModel]", "(ngModel)", "{{ngModel}}"],
            "answer": "[(ngModel)]",
        },
        {
            "question": "Which command builds an Angular application for deployment?",
            "options": ["ng build", "ng deploy-build", "angular compile", "ng package"],
            "answer": "ng build",
        },
        {
            "question": "What is an Angular pipe used for?",
            "options": [
                "Transforming data for display",
                "Creating database tables",
                "Managing Git branches",
                "Starting the server"
            ],
            "answer": "Transforming data for display",
        },
        {
            "question": "Which lifecycle hook is commonly called after Angular initializes component input properties?",
            "options": ["ngOnInit", "ngAfterStart", "ngInitComponent", "ngLoad"],
            "answer": "ngOnInit",
        },
    ],
}


# =========================================================
# NORMALIZE SKILL
# =========================================================

def normalize_skill(skill):
    """
    Normalize a skill name so that
    Python, python, and PYTHON are treated the same.
    """

    return str(skill).strip().lower()

GENERAL_QUESTIONS = [
    {
        "question": "What is the main purpose of a function in programming?",
        "options": [
            "To store files",
            "To perform a reusable task",
            "To create a database",
            "To install software"
        ],
        "answer": "To perform a reusable task"
    },
    {
        "question": "Which data structure follows the FIFO principle?",
        "options": [
            "Stack",
            "Queue",
            "Tree",
            "Graph"
        ],
        "answer": "Queue"
    },
    {
        "question": "Which data structure follows the LIFO principle?",
        "options": [
            "Queue",
            "Stack",
            "Array",
            "Linked List"
        ],
        "answer": "Stack"
    },
    {
        "question": "What is the purpose of a primary key in a database?",
        "options": [
            "To store duplicate records",
            "To uniquely identify a record",
            "To delete a table",
            "To create a database"
        ],
        "answer": "To uniquely identify a record"
    },
    {
        "question": "Which SQL command is used to retrieve data?",
        "options": [
            "INSERT",
            "UPDATE",
            "SELECT",
            "DELETE"
        ],
        "answer": "SELECT"
    },
    {
        "question": "What does API stand for?",
        "options": [
            "Application Programming Interface",
            "Application Process Integration",
            "Advanced Programming Interface",
            "Automated Program Interaction"
        ],
        "answer": "Application Programming Interface"
    },
    {
        "question": "Which HTTP method is commonly used to retrieve data?",
        "options": [
            "POST",
            "GET",
            "DELETE",
            "PATCH"
        ],
        "answer": "GET"
    },
    {
        "question": "Which HTTP status code indicates a successful request?",
        "options": [
            "404",
            "500",
            "200",
            "401"
        ],
        "answer": "200"
    },
    {
        "question": "What is OOP?",
        "options": [
            "Object-Oriented Programming",
            "Open Online Programming",
            "Object Operation Process",
            "Ordered Object Programming"
        ],
        "answer": "Object-Oriented Programming"
    },
    {
        "question": "Which of the following is an OOP concept?",
        "options": [
            "Encapsulation",
            "Compilation",
            "Execution",
            "Debugging"
        ],
        "answer": "Encapsulation"
    },
    {
        "question": "What is the purpose of Git?",
        "options": [
            "Database management",
            "Version control",
            "Web hosting only",
            "Operating system management"
        ],
        "answer": "Version control"
    },
    {
        "question": "Which Git command is commonly used to download a repository?",
        "options": [
            "git clone",
            "git push",
            "git merge",
            "git status"
        ],
        "answer": "git clone"
    },
    {
        "question": "What is debugging?",
        "options": [
            "Writing documentation",
            "Finding and fixing errors",
            "Creating a database",
            "Deploying an application"
        ],
        "answer": "Finding and fixing errors"
    },
    {
        "question": "What does REST commonly refer to in web development?",
        "options": [
            "A database system",
            "An architectural style for web services",
            "A programming language",
            "A testing framework"
        ],
        "answer": "An architectural style for web services"
    },
    {
        "question": "Which of these is a relational database?",
        "options": [
            "PostgreSQL",
            "Redis",
            "MongoDB",
            "Cassandra"
        ],
        "answer": "PostgreSQL"
    },
    {
        "question": "What is an algorithm?",
        "options": [
            "A programming language",
            "A step-by-step procedure for solving a problem",
            "A database",
            "A server"
        ],
        "answer": "A step-by-step procedure for solving a problem"
    },
    {
        "question": "What is the average time complexity of searching for a key in a hash table?",
        "options": [
            "O(1)",
            "O(n)",
            "O(n²)",
            "O(log n)"
        ],
        "answer": "O(1)"
    },
    {
        "question": "Which layer of a typical application is responsible for handling business logic?",
        "options": [
            "Presentation layer",
            "Business/service layer",
            "Database storage only",
            "Network cable"
        ],
        "answer": "Business/service layer"
    },
    {
        "question": "Why is input validation important in a web application?",
        "options": [
            "To increase screen brightness",
            "To prevent invalid or potentially harmful input",
            "To make the database larger",
            "To remove authentication"
        ],
        "answer": "To prevent invalid or potentially harmful input"
    },
    {
        "question": "What is the purpose of authentication?",
        "options": [
            "To determine who a user is",
            "To format a database",
            "To compile code",
            "To create HTML"
        ],
        "answer": "To determine who a user is"
    }
]
# =========================================================
# SELECT QUESTIONS
# =========================================================

def select_questions(skills):
    MAX_QUESTIONS = 20

    skill_question_sets = []

    for skill in skills or []:
        normalized_skill = normalize_skill(skill)

        if normalized_skill in QUESTION_BANK:
            questions = []

            for question in QUESTION_BANK[normalized_skill]:
                question_copy = question.copy()
                question_copy["skill"] = normalized_skill
                questions.append(question_copy)

            if questions:
                random.shuffle(questions)
                skill_question_sets.append(questions)

    # ---------------------------------------------------------
    # FALLBACK:
    # If no recognized candidate skills are available,
    # provide a general Software Engineering assessment.
    # ---------------------------------------------------------
    if not skill_question_sets:
        questions = []

        for question in GENERAL_QUESTIONS:
            question_copy = question.copy()
            question_copy["skill"] = "general"
            questions.append(question_copy)

        random.shuffle(questions)

        return questions[:MAX_QUESTIONS]

    # ---------------------------------------------------------
    # SKILL-BASED ASSESSMENT
    # Distribute questions across candidate skills.
    # ---------------------------------------------------------
    selected_questions = []
    question_indexes = [0] * len(skill_question_sets)

    while len(selected_questions) < MAX_QUESTIONS:
        added_question = False

        for index, questions in enumerate(skill_question_sets):
            current_index = question_indexes[index]

            if current_index >= len(questions):
                continue

            selected_questions.append(
                questions[current_index]
            )

            question_indexes[index] += 1
            added_question = True

            if len(selected_questions) >= MAX_QUESTIONS:
                break

        if not added_question:
            break

    random.shuffle(selected_questions)

    return selected_questions