# ClawGUI-Server

English | [中文](README.md)

A virtual Android container service built on [MobileWorld](https://github.com/Tongyi-MAI/MobileWorld), providing online RL training environments for [ClawGUI-RL](https://github.com/ZJU-REAL/ClawGUI/tree/master/clawgui-rl) along with various evaluation scripts.

## Overview

ClawGUI-Server provides reproducible interaction environments for GUI Agents through Docker-containerized Android emulators. Key features:

- **Online RL Training**: Virtual container environments for online reinforcement learning
- **GUI-Only Evaluation**: Test GUI tasks excluding Google services
- **GUI-Only + Google Evaluation**: Full GUI evaluation including Google tasks (Chrome/Maps, etc.)
- **Google-Only Evaluation**: Test only Google-related tasks

## Installation

### Requirements

- Docker (privileged mode required)
- KVM support
- Python 3.12+
- Linux

### Install Dependencies

```bash
git clone https://github.com/sugarandgugu/OpenGUI-Server
cd OpenGUI-Server
uv sync
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env` and fill in the required API keys:

```bash
API_KEY=your_api_key              # Agent model API Key
DASHSCOPE_API_KEY=xxx             # Required for MCP tasks
MODELSCOPE_API_KEY=xxx            # Required for MCP tasks
USER_AGENT_API_KEY=xxx            # Required for Agent-User interaction tasks
USER_AGENT_BASE_URL=xxx
USER_AGENT_MODEL=xxx
```

## Starting the Emulator

### 1. Check Environment & Pull Docker Image

```bash
sudo uv run mw env check
```

> **Note**: `env check` will verify Docker installation and permissions, KVM installation and permissions, and whether `.env` is properly configured. The image pull prompt will only appear after all checks pass. If you don't have API keys yet, you can fill in placeholder values (e.g., `11111` for all fields) and update them later.

You can also manually pull the Docker image. Since the image is hosted on `ghcr.io`, you may want to configure a registry mirror or proxy in `/etc/docker/daemon.json` for faster downloads:

```json
{
  "registry-mirrors": ["https://docker.nju.edu.cn"]
}
```

Then restart Docker:

```bash
sudo systemctl restart docker
```

Pull the image:

```bash
docker pull ghcr.io/tongyi-mai/mobile_world:latest
```

### 2. Start Containers

```bash
uv run mw env run \
    --count 8 \
    --backend-start-port 7000 \
    --viewer-start-port 8000 \
    --vnc-start-port 5900 \
    --adb-start-port 5600 \
    --launch-interval 3
```

Each container includes a full Android emulator + application backends (Mattermost, Mastodon, etc.) + API Server.

### 3. Check Container Status

```bash
sudo uv run mw env list
```

### 4. Remove Containers

```bash
sudo uv run mw env rm --all
```

## Model Deployment

Deploy model services using vLLM. Example scripts are in the `scripts/` directory:

```bash
# Deploy GUI-Owl-1.5-2B
bash scripts/guiown_serve.sh

# Deploy MAI-UI-2B (or online RL checkpoint)
bash scripts/maiui_serve.sh
```

## Evaluation Scripts

The evaluation entry script is `start.sh`, supporting the following modes:

### 1. GUI-Only Tasks (Excluding Google)

```bash
uv run mw eval \
    --agent_type gui_owl_1_5 \
    --task ALL \
    --max_round 50 \
    --model_name GUI-Owl15-2B \
    --llm_base_url http://YOUR_HOST:8001/v1 \
    --step_wait_time 3 \
    --log_file_root traj_logs/gui_only_eval
```

### 2. Google-Only Tasks

```bash
uv run mw eval \
    --agent_type gui_owl_1_5 \
    --task ALL \
    --google-only \
    --max_round 50 \
    --model_name GUI-Owl15-2B \
    --llm_base_url http://YOUR_HOST:8001/v1 \
    --step_wait_time 3 \
    --log_file_root traj_logs/google_only_eval
```

### 3. MCP Tasks

Enable MCP (Model Context Protocol) task evaluation with the `--enable-mcp` flag:

```bash
uv run mw eval \
    --agent_type gui_owl_1_5 \
    --task ALL \
    --enable-mcp \
    --max_round 50 \
    --model_name GUI-Owl15-2B \
    --llm_base_url http://YOUR_HOST:8001/v1 \
    --step_wait_time 3 \
    --log_file_root traj_logs/mcp_eval
```

> ⚠️ **Note**: MCP task evaluation has not been fully tested yet. Please adjust parameters as needed. Requires `DASHSCOPE_API_KEY` and `MODELSCOPE_API_KEY` to be configured in `.env`.

### 4. User-Interaction Tasks

Enable Agent-User interaction task evaluation with the `--enable-user-interaction` flag:

```bash
uv run mw eval \
    --agent_type gui_owl_1_5 \
    --task ALL \
    --enable-user-interaction \
    --max_round 50 \
    --model_name GUI-Owl15-2B \
    --llm_base_url http://YOUR_HOST:8001/v1 \
    --step_wait_time 3 \
    --log_file_root traj_logs/user_interaction_eval
```

> ⚠️ **Note**: User-Interaction task evaluation has not been fully tested yet. Please adjust parameters as needed. Requires `USER_AGENT_API_KEY`, `USER_AGENT_BASE_URL`, and `USER_AGENT_MODEL` to be configured in `.env`.

### 5. Specify Single/Multiple Tasks

```bash
# Single task
uv run mw eval \
    --agent_type gui_owl_1_5 \
    --task ChromeSearchBeijingWeatherTask \
    --max_round 50 \
    --model_name GUI-Owl15-2B \
    --llm_base_url http://YOUR_HOST:8001/v1 \
    --log_file_root traj_logs/single_task

# Multiple tasks (comma-separated)
uv run mw eval \
    --agent_type gui_owl_1_5 \
    --task CameraOpenSelfieCamera_0,ClockCreateAlarm_0 \
    ...
```

## Testing the Server API

After starting the containers, you can run the test script to verify the API Server is working properly:

```bash
python test_server_api.py
```

This script tests the core endpoints including health check (`/health`), controller initialization (`/init`), task initialization (`/task/init`), and screenshot (`/screenshot`).

## Viewing Logs

```bash
uv run mw logs view --log_dir traj_logs/your_eval_dir
```

For example:

```bash
uv run mw logs view --log_dir traj_logs/qwen3_vl_logs
```

This launches a visual log viewer at `http://localhost:8760`, where you can inspect evaluation trajectories and results.

## 📱 Testing on Real Devices

Beyond the containerized emulator environment, MobileWorld supports running frontier models on real physical Android phones. This lets you evaluate models like Gemini, Claude, Qwen, and others as true end-to-end mobile agents.

### Prerequisites

- A physical Android phone connected via USB
- ADB (Android Debug Bridge) installed on your local machine
- An API key for the model you want to test

### Step 1: Install ADB

Download the official [ADB Platform-Tools](https://developer.android.com/tools/releases/platform-tools?hl=zh-cn) and extract it.

macOS / Linux:

```bash
# Assuming extracted to ~/Downloads/platform-tools
export PATH=${PATH}:~/Downloads/platform-tools
```

Windows: Refer to the official documentation for configuration steps.

### Step 2: Connect Your Phone & Enable USB Debugging

1. **Enable Developer Mode**: Go to Settings > About Phone > Build Number and tap rapidly ~10 times until you see "Developer mode has been enabled."
2. **Enable USB Debugging**: Go to Settings > Developer Options > USB Debugging and enable it. Some devices may require a restart.
3. **Verify the connection**:

```bash
adb devices

# Expected output:
# List of devices attached
# <your_device_id>   device
```

### Step 3: Install ADB Keyboard (Optional)

ADB Keyboard is needed for text input. Download the `ADBKeyboard.apk` and install it on your device:

```bash
adb install ADBKeyboard.apk
adb shell ime enable com.android.adbkeyboard/.AdbIME
```

> **Note**: This step is optional — MobileWorld will install it automatically if not present.

### Step 4: Start the MobileWorld Server

```bash
uv run mobile-world server
```

This starts the backend API server that bridges the model and the device. [OpenGUI-RL](../OpenGUI/opengui-rl) also uses this server to interact with real phones for online training.

### Step 5: Run a Task on Your Real Device

```bash
uv run mw test "set an alarm at 8:00 am" \
    --agent-type general_e2e \
    --model_name anthropic/claude-sonnet-4-5 \
    --llm_base_url https://openrouter.ai/api/v1 \
    --aw-host http://127.0.0.1:6800 \
    --api_key YOUR_API_KEY
```

Replace `--model_name`, `--llm_base_url`, and `--api_key` with the model and credentials you want to use. Any OpenAI-compatible endpoint works. The `--agent-type general_e2e` prompt works across most frontier models. For Seed-2.0-Pro, use `--agent-type seed_agent` for better performance.

### Testing the Real Device Server API

After starting the server, you can run the test script to verify the real device connection:

```bash
python test_true_device.py
```

> Before running, use `adb devices` to find your device ID and update the `DEVICE` variable in the script.

This script tests device initialization (`/init`), health check (`/health`), and screenshot (`/screenshot`) endpoints.

## Project Structure

```
ClawGUI-Server/
├── start.sh                # Evaluation launch script
├── scripts/                # Model deployment & evaluation scripts
├── docker/                 # Docker image build & emulator launch
├── src/mobile_world/       # Core source code
│   ├── agents/             # Agent implementations (GUI-Owl, MAI-UI, Qwen3-VL, etc.)
│   ├── core/               # CLI, evaluation engine, API Server
│   ├── runtime/            # Android control, container management
│   └── tasks/              # Task definitions (200+ tasks, 20+ apps)
├── docs/                   # Documentation
└── resources/              # Application resource files
```

## Server Implementation

To understand how the server works under the hood, check out [`server.py`](https://github.com/Tongyi-MAI/MobileWorld/blob/main/src/mobile_world/core/server.py), which encapsulates core commands for screenshots, action execution, task management, and more.

## Acknowledgements

This project is built upon [MobileWorld](https://github.com/Tongyi-MAI/MobileWorld) ([Paper](https://arxiv.org/abs/2512.19432)).
