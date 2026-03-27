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
LOG_FILE="${LOG_DIR}/maiui_serve_2B_gigpo_exp1_step15.log"
MODEL_PATH="/home/shenyl/hf/model/Tongyi-MAI/MAI-UI-2B"
# MODEL_PATH="/home/tangfei/online_rl_exps/checkpoints/online_rl_mobile_world/grpo_4_2_3_20/global_step_20/hf"
# /home/tangfei/online_rl_exps/maiui2b_exp6_1080p_wo_step_reward/global_step_5/hf
# MODEL_PATH="/home/tangfei/online_rl_exps/maiui2b_exp6_1080p_wo_step_reward/global_step_20/hf"
# MODEL_PATH="/home/tangfei/online_rl_exps/gigpo_maiui2b_exp1/global_step_15/hf"
# Start vLLM API server (replace MODEL_PATH with your local model path or HuggingFace model ID)
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 nohup python -m vllm.entrypoints.openai.api_server \
    --model ${MODEL_PATH} \
    --served-model-name MAI-UI-2B \
    --host 0.0.0.0 \
    --gpu_memory_utilization 0.60 \
    --port 8001 \
    --tensor-parallel-size 2 \
    --max-model-len 25600 \
    --trust-remote-code > "${LOG_FILE}" 2>&1 &

echo "vLLM server started in background, PID: $!"
echo "Log file: ${LOG_FILE}"

# 8102 step 20
# 8101 step 15

