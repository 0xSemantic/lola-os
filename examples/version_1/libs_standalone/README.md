# Libs Standalone: LiteLLM Routing (LOLA OS V1 Example)

## Overview
Zero-mastery demo of LLMProxy: Routes to Gemini default, fallback on fail, cost est. Why? V1 agents need reliable LLM (no lock-in). Run: <30s. Output: Response + log/cost.

## Prerequisites
- Poetry/Python 3.12+.
- Free Gemini key [](https://aistudio.google.com).

## Setup
1. `cd examples/version_1/libs_standalone`
2. `cp .env.sample .env` & fill GEMINI_API_KEY.
3. `poetry install` (root).

## Run
`python agent.py`

Expected: "Gemini response: LOLA OS is a sovereign operating system..." + "Cost est: 0.0001"

## Walkthrough
1. `load_config()`: Model/key from YAML/.env.
2. `LLMProxy()`: Init with model, fallbacks.
3. `complete()`: Calls litellm, fallback if fail.
4. `cost_estimate()`: model_cost for budget.

**Exercise 1:** Fallback. Set .env model="fail", rerun—uses "openai/gpt-4o-mini" (needs OpenAI key).
**Exercise 2:** Custom prompt. Edit "What is LOLA OS?" to "Summarize blockchain", see response.

## Troubleshooting
- API error? Check key/rate (free tier 15RPM). Log: "LLM fail".
- No response? Fallback chain fail—add key for "openai".

Best: Config for sovereignty—switch models easy.

## Next Steps
Integrate: See libs_combined for crawl+LLM. Phase 3: Core graph uses proxy.

Files: agent.py (main), config.yaml, .env.sample, README.