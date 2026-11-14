# dsh-floorplan-adapter

A [DeepSeek Harness](https://github.com/deepseek-ai/DeepSeek-Harness) (`dsh`) plugin that connects the open-source [Floorplan](https://github.com/haydenschmitty/floorplan) codebase mapper to DeepSeek, as an open-source alternative to Claude Code / Codex.

## What it does
This plugin acts as a bridge. It provides the "mechanical hands" (running Floorplan's Node.js scripts), while DeepSeek acts as the "brain" (reading code and writing the architecture).

The plugin registers three tools in `dsh`:
- **`floorplan_scan`**: Runs `scan.mjs` and returns a summary of files and HTTP routes.
- **`floorplan_build`**: Runs `build.mjs` to generate the interactive `index.html` map.
- **`floorplan_describe`**: Runs `describe.mjs` to generate worksheets, allowing DeepSeek to write human-readable descriptions for every file and route.

## Requirements
- Node.js 20+
- `pnpm` (used by `dsh plugin add`)
- A DeepSeek API key (`DEEPSEEK_API_KEY`)
- [Floorplan](https://github.com/haydenschmitty/floorplan) cloned locally at `~/floorplan`

## Install
```bash
npm install
npm run build
npx @deepseek-ai/dsh plugin --profile headless add "$(pwd)"
export DEEPSEEK_API_KEY="sk-..."
Usage
We provide a wrapper script that reduces terminal noise, shows a live progress bar, and saves a full log file.

bash
./scripts/dsh-progress.sh ~/path/to/your/project "Use floorplan_scan on ~/path/to/your/project. Follow the instructions in the tool result."
Progress Bar: Displays live progress from 5% to 100%.

Logs: Full reasoning and diagnostics are saved to <project>/floorplan/.cache/adapter.log.

Answer: The clean final output is saved to <project>/floorplan/.cache/answer.txt.

Layout
src/index.ts: Registers the three tools.

src/floorplan-runner.ts: Runs Floorplan's scripts as subprocesses.

src/progress.ts: Writes progress markers for the wrapper script.

scripts/dsh-progress.sh: The wrapper script for progress bars and logging.

License
MIT# dsh-floorplan-adapter
