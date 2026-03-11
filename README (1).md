<!-- JARVIS README — Professional · Aesthetic · Techy -->

<div align="center">

<!-- Animated Header Banner -->
```
 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 ░                                                             ░
 ░      ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗              ░
 ░      ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝              ░
 ░      ██║███████║██████╔╝██║   ██║██║███████╗              ░
 ░ ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║              ░
 ░ ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║              ░
 ░  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝              ░
 ░                                                             ░
 ░         Just A Rather Very     Intelligent System               ░
 ░                                                         ░
 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

<!-- Badges Row 1 -->
![Python](https://img.shields.io/badge/Python-3.11+-00bfff?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0e1a)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-00ffaa?style=for-the-badge&logo=llama&logoColor=white&labelColor=0a0e1a)
![PopOS](https://img.shields.io/badge/Pop!__OS-Linux-48b9c7?style=for-the-badge&logo=popos&logoColor=white&labelColor=0a0e1a)
![NVIDIA](https://img.shields.io/badge/NVIDIA-RTX_3050-76b900?style=for-the-badge&logo=nvidia&logoColor=white&labelColor=0a0e1a)

<!-- Badges Row 2 -->
![Status](https://img.shields.io/badge/Status-Active_Development-ff6600?style=for-the-badge&labelColor=0a0e1a)
![License](https://img.shields.io/badge/License-MIT-7b61ff?style=for-the-badge&labelColor=0a0e1a)
![Cost](https://img.shields.io/badge/API_Cost-₹0_per_month-00ffaa?style=for-the-badge&labelColor=0a0e1a)
![Privacy](https://img.shields.io/badge/Privacy-100%25_Local-ff3366?style=for-the-badge&labelColor=0a0e1a)

<br/>

> **"Any sufficiently advanced automation is indistinguishable from magic."**
>
> — A developer who got tired of doing things manually

<br/>

</div>

---

## ◈ What Is JARVIS?

**JARVIS** is a fully local, privacy-first AI automation system that runs entirely on your own hardware — no cloud, no subscriptions, no data leaks. Think Iron Man's assistant, but real, open-source, and running on a ₹0/month budget.

It combines a **local Large Language Model** (Qwen 3.5:4B via Ollama), **vector memory** (ChromaDB RAG), **computer automation** (PyAutoGUI), **messaging bots** (Telegram, Discord), and a **task planning engine** into one unified system that can:

- 🎤 **Listen** to your voice and respond
- 🧠 **Remember** everything you tell it — forever
- 🖥️ **Control** your computer autonomously
- 📱 **Receive commands** from your phone via Telegram
- 💼 **Automate** job applications, emails, GitHub, and more
- 🔀 **Break down** complex goals into executable steps

```
You say:  "Apply to 10 Python developer jobs today"
JARVIS:   → Searches LinkedIn/Indeed for matching jobs
          → Reads each job description
          → Customizes your resume for each role
          → Writes a unique cover letter
          → Logs everything to your spreadsheet
          → Reports back: "Done. Applied to 10 jobs."
```

---

## ◈ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         JARVIS CORE                             │
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    │
│   │   BRAIN     │    │   MEMORY    │    │    SENSES       │    │
│   │             │    │             │    │                 │    │
│   │ Qwen 3.5:4B │◄──►│ ChromaDB    │◄──►│ Voice (Whisper) │    │
│   │             │    │ RAG System  │    │ Screen Vision   │    │
│   │ Task Planner│    │ SQLite Logs │    │ File Watcher    │    │
│   └──────┬──────┘    └─────────────┘    └────────┬────────┘    │
│          │                                        │             │
│          ▼                                        ▼             │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                      ACTION ENGINE                      │  │
│   │                                                         │  │
│   │  🖱️ PyAutoGUI   🌐 Playwright   💻 Subprocess           │  │
│   │  📁 File Mgmt   📧 Email API    ✈️ Telegram Bot          │  │
│   │  🐙 GitHub API  📊 Sheets API   🎮 Discord Bot           │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    SAFETY LAYER  🛡️                      │  │
│   │  Kill Switch · Approval Gates · Action Logs · Sandbox   │  │
│   └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ◈ Feature Map

### 🧠 Intelligence Layer
| Feature | Description | Status |
|---------|-------------|--------|
| **Single Model** | Qwen 3.5:4B handles all tasks — fast, capable, fits in 4GB VRAM | 🔵 Planned |
| **RAG Memory** | Vector search over your personal files, notes, and docs | � Planned |
| **Task Planner** | Breaks big goals into ordered, executable steps | � Planned |
| **Conversation History** | Remembers context across sessions | � Planned |
| **Web Knowledge** | Searches the web when it doesn't know something | 🔵 Planned |

### 👁️ Senses
| Feature | Description | Status |
|---------|-------------|--------|
| **Wake Word** | "Hey Jarvis" triggers activation | 🔵 Planned |
| **Voice Input** | Whisper-based local speech-to-text | 🔵 Planned |
| **Screen Vision** | Reads and understands what's on screen (LLaVA) | 🔵 Planned |
| **File Watcher** | Monitors folders and triggers on new files | � Planned |

### 🤖 Automation
| Feature | Description | Status |
|---------|-------------|--------|
| **PC Control** | Full mouse, keyboard, and window automation | � Planned |
| **Browser Agent** | Controls Chrome/Firefox for any web task | � Planned |
| **Terminal Agent** | Runs shell commands safely with guardrails | � Planned |
| **File Organizer** | Auto-sorts downloads, renames, deduplicates | � Planned |

### 📡 Communication
| Feature | Description | Status |
|---------|-------------|--------|
| **Telegram Bot** | Control JARVIS from your phone anywhere | 🔵 Planned |
| **Discord Bot** | AI assistant inside your Discord server | � Planned |
| **Email Automation** | Read, summarize, draft, and send emails | 🔵 Planned |
| **WhatsApp Bot** | Unofficial — use at your own risk | 🔵 Planned |

### 💼 Career Tools
| Feature | Description | Status |
|---------|-------------|--------|
| **Job Application Bot** | Scrape → customize resume → cover letter → apply | � Planned |
| **GitHub Automator** | Auto README, commit messages, issue creation | � Planned |
| **Code Reviewer** | Finds bugs, suggests fixes in your own code | 🔵 Planned |
| **Daily Briefing** | Morning report: tasks, emails, goals, news | 🔵 Planned |

> 🔵 Planned

---

## ◈ Tech Stack

```
┌──────────────────────────────────────────────────────┐
│  AI / ML                                             │
│  ├── Ollama          — Local LLM runtime             │
│  ├── Qwen 3.5:4B     — Primary model (all tasks)     │
│  ├── Whisper         — Speech to text                │
│  └── LLaVA           — Vision model                  │
│                                                      │
│  MEMORY                                              │
│  ├── ChromaDB        — Vector database               │
│  ├── LangChain       — RAG pipeline                  │
│  └── SQLite          — Conversation history          │
│                                                      │
│  AUTOMATION                                          │
│  ├── PyAutoGUI       — Mouse & keyboard              │
│  ├── Playwright      — Browser control               │
│  ├── Watchdog        — File system monitoring        │
│  └── subprocess      — Terminal commands             │
│                                                      │
│  COMMUNICATION                                       │
│  ├── python-telegram-bot  — Telegram                 │
│  ├── discord.py           — Discord                  │
│  ├── Gmail API            — Email                    │
│  └── whatsapp-web.js      — WhatsApp (risky)         │
│                                                      │
│  BACKEND                                             │
│  ├── FastAPI         — REST API                      │
│  ├── WebSockets      — Real-time dashboard           │
│  └── React           — Web UI                        │
│                                                      │
│  SYSTEM                                              │
│  ├── Pop!_OS (Linux) — OS                            │
│  ├── RTX 3050 4GB    — GPU inference                 │
│  ├── i5-12500K       — CPU                           │
│  └── 8GB RAM         — Memory                        │
└──────────────────────────────────────────────────────┘
```

---

## ◈ Project Structure

```
jarvis/
│
├── 🧠 brain/
│   ├── __init__.py
│   ├── llm.py              # Ollama model interface (Qwen 3.5:4B)
│   ├── planner.py          # Task breakdown engine
│   └── router.py           # Decides which module handles task
│
├── 🗃️ memory/
│   ├── __init__.py
│   ├── rag.py              # ChromaDB vector store + retrieval
│   ├── history.py          # Conversation persistence (SQLite)
│   └── indexer.py          # File system indexer
│
├── 👁️ senses/
│   ├── __init__.py
│   ├── voice.py            # Whisper speech-to-text
│   ├── screen.py           # Screenshot + LLaVA vision
│   └── watcher.py          # File system watcher
│
├── 🤖 actions/
│   ├── __init__.py
│   ├── computer.py         # PyAutoGUI mouse/keyboard
│   ├── browser.py          # Playwright web automation
│   ├── terminal.py         # Safe subprocess execution
│   └── files.py            # File management
│
├── 📡 comms/
│   ├── __init__.py
│   ├── telegram_bot.py     # Telegram interface
│   ├── discord_bot.py      # Discord interface
│   └── email_handler.py    # Gmail read/send
│
├── 💼 career/
│   ├── __init__.py
│   ├── job_bot.py          # Job scraper + applier
│   ├── resume.py           # Resume customizer
│   └── github_bot.py       # GitHub automator
│
├── 🛡️ safety/
│   ├── __init__.py
│   ├── guardrails.py       # Command safety checker
│   ├── logger.py           # Full action audit log
│   └── killswitch.py       # Emergency stop
│
├── 🖥️ dashboard/
│   ├── api.py              # FastAPI backend
│   └── ui/                 # React frontend
│
├── data/
│   ├── knowledge/          # Your documents for RAG
│   ├── resume.docx         # Your resume
│   └── logs/               # Action history
│
├── config.yaml             # All settings in one place
├── main.py                 # Entry point
├── setup.sh                # One-command setup
└── requirements.txt        # All dependencies
```

---

## ◈ Quick Start

### Prerequisites

```bash
# Make sure you have:
# - Pop!_OS or any Linux distro
# - Python 3.11+
# - NVIDIA GPU (any VRAM)
# - Git installed

python3 --version    # Should be 3.11+
nvidia-smi           # Should show your GPU
```

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/jarvis.git
cd jarvis

# 2. Run the one-command setup
chmod +x setup.sh
./setup.sh

# 3. Configure your settings
cp config.example.yaml config.yaml
nano config.yaml   # Add your Telegram token, etc.

# 4. Add your documents to RAG
cp ~/Documents/my_resume.docx data/resume.docx
cp ~/Documents/notes.txt data/knowledge/

# 5. Start JARVIS
python main.py
```

### Setup Script (setup.sh)

```bash
#!/bin/bash
echo "⚡ Installing JARVIS..."

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull AI model
ollama pull qwen3.5:4b

# Python environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

echo "✅ JARVIS is ready. Run: python main.py"
```

---

## ◈ Configuration

```yaml
# config.yaml

jarvis:
  name: "JARVIS"
  wake_word: "hey jarvis"

models:
  primary: "qwen3.5:4b"    # Single model — handles all tasks
  vision: "llava:7b"       # For screen reading
  speech: "whisper"        # For voice input

memory:
  rag_db_path: "./data/rag_db"
  history_db: "./data/history.db"
  knowledge_dir: "./data/knowledge"

telegram:
  token: "YOUR_BOT_TOKEN"
  allowed_user_id: 123456789   # Only YOU can control it

safety:
  require_approval_for:
    - file_delete
    - send_message
    - run_script
  blacklisted_paths:
    - "~/.ssh"
    - "~/passwords"
    - "/etc"
  max_actions_per_minute: 10
  dry_run: false             # Set true to test without executing
```

---

## ◈ Usage Examples

### Via Terminal
```bash
python main.py

> What can you do?
◈ I can control your computer, manage files, send messages,
  apply to jobs, search the web, and remember everything
  you tell me. All locally. What do you need?

> Organize my Downloads folder
◈ Scanning Downloads folder...
  → Sorting files by type
  → Moving files to categorized folders: Documents/ Images/ Videos/ Code/
  → Done ✓

> Apply to Python developer jobs on LinkedIn
◈ Searching LinkedIn for Python developer roles...
  → Reading job descriptions
  → Customizing resume and writing cover letter
  → Logging application to spreadsheet
  → Done ✓
```

### Via Telegram (from your phone)
```
You:    hey jarvis what files did i download today
JARVIS: You downloaded 3 files today:
        • invoice_nov.pdf (2.3MB) at 10:42am
        • project_brief.docx (445KB) at 2:15pm
        • dataset.csv (12MB) at 4:30pm
        Want me to organize them?

You:    yes move them to the right folders
JARVIS: ✅ Done — moved all 3 files to their folders.
```

### Via Python API
```python
from jarvis import Jarvis

j = Jarvis()

# Ask a question with RAG context from your files
answer = j.ask("What are my strongest Python skills?")

# Run a computer automation task
j.do("Open VS Code and create a new Python file called main.py")

# Use the job bot
j.career.apply_to_jobs(
    query="Python developer India",
    max_applications=10
)

# Add documents to memory
j.memory.add("~/Documents/my_notes.txt")
j.memory.add("~/Documents/resume.pdf")
```

---

## ◈ Safety System

JARVIS is powerful — so it has strict safety guardrails built in from day one.

```
SAFETY PRINCIPLES
─────────────────
1. Human approval required for all destructive actions
2. Blacklisted paths are never touched (SSH keys, passwords, /etc)
3. Every single action is logged with timestamp
4. Rate limiting prevents runaway loops
5. Kill switch stops everything instantly
6. Dry-run mode tests actions without executing
7. Only YOUR Telegram ID can send commands
```

```bash
# Emergency stop — kills all JARVIS processes instantly
python -m jarvis.safety.killswitch

# Or from Telegram:
/killswitch

# View action log
python -m jarvis.safety.logger --tail 50
```

---

## ◈ Hardware

| Component | Spec | Role |
|-----------|------|------|
| **GPU** | RTX 3050 4GB | GPU-accelerated LLM inference |
| **CPU** | i5-12500K | Automation, orchestration |
| **RAM** | 8GB | Model runtime + system |
| **OS** | Pop!_OS | Linux — optimized for AI dev |

---

## ◈ Roadmap

```
Phase 1 — BRAIN
  🔵 Ollama + Qwen 3.5:4B integration
  🔵 RAG system (ChromaDB + LangChain)
  � Task planner
  🔵 Conversation history (SQLite)

Phase 2 — SENSES
  🔵 Wake word detection
  🔵 Voice input (Whisper)
  🔵 Screen vision (LLaVA)
  🔵 File system watcher

Phase 3 — HANDS
  🔵 Computer control (PyAutoGUI)
  🔵 Browser automation (Playwright)
  🔵 Terminal agent (safe subprocess)
  🔵 File organizer

Phase 4 — CONNECT
  🔵 Telegram bot
  🔵 Discord bot
  🔵 Email automation (Gmail API)
  🔵 Web dashboard (FastAPI + React)

Phase 5 — JARVIS v1.0
  🔵 Job application bot
  🔵 GitHub automator
  🔵 Voice response (Piper TTS)
  🔵 Daily briefing system
  🔵 Public release 🚀
```

---

## ◈ Contributing

This is an open project. PRs, issues, and ideas are welcome.

```bash
# Fork the repo
# Create your feature branch
git checkout -b feature/your-feature-name

# Make your changes
# Write a clear commit message
git commit -m "feat: add voice response with Piper TTS"

# Push and open a PR
git push origin feature/your-feature-name
```

**Good first issues:**
- Add a new automation module
- Improve the safety guardrails
- Add support for a new messaging platform
- Write tests for existing modules
- Improve documentation

---

## ◈ Why Local AI?

Most AI tools send your data to the cloud. JARVIS doesn't.

```
Cloud AI                    │  JARVIS (Local)
────────────────────────────┼──────────────────────────
Sends data to servers       │  Everything stays on your PC
Costs money per token       │  ₹0 per month forever
Rate limited                │  Unlimited requests
Needs internet              │  Works offline
Can't automate your PC      │  Full computer control
Privacy concerns            │  100% private
```

---

## ◈ License

```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software to use, copy, modify, merge,
publish, distribute, and sublicense — subject to the conditions
in the LICENSE file.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

---

## ◈ Acknowledgements

Built on the shoulders of giants:

- [**Ollama**](https://ollama.ai) — Local LLM runtime
- [**Qwen**](https://github.com/QwenLM/Qwen) — The AI model powering JARVIS
- [**ChromaDB**](https://www.trychroma.com) — Vector database for RAG
- [**LangChain**](https://langchain.com) — RAG pipeline framework
- [**Playwright**](https://playwright.dev) — Browser automation
- [**Whisper**](https://github.com/openai/whisper) — Speech recognition
- [**Pop!_OS**](https://pop.system76.com) — The best Linux distro for AI dev

---

<div align="center">

```
◈ ─────────────────────────────────────────── ◈
         Built with obsession. Runs locally.
              No cloud. No limits. No cost.
◈ ─────────────────────────────────────────── ◈
```

**[⭐ Star this repo](https://github.com/yourusername/jarvis)** if you find it useful

![Visitors](https://img.shields.io/badge/Status-Building_in_Public-00bfff?style=for-the-badge&labelColor=0a0e1a)

</div>
