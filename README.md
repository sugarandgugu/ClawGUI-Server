# ClawGUI-Server

[English](README_EN.md) | 中文

基于 [MobileWorld](https://github.com/Tongyi-MAI/MobileWorld) 构建的虚拟 Android 容器服务，为 [ClawGUI-RL](https://github.com/ZJU-REAL/ClawGUI/tree/master/clawgui-rl) 提供 online RL 训练环境，同时提供多种评估脚本。

## Overview

ClawGUI-Server 通过 Docker 容器化的 Android 模拟器，为 GUI Agent 提供可复现的交互环境。主要功能：

- **Online RL 训练**：为 OpenGUI-RL 提供虚拟容器环境进行在线强化学习训练
- **GUI-Only 评估**：测试不含 Google 服务的 GUI 任务
- **GUI-Only + Google 评估**：测试包含 Google 任务（Chrome/Maps 等）的完整 GUI 评估
- **Google-Only 评估**：仅测试 Google 相关任务

## 安装

### 环境要求

- Docker（需 privileged 权限）
- KVM 支持
- Python 3.12+
- Linux

### 安装依赖

```bash
git clone https://github.com/sugarandgugu/OpenGUI-Server
cd OpenGUI-Server
uv sync
```

### 环境配置

```bash
cp .env.example .env
```

编辑 `.env` 填入所需的 API Key：

```bash
API_KEY=your_api_key              # Agent 模型的 API Key
DASHSCOPE_API_KEY=xxx             # MCP 任务需要
MODELSCOPE_API_KEY=xxx            # MCP 任务需要
USER_AGENT_API_KEY=xxx            # Agent-User 交互任务需要
USER_AGENT_BASE_URL=xxx
USER_AGENT_MODEL=xxx
```

## 启动模拟器

### 1. 检查环境 & 拉取 Docker 镜像

```bash
sudo uv run mw env check
```

> **注意**：`env check` 会依次检查 Docker 是否安装及其权限、KVM 是否安装及其权限、`.env` 是否正确填写。只有所有检查通过后，才会提示你是否拉取镜像。如果暂时没有 API Key，可以先随意填写（例如全部填 `11111`），后续再修改。

你也可以手动拉取 Docker 镜像。由于镜像托管在 `ghcr.io`，国内网络可能较慢，可以在 `/etc/docker/daemon.json` 中配置镜像加速或代理：

```json
{
  "registry-mirrors": ["https://docker.nju.edu.cn"]
}
```

配置后重启 Docker：

```bash
sudo systemctl restart docker
```

然后拉取镜像：

```bash
docker pull ghcr.io/tongyi-mai/mobile_world:latest
```

### 2. 启动容器

```bash
uv run mw env run \
    --count 8 \
    --backend-start-port 7000 \
    --viewer-start-port 8000 \
    --vnc-start-port 5900 \
    --adb-start-port 5600 \
    --launch-interval 3
```

每个容器内含完整的 Android 模拟器 + 应用后端（Mattermost、Mastodon 等）+ API Server。

### 3. 查看容器状态

```bash
sudo uv run mw env list
```

### 4. 销毁容器

```bash
sudo uv run mw env rm --all
```

## 模型部署

使用 vLLM 部署模型服务，示例脚本在 `scripts/` 目录下：

```bash
# 部署 GUI-Owl-1.5-2B
bash scripts/guiown_serve.sh

# 部署 MAI-UI-2B（或 online RL checkpoint）
bash scripts/maiui_serve.sh
```

## 评估脚本

评估入口脚本为 `start.sh`，包含以下几种评测模式：

### 1. GUI-Only 任务（排除 Google）

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

### 2. Google-Only 任务

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

### 3. MCP 任务

通过 `--enable-mcp` 参数启用 MCP（Model Context Protocol）相关任务的评估：

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

> ⚠️ **注意**：MCP 任务评估尚未经过完整测试，请根据实际情况调整参数。需要在 `.env` 中配置 `DASHSCOPE_API_KEY` 和 `MODELSCOPE_API_KEY`。

### 4. User-Interaction 任务

通过 `--enable-user-interaction` 参数启用 Agent-User 交互任务的评估：

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

> ⚠️ **注意**：User-Interaction 任务评估尚未经过完整测试，请根据实际情况调整参数。需要在 `.env` 中配置 `USER_AGENT_API_KEY`、`USER_AGENT_BASE_URL` 和 `USER_AGENT_MODEL`。

### 5. 指定单个/多个任务

```bash
# 单个任务
uv run mw eval \
    --agent_type gui_owl_1_5 \
    --task ChromeSearchBeijingWeatherTask \
    --max_round 50 \
    --model_name GUI-Owl15-2B \
    --llm_base_url http://YOUR_HOST:8001/v1 \
    --log_file_root traj_logs/single_task

# 多个任务（逗号分隔）
uv run mw eval \
    --agent_type gui_owl_1_5 \
    --task CameraOpenSelfieCamera_0,ClockCreateAlarm_0 \
    ...
```

## 测试 Server API

启动容器后，可以运行测试脚本验证 API Server 是否正常工作：

```bash
python test_server_api.py
```

该脚本会依次测试健康检查（`/health`）、控制器初始化（`/init`）、任务初始化（`/task/init`）和截图（`/screenshot`）等核心接口。

## 查看日志

```bash
uv run mw logs view --log_dir traj_logs/your_eval_dir
```

例如：

```bash
uv run mw logs view --log_dir traj_logs/qwen3_vl_logs
```

会在 `http://localhost:8760` 启动可视化日志查看器，可以查看评估轨迹和结果。

## 📱 真机测试

除了容器化的模拟器环境，MobileWorld 还支持在真实 Android 手机上运行前沿模型（如 Gemini、Claude、Qwen 等），实现端到端的移动端 Agent 评估。

### 前提条件

- 一台通过 USB 连接的 Android 手机
- 本机已安装 ADB（Android Debug Bridge）
- 待测试模型的 API Key

### 第 1 步：安装 ADB

前往 [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools?hl=zh-cn) 下载并解压。

macOS / Linux：

```bash
# 假设解压到 ~/Downloads/platform-tools
export PATH=${PATH}:~/Downloads/platform-tools
```

Windows 用户请参考官方文档进行配置。

### 第 2 步：连接手机并开启 USB 调试

1. **开启开发者模式**：进入 设置 > 关于手机 > 版本号，连续点击约 10 次，直到提示"已进入开发者模式"。
2. **开启 USB 调试**：进入 设置 > 开发者选项 > USB 调试，开启即可。部分设备可能需要重启。
3. **验证连接**：

```bash
adb devices

# 预期输出：
# List of devices attached
# <your_device_id>   device
```

### 第 3 步：安装 ADB Keyboard（可选）

ADB Keyboard 用于文本输入。下载 `ADBKeyboard.apk` 后安装到设备：

```bash
adb install ADBKeyboard.apk
adb shell ime enable com.android.adbkeyboard/.AdbIME
```

> **注意**：此步骤为可选，MobileWorld 会在需要时自动安装。

### 第 4 步：启动 MobileWorld Server

```bash
uv run mobile-world server
```

这将启动后端 API Server，作为模型与设备之间的桥梁。[OpenGUI-RL](../OpenGUI/opengui-rl) 也通过该 Server 来调用真实手机进行在线训练。

### 第 5 步：在真机上运行任务

```bash
uv run mw test "set an alarm at 8:00 am" \
    --agent-type general_e2e \
    --model_name anthropic/claude-sonnet-4-5 \
    --llm_base_url https://openrouter.ai/api/v1 \
    --aw-host http://127.0.0.1:6800 \
    --api_key YOUR_API_KEY
```

将 `--model_name`、`--llm_base_url` 和 `--api_key` 替换为你要使用的模型和凭证，任何 OpenAI 兼容的 API 端点均可。`--agent-type general_e2e` 适用于大部分前沿模型；如使用 Seed-2.0-Pro，建议使用 `--agent-type seed_agent` 以获得更好的效果。

### 测试真机 Server API

启动 Server 后，可以运行测试脚本验证真机连接是否正常：

```bash
python test_true_device.py
```

> 运行前请先通过 `adb devices` 查看设备 ID，然后修改脚本中的 `DEVICE` 变量。

该脚本会测试设备初始化（`/init`）、健康检查（`/health`）和截图（`/screenshot`）等接口。

## 项目结构

```
ClawGUI-Server/
├── start.sh                # 评测启动脚本
├── scripts/                # 模型部署 & 评测脚本
├── docker/                 # Docker 镜像构建 & 模拟器启动
├── src/mobile_world/       # 核心源码
│   ├── agents/             # Agent 实现（GUI-Owl, MAI-UI, Qwen3-VL 等）
│   ├── core/               # CLI, 评测引擎, API Server
│   ├── runtime/            # Android 控制, 容器管理
│   └── tasks/              # 任务定义（200+ 任务，覆盖 20+ 应用）
├── docs/                   # 文档
└── resources/              # 应用资源文件
```

## Server 实现

如果想了解 Server 的具体实现细节，可以查看 [`server.py`](https://github.com/Tongyi-MAI/MobileWorld/blob/main/src/mobile_world/core/server.py)，其中封装了截图、操作执行、任务管理等核心命令。

## 致谢

本项目基于 [MobileWorld](https://github.com/Tongyi-MAI/MobileWorld)（[Paper](https://arxiv.org/abs/2512.19432)）构建。
