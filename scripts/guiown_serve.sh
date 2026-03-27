#!/bin/bash
# Install vLLM
# ps -u tangfei -o pid,cmd | grep -i vllm
# Source conda configuration
source /home/tangfei/anaconda3/etc/profile.d/conda.sh

conda activate verl-agent
# pip install vllm  # vllm>=0.11.0 and transformers>=4.57.0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/log"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/guiown15_serve_2B.log"
# GUI-OWL-2B: /home/tangfei/models/GUI-Owl-1.5-2B-Instruct
# /home/shenyl/hf/model/mPLUG/GUI-Owl-7B 
# Start vLLM API server (replace MODEL_PATH with your local model path or HuggingFace model ID)
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 nohup python -m vllm.entrypoints.openai.api_server \
    --model /home/tangfei/models/GUI-Owl-1.5-2B-Instruct \
    --served-model-name GUI-Owl15-2B \
    --host 0.0.0.0 \
    --gpu_memory_utilization 0.60 \
    --port 8001 \
    --tensor-parallel-size 2 \
    --trust-remote-code > "${LOG_FILE}" 2>&1 &

echo "vLLM server started in background, PID: $!"
echo "Log file: ${LOG_FILE}"