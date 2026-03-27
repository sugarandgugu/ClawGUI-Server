#!/bin/bash
# Start vLLM API server for MAI-UI
# Requirements: vllm>=0.11.0, transformers>=4.57.0

MODEL_PATH="Tongyi-MAI/MAI-UI-2B"
MODEL_NAME="MAI-UI-2B"
PORT=8001
GPU_IDS="0,1"
TP_SIZE=2
GPU_MEM_UTIL=0.60
MAX_MODEL_LEN=25600

# Log
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/log"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/maiui_serve.log"

CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=$GPU_IDS \
nohup python -m vllm.entrypoints.openai.api_server \
    --model $MODEL_PATH \
    --served-model-name $MODEL_NAME \
    --host 0.0.0.0 \
    --port $PORT \
    --gpu_memory_utilization $GPU_MEM_UTIL \
    --tensor-parallel-size $TP_SIZE \
    --max-model-len $MAX_MODEL_LEN \
    --trust-remote-code > "${LOG_FILE}" 2>&1 &

echo "vLLM server started, PID: $!, log: ${LOG_FILE}"
