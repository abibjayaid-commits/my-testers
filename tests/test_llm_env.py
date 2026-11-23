"""scripts/llm_env.sh: Gemini API key default or custom Gemini-compatible endpoint (llm_base_url input)."""
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOWN = ("GOOGLE_GEMINI_BASE_URL", "GEMINI_API_KEY")


def source(show=True, **env):
    """Sources the helper like run_agent.sh does, then prints the variables it may change."""
    clean = {k: v for k, v in os.environ.items()
             if not k.startswith(("GOOGLE_GEMINI_", "GEMINI_", "LLM_")) and k != "MODEL"}
    script = f'source "{ROOT / "scripts/llm_env.sh"}" || exit 3'
    if show:
        script += "".join(f'; echo "{v}=${{{v}-<unset>}}"' for v in SHOWN)
    return subprocess.run(["bash", "-c", script], env={**clean, **env}, capture_output=True, text=True)


def values(out):
    return dict(line.split("=", 1) for line in out.stdout.splitlines() if "=" in line)


class LlmEnv(unittest.TestCase):
    def test_gemini_stays_when_no_base_url(self):
        out = source(GEMINI_API_KEY="AIza-test", MODEL="gemini-3.8-flash-high")
        self.assertEqual(out.returncode, 0, out.stderr)
        v = values(out)
        self.assertEqual(v["GEMINI_API_KEY"], "AIza-test")
        self.assertEqual(v["GOOGLE_GEMINI_BASE_URL"], "<unset>")

    def test_provider_sets_base_url_and_key(self):
        out = source(LLM_BASE_URL="https://proxy.example.com/v1/", LLM_API_KEY="sk-provider",
                     MODEL="gemini-3.8-flash-high", GEMINI_API_KEY="AIza-old")
        self.assertEqual(out.returncode, 0, out.stderr)
        v = values(out)
        self.assertEqual(v["GOOGLE_GEMINI_BASE_URL"], "https://proxy.example.com/v1")
        self.assertEqual(v["GEMINI_API_KEY"], "sk-provider")

    def test_log_shows_the_host_never_the_key(self):
        out = source(show=False, LLM_BASE_URL="https://user:pw@openrouter.ai/api", LLM_API_KEY="sk-provider",
                     MODEL="gemini-3.8-flash-high")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), "Model gemini-3.8-flash-high through openrouter.ai")
        self.assertNotIn("sk-provider", out.stdout + out.stderr)
        self.assertNotIn("pw", out.stdout + out.stderr)

    def test_missing_key_stops_the_agent(self):
        out = source(LLM_BASE_URL="https://proxy.example.com/v1", MODEL="gemini-3.8-flash-high")
        self.assertEqual(out.returncode, 3)
        self.assertIn("LLM_API_KEY", out.stderr)

    def test_empty_model_with_base_url_stops_the_agent(self):
        out = source(LLM_BASE_URL="https://proxy.example.com/v1", LLM_API_KEY="k", MODEL="")
        self.assertEqual(out.returncode, 3)
        self.assertIn("model input", out.stderr)


if __name__ == "__main__":
    unittest.main()
