# 🧠 Developer Tools Research Agent

A command-line AI-powered research assistant that helps developers discover and analyze software tools, libraries, and platforms. Built using [OpenAI](https://openai.com/), [LangChain](https://www.langchain.com/), [LangGraph](https://www.langchain.com/langgraph/), and [Firecrawl](https://firecrawl.dev/), this agent automates tool discovery, comparison, and recommendation — all from a single query.

---

## 🚀 Features

- 🔍 **Tool Extraction**: Automatically identifies relevant tools from articles and websites.
- 🧪 **Structured Analysis**: Uses LLMs to evaluate pricing, APIs, tech stack, integrations, and more.
- 🧩 **Multi-step Workflow**: Built with LangGraph to handle complex stateful logic.
- 💡 **LLM-Powered Recommendations**: Summarizes the best tools for your query.
- 🌐 **Web Scraping via Firecrawl**: Pulls real-time content from the web.

---

## 🗂️ Project Structure

```text

dev-research-agent/ 
├── main.py # CLI entry point 
├── pyproject.toml # Project dependencies (uv-compatible) 
├── uv.lock # Locked dependency versions 
├── README.md # You're reading it! 
└── src/ 
  ├── workflow.py # LangGraph process logic 
  ├── prompts.py # Prompt templates for LLM 
  ├── models.py # Pydantic data models 
  ├── firecrawl_ops.py # Firecrawl search/scrape wrapper 
  └── init.py
```


---

## ⚙️ Installation

### 🔐 Prerequisites

- Python 3.10+
- A valid [Firecrawl API key](https://firecrawl.dev/)
- OpenAI API key 

### 📦 Install Dependencies

You can use [uv](https://github.com/astral-sh/uv) or plain `pip`:

```bash
# Recommended: using uv
uv pip install -r pyproject.toml

# Or with pip
pip install -r requirements.txt  # if you generate one
```

🔑 Set Environment Variables
Create a .env file in the project root:

```bash
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Required for LangChain
```
🧪 Usage
Run the agent from the project root:
```
python main.py

```

You'll be prompted to enter a query, such as:

```
🔍 Developer Tools Query: observability tools
```
The agent will:

Search for relevant articles and tools
Scrape and analyze tool websites
Display structured results and a recommendation
📖 Example Output

```
Developer Tools Query: cursor

1. TabNine - Paid - JavaScript, Python - GitHub Integration - AI code assistant
2. Zencoder - Freemium - Python, Go - CI/CD focus
3. Cursor - Freemium - GPT-4 + Claude integration - Great dev UX

Recommendation:
"Cursor is the best choice due to its advanced language model stack..."
```
🧱 Built With
- LangChain
- LangGraph
- Firecrawl
- Pydantic
- OpenAI GPT Models

