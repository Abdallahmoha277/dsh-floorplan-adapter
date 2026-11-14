#!/usr/bin/env python3
"""Generate floorplan/architecture.json for the Gobber project.

Single source of truth: SUBSYSTEMS below. The same module list produces both
the `subsystems` view (the compact schema asked for by floorplan_scan) and the
`nodes` view (what floorplan's build.mjs consumes), so the two can never drift.
"""
import json
import os

SCAN_PATH = "/home/abdallahmohamedabdallah277/Gobber-/floorplan/.cache/scan.json"
OUT_PATH = "/home/abdallahmohamedabdallah277/dsh-floorplan-adapter/generated/architecture.json"

# id, name, description, kind, modules
# module: id, name, description, files, kind
SUBSYSTEMS = [
    {
        "id": "api",
        "name": "Main Server",
        "description": "The web server that receives requests, checks them and passes them to the right place.",
        "kind": "service",
        "modules": [
            {
                "id": "app-entry",
                "name": "Application Entry",
                "description": "Starts the web server, lets the chat screen connect and publishes performance numbers.",
                "kind": "feature",
                "files": ["app/__init__.py", "app/main.py"],
            },
            {
                "id": "route-registration",
                "name": "Route Wiring",
                "description": "Connects the sign-in, ask, history, memory and health requests under one address.",
                "kind": "feature",
                "files": [
                    "app/api/__init__.py",
                    "app/api/v1/__init__.py",
                    "app/api/v1/endpoints/__init__.py",
                    "app/api/v1/router.py",
                ],
            },
            {
                "id": "auth-endpoints",
                "name": "Sign-in Routes",
                "description": "Registers people and checks their password to issue a sign-in pass.",
                "kind": "feature",
                "files": ["app/api/v1/endpoints/auth.py"],
            },
            {
                "id": "agent-endpoints",
                "name": "Ask Route",
                "description": "Accepts a question, runs the agent graph and returns the route, code and output.",
                "kind": "feature",
                "files": ["app/api/v1/endpoints/agent.py"],
            },
            {
                "id": "history-endpoints",
                "name": "History Routes",
                "description": "Reads and appends the signed-in user's chat messages.",
                "kind": "feature",
                "files": ["app/api/v1/endpoints/history.py"],
            },
            {
                "id": "memory-endpoints",
                "name": "Memory Routes",
                "description": "Creates and lists stored question-and-solution records.",
                "kind": "feature",
                "files": ["app/api/v1/endpoints/memory.py"],
            },
            {
                "id": "health-endpoints",
                "name": "Health Routes",
                "description": "Reports whether the main server is running and whether the database answers.",
                "kind": "feature",
                "files": ["app/api/v1/endpoints/health.py"],
            },
        ],
    },
    {
        "id": "agents",
        "name": "Agent Workflow",
        "description": "The workflow that decides what happens to a question and the specialist helpers that carry it out.",
        "kind": "feature",
        "modules": [
            {
                "id": "workflow-graph",
                "name": "Workflow Graph",
                "description": "Defines the shared agent state, graph nodes and the conditional retry loop.",
                "kind": "feature",
                "files": ["app/agents/__init__.py", "app/agents/graph.py"],
            },
            {
                "id": "router-agent",
                "name": "Question Sorter",
                "description": "Classifies a question as general QA, research or code.",
                "kind": "feature",
                "files": ["app/agents/router_agent.py"],
            },
            {
                "id": "coder-agent",
                "name": "Code Writer",
                "description": "Generates raw Python from the task, a remembered solution and review feedback.",
                "kind": "feature",
                "files": ["app/agents/coder_agent.py"],
            },
            {
                "id": "executor-agent",
                "name": "Code Runner",
                "description": "Sends generated code to the sandbox and returns stdout and stderr.",
                "kind": "feature",
                "files": ["app/agents/executor_agent.py"],
            },
            {
                "id": "critic-agent",
                "name": "Code Reviewer",
                "description": "Passes or fails the execution result and supplies feedback for another attempt.",
                "kind": "feature",
                "files": ["app/agents/critic_agent.py"],
            },
            {
                "id": "responder-agent",
                "name": "Answer Writer",
                "description": "Writes a direct answer for non-coding questions.",
                "kind": "feature",
                "files": ["app/agents/responder_agent.py"],
            },
        ],
    },
    {
        "id": "core",
        "name": "Platform Core",
        "description": "Shared configuration, database session handling and credential helpers.",
        "kind": "library",
        "modules": [
            {
                "id": "settings",
                "name": "Settings",
                "description": "Loads project, database, Redis and DeepSeek settings from the environment.",
                "kind": "config",
                "files": ["app/core/__init__.py", "app/core/config.py", ".env.example"],
            },
            {
                "id": "database-session",
                "name": "Database Session",
                "description": "Opens and closes connections to the saved records and gives each request its own session.",
                "kind": "data",
                "files": ["app/core/database.py"],
            },
            {
                "id": "auth-security",
                "name": "Access Security",
                "description": "Hashes passwords, checks them and signs the pass used for later requests.",
                "kind": "library",
                "files": ["app/core/security.py"],
            },
        ],
    },
    {
        "id": "data",
        "name": "Data Layer",
        "description": "Database records, the shape of each request and response, and the steps that keep tables current.",
        "kind": "data",
        "modules": [
            {
                "id": "orm-models",
                "name": "Tables",
                "description": "The records for people, chat messages and saved solutions, and how they map to tables.",
                "kind": "data",
                "files": [
                    "app/models/__init__.py",
                    "app/models/chat.py",
                    "app/models/memory.py",
                    "app/models/user.py",
                ],
            },
            {
                "id": "schemas",
                "name": "Payload Shapes",
                "description": "Defines what each request and response must contain and checks it.",
                "kind": "data",
                "files": [
                    "app/schemas/__init__.py",
                    "app/schemas/chat.py",
                    "app/schemas/memory.py",
                    "app/schemas/user.py",
                ],
            },
            {
                "id": "migrations",
                "name": "Table Changes",
                "description": "The setup that creates the tables and keeps their shape current.",
                "kind": "data",
                "files": [
                    "alembic.ini",
                    "alembic/README",
                    "alembic/env.py",
                    "alembic/script.py.mako",
                    "alembic/versions/dcf6d5c2ab38_init_tables.py",
                ],
            },
        ],
    },
    {
        "id": "memory",
        "name": "Solution Memory",
        "description": "Vector search that lets the system reuse code that already passed review.",
        "kind": "library",
        "modules": [
            {
                "id": "vector-store",
                "name": "Solution Store",
                "description": "Embeds questions with Hugging Face and searches or upserts solutions in Qdrant.",
                "kind": "library",
                "files": ["app/services/__init__.py", "app/services/memory_service.py"],
            },
        ],
    },
    {
        "id": "sandbox",
        "name": "Execution Sandbox",
        "description": "The locked-down service that runs AI-generated Python.",
        "kind": "service",
        "modules": [
            {
                "id": "execution-server",
                "name": "Execution Server",
                "description": "Writes code to a temporary file, runs it with a timeout and returns the output.",
                "kind": "feature",
                "files": ["sandbox/server.py"],
            },
            {
                "id": "sandbox-image",
                "name": "Sandbox Image",
                "description": "Builds a non-root Python image that serves the executor on port 7070.",
                "kind": "infra",
                "files": ["sandbox/Dockerfile"],
            },
        ],
    },
    {
        "id": "ui",
        "name": "Chat UI",
        "description": "The Streamlit chat screen people use to sign in and talk to the agents.",
        "kind": "ui",
        "modules": [
            {
                "id": "streamlit-app",
                "name": "Chat Screen",
                "description": "Signs in, shows history, sends questions and displays answers or generated code.",
                "kind": "ui",
                "files": ["app_ui.py", ".streamlit/config.toml"],
            },
        ],
    },
    {
        "id": "ops",
        "name": "Infrastructure and Ops",
        "description": "Local setup, containers, monitoring, developer tooling and project documentation.",
        "kind": "infra",
        "modules": [
            {
                "id": "containers",
                "name": "Container Stack",
                "description": "Runs PostgreSQL, Redis, Qdrant, the sandbox, Prometheus, Grafana and Loki.",
                "kind": "infra",
                "files": ["docker-compose.yml"],
            },
            {
                "id": "observability",
                "name": "Monitoring",
                "description": "Collects request counts and timings from the main server every 15 seconds.",
                "kind": "infra",
                "files": ["prometheus.yml"],
            },
            {
                "id": "dev-scripts",
                "name": "Setup Scripts",
                "description": "Installs dependencies, starts the services, prepares the database and launches the server.",
                "kind": "script",
                "files": ["setup.sh", "start.sh"],
            },
            {
                "id": "project-docs",
                "name": "Project Docs",
                "description": "Explains the system and keeps generated files out of version control.",
                "kind": "config",
                "files": ["README.md", ".gitignore"],
            },
            {
                "id": "tooling",
                "name": "Developer Tooling",
                "description": "Pins dependencies and configures formatting, linting and the Python interpreter.",
                "kind": "config",
                "files": ["requirements.txt", ".pre-commit-config.yaml", ".vscode/settings.json"],
            },
            {
                "id": "ci-pipeline",
                "name": "Automatic Checks",
                "description": "Starts the databases, prepares the tables and runs all automatic checks on every push.",
                "kind": "infra",
                "files": [".github/workflows/ci.yml"],
            },
        ],
    },
    {
        "id": "tests",
        "name": "Tests",
        "description": "Automated checks for the main server and the question sorter.",
        "kind": "test",
        "modules": [
            {
                "id": "api-tests",
                "name": "Server Tests",
                "description": "Exercises health, registration and login against a test client.",
                "kind": "test",
                "files": ["tests/conftest.py", "tests/test_api.py"],
            },
            {
                "id": "router-smoke-test",
                "name": "Sorting Check",
                "description": "Prints the route chosen for three sample questions.",
                "kind": "test",
                "files": ["test_router.py"],
            },
        ],
    },
]

EXTERNALS = [
    {
        "id": "deepseek",
        "label": "DeepSeek Model",
        "kind": "external",
        "summary": "The hosted chat model behind the sorter, coder, reviewer and answer writer.",
        "packages": ["pypi:langchain_openai"],
        "hosts": ["api.deepseek.com"],
    },
    {
        "id": "qdrant",
        "label": "Qdrant",
        "kind": "external",
        "summary": "Vector database that stores and searches embedded solutions.",
        "packages": ["pypi:qdrant_client"],
    },
    {
        "id": "huggingface",
        "label": "Hugging Face Embeddings",
        "kind": "external",
        "summary": "Turns questions into vectors with the all-MiniLM-L6-v2 model.",
        "packages": ["pypi:langchain_huggingface"],
    },
    {
        "id": "postgres",
        "label": "PostgreSQL",
        "kind": "external",
        "summary": "Stores users, chat messages and memory records through SQLAlchemy.",
        "packages": ["pypi:sqlalchemy", "pypi:psycopg"],
    },
    {
        "id": "prometheus",
        "label": "Prometheus",
        "kind": "external",
        "summary": "Collects request counts and timings from the main server's metrics address.",
        "packages": ["pypi:prometheus_fastapi_instrumentator"],
    },
]

EDGES = [
    {
        "from": "ui",
        "to": "api",
        "kind": "http",
        "label": "REST calls",
        "description": "The chat screen signs in, asks questions and reads or saves history under /api/v1.",
    },
    {
        "from": "agents.executor-agent",
        "to": "sandbox.execution-server",
        "kind": "http",
        "label": "POST /execute",
        "description": "Sends generated Python to the sandbox and receives stdout and stderr.",
    },
    {
        "from": "memory",
        "to": "qdrant",
        "kind": "data",
        "label": "search and upsert",
        "description": "Embeds a question, finds the nearest saved solution and stores newly approved code.",
    },
    {
        "from": "memory",
        "to": "huggingface",
        "kind": "call",
        "label": "embed query",
        "description": "Builds a 384-dimension vector for every question before searching or saving.",
    },
    {
        "from": "api",
        "to": "postgres",
        "kind": "data",
        "label": "users, chat, memories",
        "description": "All persistent records go through SQLAlchemy sessions to PostgreSQL.",
    },
    {
        "from": "agents",
        "to": "deepseek",
        "kind": "http",
        "label": "chat completions",
        "description": "Every model-backed agent calls the DeepSeek chat API with its own prompt.",
    },
    {
        "from": "agents.critic-agent",
        "to": "memory",
        "kind": "call",
        "label": "saves approved code",
        "description": "When the critic passes a solution, the workflow stores it in Qdrant before finishing.",
    },
    {
        "from": "ops.dev-scripts",
        "to": "ops.containers",
        "kind": "call",
        "label": "docker compose up",
        "description": "The startup script brings the service stack up before running the API.",
    },
    {
        "from": "prometheus",
        "to": "api",
        "kind": "http",
        "label": "scrapes /metrics",
        "description": "Prometheus polls the instrumented API every 15 seconds.",
    },
]

ANNOTATIONS = [
    {
        "path": "app/core/security.py",
        "note": "The JWT signing key and token lifetime are hardcoded here; move them into settings before production.",
        "tags": ["hotspot"],
    },
    {
        "path": "app/api/v1/endpoints/history.py",
        "note": "Every valid token is treated as user 1, so all accounts share one chat history.",
        "tags": ["hotspot"],
    },
    {
        "path": "app/main.py",
        "note": "Prometheus instrumentation is registered twice, so the metrics middleware is installed twice.",
        "tags": ["cleanup"],
    },
    {
        "path": ".env.example",
        "note": "The example settings file omits DEEPSEEK_API_KEY even though the app refuses to start without it.",
        "tags": ["config"],
    },
]

FLOWS = [
    {
        "id": "ask-assistant",
        "name": "Ask the assistant",
        "title": "Ask the assistant",
        "description": "A chat question is classified, answered directly or turned into code that runs and is reviewed.",
        "steps": [
            ("ui", "A person types a question in the chat screen."),
            ("api.agent-endpoints", "POST /api/v1/agent/ask checks the token and starts the workflow with an empty state."),
            ("agents.workflow-graph", "The router node classifies the request and chooses a branch."),
            ("agents.router-agent", "DeepSeek labels the question as general QA, research or code."),
            ("memory", "Code tasks search Qdrant for a similar solution that already passed review."),
            ("agents.coder-agent", "The coder writes Python using the task, the recalled solution and any feedback."),
            ("agents.executor-agent", "The runner posts the code to the sandbox."),
            ("sandbox.execution-server", "The sandbox runs the file under a timeout and returns stdout and stderr."),
            ("agents.critic-agent", "The critic passes the output or sends feedback back to the coder, up to three tries."),
            ("memory", "An approved solution is embedded and saved for future tasks."),
            ("ui", "The screen shows the answer, or the generated code and its output."),
        ],
    },
    {
        "id": "sign-in",
        "name": "Sign in",
        "title": "Sign in",
        "description": "A person logs in, gets a token and uses it to load and save chat history.",
        "steps": [
            ("ui", "The person enters a username and password in the sidebar."),
            ("api.auth-endpoints", "Login looks up the user and checks the password hash."),
            ("core.auth-security", "A signed JWT is issued for later requests."),
            ("data.orm-models", "The user record comes from the users table."),
            ("api.history-endpoints", "The token lets the app load and save that person's messages."),
        ],
    },
    {
        "id": "start-system",
        "name": "Start the system",
        "title": "Start the system",
        "description": "One script brings up the services, prepares the database and starts the API and chat app.",
        "steps": [
            ("ops.dev-scripts", "./start.sh creates and activates the virtual environment if needed."),
            ("ops.containers", "Docker Compose starts PostgreSQL, Redis, Qdrant, the sandbox and the monitoring stack."),
            ("data.migrations", "Alembic creates or updates the database tables."),
            ("api", "Uvicorn serves the main API on port 8000."),
            ("ops.observability", "Prometheus starts scraping the API's metrics."),
            ("ui", "Streamlit opens the chat screen and calls the API."),
        ],
    },
    {
        "id": "code-retry-loop",
        "name": "Fix a failed run",
        "title": "Fix a failed run",
        "description": "A failed execution loops back to the coder with feedback until it passes or runs out of tries.",
        "steps": [
            ("agents.workflow-graph", "The graph sends coding tasks down the code branch."),
            ("agents.coder-agent", "The coder writes the first version of the program."),
            ("agents.executor-agent", "The runner sends it to the sandbox."),
            ("sandbox.execution-server", "The sandbox returns output or an error."),
            ("agents.critic-agent", "The critic fails the result and writes what went wrong."),
            ("agents.coder-agent", "The coder receives that feedback and rewrites the code."),
            ("memory", "After a pass, the working solution is saved to Qdrant."),
        ],
    },
]

TOUR = [
    ("ui", "The chat screen", "People sign in here, type a question and see either an answer or generated code and its output."),
    ("api", "The main server", "Every request from the chat screen lands here and is passed to the right route."),
    ("agents", "The AI team", "The agents decide what kind of question this is, write code when needed, run it and review the result."),
    ("sandbox", "The safe runner", "Generated code runs in a separate locked-down container so it cannot touch the main app."),
    ("memory", "The memory", "Solutions that passed review are stored as vectors so a similar future task can start from them."),
    ("data", "The saved records", "Users, chat messages and memory records live in PostgreSQL, with Alembic keeping the tables current."),
]


def main():
    scan = json.load(open(SCAN_PATH, encoding="utf-8"))
    scanned = [f["path"] for f in scan["files"]]

    # --- subsystems view (compact schema) ---
    subsystems = []
    node_modules = []
    for sub in SUBSYSTEMS:
        modules = []
        for m in sub["modules"]:
            modules.append(
                {
                    "id": m["id"],
                    "name": m["name"],
                    "description": m["description"],
                    "files": list(m["files"]),
                }
            )
            node_modules.append(
                {
                    "id": f"{sub['id']}.{m['id']}",
                    "parent": sub["id"],
                    "label": m["name"],
                    "kind": m["kind"],
                    "summary": m["description"],
                    "paths": list(m["files"]),
                }
            )
        subsystems.append(
            {
                "id": sub["id"],
                "name": sub["name"],
                "description": sub["description"],
                "modules": modules,
            }
        )

    # --- nodes view (build.mjs) ---
    nodes = []
    for sub in SUBSYSTEMS:
        nodes.append(
            {
                "id": sub["id"],
                "label": sub["name"],
                "kind": sub["kind"],
                "summary": sub["description"],
            }
        )
    nodes.extend(node_modules)
    nodes.extend(EXTERNALS)

    # --- flows view: canonical objects + plain-text steps ---
    flows = []
    for fl in FLOWS:
        flows.append(
            {
                "id": fl["id"],
                "name": fl["name"],
                "title": fl["title"],
                "description": fl["description"],
                "steps": [
                    {"node": node_id, "note": note} for node_id, note in fl["steps"]
                ],
                "stepsText": [note for _, note in fl["steps"]],
            }
        )

    tour = [
        {"node": node_id, "title": title, "note": note}
        for node_id, title, note in TOUR
    ]

    summary = (
        "Gobber is a multi-agent AI backend for coding tasks. A FastAPI server sends each "
        "question through a LangGraph workflow that classifies it, writes Python with DeepSeek, "
        "runs the code in an isolated Docker sandbox, reviews the result, and stores approved "
        "solutions in Qdrant so similar tasks can reuse them. PostgreSQL keeps users and chat "
        "history, a Streamlit chat app is the interface, and Compose, Prometheus and Alembic "
        "cover setup and operations."
    )

    arch = {
        "$schema": "floorplan/architecture@1",
        "schema": "floorplan/architecture@1",
        "summary": summary,
        "project": {
            "name": "Gobber",
            "summary": (
                "A FastAPI backend and Streamlit chat app for a multi-agent coding assistant. "
                "LangGraph routes each question, writes and runs Python in a locked-down Docker "
                "sandbox, reviews the result, and stores successful solutions in Qdrant; "
                "PostgreSQL keeps users and chat history."
            ),
            "entrypoints": [
                "app/main.py",
                "app_ui.py",
                "sandbox/server.py",
                "start.sh",
            ],
        },
        "audience": "everyone",
        "include": ["code", "config", "docs", "other"],
        "subsystems": subsystems,
        "nodes": nodes,
        "edges": EDGES,
        "annotations": ANNOTATIONS,
        "flows": flows,
        "tour": tour,
    }

    # --- validation ---
    assigned = []
    for sub in subsystems:
        for m in sub["modules"]:
            assigned.extend(m["files"])
    dupes = sorted({p for p in assigned if assigned.count(p) > 1})
    missing = sorted(set(scanned) - set(assigned))
    extra = sorted(set(assigned) - set(scanned))
    assert not dupes, f"duplicate file assignments: {dupes}"
    assert not missing, f"unassigned scanned files: {missing}"
    assert not extra, f"assigned files not in scan: {extra}"
    assert len(assigned) == len(scanned) == 55, (len(assigned), len(scanned))

    node_ids = {n["id"] for n in nodes}
    for n in nodes:
        if "parent" in n:
            assert n["parent"] in node_ids, n
    for fl in flows:
        assert len(fl["steps"]) >= 2, fl["id"]
        for st in fl["steps"]:
            assert st["node"] in node_ids, (fl["id"], st["node"])
    for t in tour:
        assert t["node"] in node_ids, t

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(arch, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"wrote {OUT_PATH}")
    print(f"subsystems={len(subsystems)} modules={len(assigned)} nodes={len(nodes)} flows={len(flows)} tour={len(tour)}")
    print("all 55 scanned files assigned exactly once")


if __name__ == "__main__":
    main()
