#!/usr/bin/env bash
# --------------------------------------------------------------
# LOLA OS – V1 folder / file skeleton creator
# --------------------------------------------------------------
# • Creates every folder and empty file that the blueprint lists.
# • **Never overwrites** existing files (uses `mkdir -p` and `touch` only
#   when the target does not exist).
# • Works on Ubuntu 24 (or any POSIX shell).
# --------------------------------------------------------------

set -euo pipefail   # safe mode

# ---- Helper: create dir + file only if missing -----------------
create_file() {
    local path="$1"
    if [[ ! -f "$path" ]]; then
        echo "Creating $path"
        mkdir -p "$(dirname "$path")"
        touch "$path"
    else
        echo "Skipping (already exists): $path"
    fi
}

# ---- Root files ------------------------------------------------
create_file "README.md"
create_file "pyproject.toml"
create_file "LICENSE"
create_file ".gitignore"

# ---- .github/workflows -----------------------------------------
create_file ".github/workflows/test.yml"
create_file ".github/workflows/lint.yml"

# ---- docs ------------------------------------------------------
create_file "docs/index.md"
create_file "docs/quickstart.md"
create_file "docs/concepts.md"
create_file "docs/integration_guide.md"
create_file "docs/api_reference.md"
create_file "docs/changelog.md"
create_file "docs/diagrams/.gitkeep"   # keep empty diagrams folder

# ---- docs/tutorials --------------------------------------------
create_file "docs/tutorials/first_agent.md"
create_file "docs/tutorials/onchain_tools.md"

# ---- examples (version_1 placeholders) -------------------------
# easy
for i in $(seq -w 1 8); do
    create_file "examples/version_1/easy/0${i}_placeholder/agent.py"
    create_file "examples/version_1/easy/0${i}_placeholder/config.yaml"
    create_file "examples/version_1/easy/0${i}_placeholder/requirements.txt"
    create_file "examples/version_1/easy/0${i}_placeholder/.env.sample"
    create_file "examples/version_1/easy/0${i}_placeholder/README.md"
done

# moderate
for i in $(seq -w 1 8); do
    create_file "examples/version_1/moderate/0${i}_placeholder/agent.py"
    create_file "examples/version_1/moderate/0${i}_placeholder/config.yaml"
    create_file "examples/version_1/moderate/0${i}_placeholder/requirements.txt"
    create_file "examples/version_1/moderate/0${i}_placeholder/.env.sample"
    create_file "examples/version_1/moderate/0${i}_placeholder/README.md"
done

# advanced
for i in $(seq -w 1 8); do
    create_file "examples/version_1/advanced/0${i}_placeholder/agent.py"
    create_file "examples/version_1/advanced/0${i}_placeholder/config.yaml"
    create_file "examples/version_1/advanced/0${i}_placeholder/requirements.txt"
    create_file "examples/version_1/advanced/0${i}_placeholder/.env.sample"
    create_file "examples/version_1/advanced/0${i}_placeholder/README.md"
done

# ---- tests ------------------------------------------------------
create_file "tests/test_core.py"
create_file "tests/test_agents.py"
create_file "tests/test_tools.py"
create_file "tests/test_chains.py"
create_file "tests/test_agnostic.py"
create_file "tests/test_libs.py"
create_file "tests/test_utils.py"
create_file "tests/integration/.gitkeep"

# ---- python/lola ------------------------------------------------
create_file "python/lola/__init__.py"

# core
create_file "python/lola/core/__init__.py"
create_file "python/lola/core/agent.py"
create_file "python/lola/core/graph.py"
create_file "python/lola/core/state.py"
create_file "python/lola/core/memory.py"

# agents
create_file "python/lola/agents/__init__.py"
create_file "python/lola/agents/base.py"
create_file "python/lola/agents/react.py"
create_file "python/lola/agents/plan_execute.py"
create_file "python/lola/agents/conversational.py"

# tools
create_file "python/lola/tools/__init__.py"
create_file "python/lola/tools/base.py"
create_file "python/lola/tools/web_crawl.py"
create_file "python/lola/tools/onchain/__init__.py"
create_file "python/lola/tools/onchain/contract_call.py"
create_file "python/lola/tools/onchain/transact.py"
create_file "python/lola/tools/onchain/utils.py"

# chains
create_file "python/lola/chains/__init__.py"
create_file "python/lola/chains/connection.py"
create_file "python/lola/chains/contract.py"
create_file "python/lola/chains/wallet.py"
create_file "python/lola/chains/key_manager.py"
create_file "python/lola/chains/utils.py"

# agnostic
create_file "python/lola/agnostic/__init__.py"
create_file "python/lola/agnostic/unified.py"
create_file "python/lola/agnostic/fallback.py"

# libs
create_file "python/lola/libs/__init__.py"

#   langgraph
create_file "python/lola/libs/langgraph/__init__.py"
create_file "python/lola/libs/langgraph/adapter.py"

#   litellm
create_file "python/lola/libs/litellm/__init__.py"
create_file "python/lola/libs/litellm/proxy.py"

#   crawl4ai
create_file "python/lola/libs/crawl4ai/__init__.py"
create_file "python/lola/libs/crawl4ai/crawler.py"

#   web3
create_file "python/lola/libs/web3/__init__.py"
create_file "python/lola/libs/web3/connection.py"
create_file "python/lola/libs/web3/contract.py"
create_file "python/lola/libs/web3/wallet.py"
create_file "python/lola/libs/web3/utils.py"

# cli
create_file "python/lola/cli/__init__.py"
create_file "python/lola/cli/main.py"
create_file "python/lola/cli/commands/__init__.py"
create_file "python/lola/cli/commands/create.py"
create_file "python/lola/cli/commands/run.py"

# utils
create_file "python/lola/utils/__init__.py"
create_file "python/lola/utils/logging.py"
create_file "python/lola/utils/config.py"

# ---- rust placeholder -------------------------------------------
create_file "rust/.gitignore"
create_file "rust/Cargo.toml"
create_file "rust/src/lib.rs"

# --------------------------------------------------------------
echo "Skeleton creation complete! All missing folders/files are now in place."
echo "You can now safely paste the Phase 1 code I gave you into the appropriate files."