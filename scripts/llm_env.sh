# shellcheck shell=bash
# Sourced by scripts/*/run_agent.sh. Configures Antigravity CLI (`agy`) for
# Gemini API key auth (`GEMINI_API_KEY`) or a custom Gemini-compatible endpoint
# (`GOOGLE_GEMINI_BASE_URL` with `LLM_API_KEY`) when llm_base_url is set.
export PATH="$HOME/.local/bin:$PATH"
if [ -n "${LLM_BASE_URL:-}" ]; then
  if [ -z "${LLM_API_KEY:-}" ]; then
    echo "llm_base_url is set, but the LLM_API_KEY secret is empty" >&2
    return 1
  fi
  if [ -z "${MODEL:-}" ]; then
    echo "llm_base_url is set: put the endpoint's model name in the model input" >&2
    return 1
  fi
  export GOOGLE_GEMINI_BASE_URL="${LLM_BASE_URL%/}" GEMINI_API_KEY="$LLM_API_KEY"
  llm_host=${LLM_BASE_URL#*://}; llm_host=${llm_host%%/*}
  echo "Model $MODEL through ${llm_host##*@}"
fi

