# If we are on Windows, use the full path to llama-server
# Otherwise, use the llama-server command directly
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    LLAMASERVER_CMD="~/Downloads/llama-b5711-bin-win-cuda-12.4-x64/llama-server"
else
    LLAMASERVER_CMD="llama-server"
fi
$LLAMASERVER_CMD --jinja -fa -hf bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M