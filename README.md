# Mappa Linux Agent

Mappa is a lightweight, agentic Linux terminal assistant powered by Google Gemini 2.5 Flash. It helps you execute terminal commands using natural language.

## Installation

Run this one-liner to install:

```bash
git clone https://github.com/urabhay10/mappalinux.git
cd mappalinux
./setup.sh
```

## Usage

1. **Set your API Key** (first time only):
   ```bash
   export GEMINI_API_KEY="your_api_key"
   ```
   *Or just run the tool, and it will prompt you.*

2. **Run Commands**:
   ```bash
   ./mappa list files in current directory
   ./mappa create a python script that prints hello world
   ./mappa check disk usage
   ```

## Features

- **Natural Language Control**: Just say what you want.
- **Auto-Execution**: Generates and runs commands (with feedback loop).
- **Production Ready**: Clean, minimal code.
- **Secure**: Handles `sudo` via standard input; API keys strictly managed.

## Requirements

- Python 3
- Linux/macOS
- Google Gemini API Key
