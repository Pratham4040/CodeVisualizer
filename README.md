# CodeVisualizer
Its A Code Visualizer it visualizes your code step by step :)
## AlgoVisualizer Backend

**AlgoVisualizer** is a FastAPI backend for visualizing Python algorithms and data structures step-by-step. It parses and executes user-submitted Python code in a safe, controlled environment and returns a detailed trace of variable states and execution steps for frontend visualization.

---

### 🚀 Features
- Visualizes Python code execution step-by-step
- Returns variable state, line number, and message for each step
- Supports assignments, loops, if/else, lists, dicts, and basic built-ins (`len`, `range`)
- CORS enabled for frontend integration
- API documented with OpenAPI (Swagger UI at `/docs`)

---

### 🛠️ Requirements
- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/) (for local dev)
- [pydantic](https://docs.pydantic.dev/)

---

### ⚡ Setup & Run

```bash
# 1. Clone the repo and enter Backend directory
git clone https://github.com/Pratham4040/CodeVisualizer.git
cd CodeVisualizer/Backend

# 2. (Recommended) Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt  # or see pyproject.toml

# 4. Run the FastAPI server
uvicorn main:app --reload
# The API will be available at http://localhost:8000
```

---

### 📚 API Usage

**POST** `/visualize`

**Request JSON:**
```json
{
	"code": "items = []\nfor i in range(3):\n    items.append(i)\nprint(items)"
}
```

**Response JSON:**
```json
{
	"status": "success",
	"steps": [
		{
			"line": 1,
			"message": "Assigns [] to variable 'items'",
			"scope": {"items": []}
		},
		...
	]
}
```

**Error Example:**
```json
{
	"detail": "Execution Error: name 'foo' is not defined"
}
```

---

### 🧩 Supported Python Features
- Variable assignment, arithmetic, lists, dicts
- for/while loops, if/else
- Built-ins: `len`, `range`
- List/dict methods: `append`, `pop`, `update`

---

### Credits
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Project by [Pratham4040](https://github.com/Pratham4040)
