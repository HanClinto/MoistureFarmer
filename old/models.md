Small LLMs for investigation / experimentation:

smollm2-360m-instruct-q8_0.gguf
HF repo: ngxson/SmolLM2-360M-Instruct-Q8_0-GGUF
Size: 368.5 MB
llama-cli --hf-repo ngxson/SmolLM2-360M-Instruct-Q8_0-GGUF --hf-file smollm2-360m-instruct-q8_0.gguf -p "The meaning to life and the universe is"

llama-server --hf-repo ngxson/SmolLM2-360M-Instruct-Q8_0-GGUF --hf-file smollm2-360m-instruct-q8_0.gguf

qwen2.5-0.5b-instruct-q8_0.gguf
HF repo: Qwen/Qwen2.5-0.5B-Instruct-GGUF
Size: 644.4 MB

llama-server --hf-repo Qwen/Qwen2.5-0.5B-Instruct-GGUF --hf-file qwen2.5-0.5b-instruct-q8_0.gguf

llama-3.2-1b-instruct-q4_k_m.gguf
HF repo: hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF
Size: 770.3 MB

llama-server --hf-repo hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF --hf-file llama-3.2-1b-instruct-q4_k_m.gguf


DeepSeek-R1-Distill-Qwen-1.5B-Q3_K_M.gguf
HF repo: bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF
Size: 881.6 MB

qwen2-1_5b-instruct-q4_k_m-(shards).gguf
HF repo: ngxson/wllama-split-models
Size: 940.4 MB

smollm2-1.7b-instruct-q4_k_m.gguf
HF repo: ngxson/SmolLM2-1.7B-Instruct-Q4_K_M-GGUF
Size: 1006.7 MB

gemma-2-2b-it-abliterated-Q4_K_M-(shards).gguf
HF repo: ngxson/wllama-split-models
Size: 1.6 GB

neuralreyna-mini-1.8b-v0.3.q4_k_m-(shards).gguf
HF repo: ngxson/wllama-split-models
Size: 1.1 GB

Phi-3.1-mini-128k-instruct-Q3_K_M-(shards).gguf
HF repo: ngxson/wllama-split-models
Size: 1.8 GB

meta-llama-3.1-8b-instruct-abliterated.Q2_K-(shards).gguf
HF repo: ngxson/wllama-split-models
Size: 3.0 GB

Meta-Llama-3.1-8B-Instruct-Q2_K-(shards).gguf
HF repo: ngxson/wllama-split-models
Size: 3.0 GB

llama-server --jinja -fa -hf bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M
llama-server --jinja -fa -hf bartowski/Mistral-Nemo-Instruct-2407-GGUF:Q6_K_L
llama-server --jinja -fa -hf bartowski/Llama-3.3-70B-Instruct-GGUF:Q4_K_M