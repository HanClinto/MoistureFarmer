# If we are on Windows, use the full path to llama-server
# Otherwise, use the llama-server command directly
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    LLAMASERVER_CMD="~/Downloads/llama-b5711-bin-win-cuda-12.4-x64/llama-server"
else
    LLAMASERVER_CMD="llama-server"
fi
# Enable flash-attention, default to port 8080, always use jinja template file for tool-calling
# Setting ctx-size to 0 loads the context size from the model itself
OPTS="-fa --port 8080 --jinja --ctx-size 0"

if ! command -v $LLAMASERVER_CMD &> /dev/null; then
    echo "llama-server could not be found. Please follow install instructions from https://github.com/ggml-org/llama.cpp?tab=readme-ov-file#quick-start"
    exit
fi

$LLAMASERVER_CMD $OPTS -hf bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M

# Other tested models ( Thanks, Ochafik! From https://gist.github.com/ochafik/9246d289b7d38d49e1ee2755698d6c79 )
# Native support for Llama 3.x, Mistral Nemo, Qwen 2.5, Hermes 3, Functionary 3.x, Firefunction v2...

# $LLAMASERVER_CMD --jinja -fa -hf bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M
# $LLAMASERVER_CMD --jinja -fa -hf bartowski/phi-4-GGUF:Q4_0
# $LLAMASERVER_CMD --jinja -fa -hf bartowski/Mistral-Nemo-Instruct-2407-GGUF:Q6_K_L
# $LLAMASERVER_CMD --jinja -fa -hf bartowski/functionary-small-v3.2-GGUF:Q4_K_M
# $LLAMASERVER_CMD --jinja -fa -hf bartowski/Hermes-3-Llama-3.1-8B-GGUF:Q4_K_M \
#  --chat-template-file <( python scripts/get_chat_template.py NousResearch/Hermes-3-Llama-3.1-8B tool_use )
# $LLAMASERVER_CMD --jinja -fa -hf bartowski/Llama-3.3-70B-Instruct-GGUF:Q4_K_M
# $LLAMASERVER_CMD --jinja -fa -hf bartowski/firefunction-v2-GGUF -hff firefunction-v2-Q5_K_M.gguf \
#  --chat-template-file <( python scripts/get_chat_template.py fireworks-ai/llama-3-firefunction-v2 tool_use )
# $LLAMASERVER_CMD --jinja -fa -hf bartowski/Hermes-2-Pro-Llama-3-8B-GGUF:Q4_K_M \
#  --chat-template-file <( python scripts/get_chat_template.py NousResearch/Hermes-2-Pro-Llama-3-8B tool_use )
