# Quickstart: Get Running with LOLA OS V1

## Install
1. Clone: `git clone https://github.com/lola-os/open-core && cd lola-os`
2. `poetry install` (Python 3.12+).
3. `.env`: Copy sample, add Gemini key (free: [AI Studio](https://aistudio.google.com)).

## Phase 1: Utils Demo
`cd examples/version_1/utils_standalone && python agent.py`
- Loads config (Gemini default), logs JSON.
- Override: Edit .env (beats YAML).

## Full V1 (Post-Phases)
`lola create my-agent --template react && lola run --query "Check ETH balance"`

Tutorials: [First Agent](tutorials/first_agent.md) (stub). API: [Reference](api_reference.md).

Troubleshoot: Keys? See integration_guide.md.