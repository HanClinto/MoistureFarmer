# If we are on Windows, use the full path to uvicorn
# Otherwise, use the uvicorn command directly
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    UVICORN_CMD="/c/Python313/Scripts/uvicorn.exe"
else
    UVICORN_CMD="uvicorn"
fi
# Clear our logs folder
rm logs/*.json

MF_DEFAULT_SCENARIO="$(dirname "$0")/scenarios/example_scenario.json" $UVICORN_CMD webgui.server:app --reload
