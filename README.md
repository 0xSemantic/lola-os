# LOLA OS: The Android OS for the On-Chain Agent Economy

[![GitHub Stars](https://img.shields.io/github/stars/lola-os/open-core?style=social)](https://github.com/lola-os/open-core/stargazers) [![GitHub Forks](https://img.shields.io/github/forks/lola-os/open-core?style=social)](https://github.com/lola-os/open-core/network/members) [![GitHub Issues](https://img.shields.io/github/issues/lola-os/open-core)](https://github.com/lola-os/open-core/issues) [![GitHub License](https://img.shields.io/github/license/lola-os/open-core)](https://github.com/lola-os/open-core/blob/main/LICENSE) [![PyPI Version](https://img.shields.io/pypi/v/lola-os)](https://pypi.org/project/lola-os/) [![Documentation](https://img.shields.io/badge/docs-Sphinx-blue)](https://lola-os.readthedocs.io/) [![Twitter Follow](https://img.shields.io/twitter/follow/lola_os?style=social)](https://twitter.com/lola_os) [![Discord](https://img.shields.io/discord/1234567890?label=Discord&logo=discord&logoColor=white)](https://discord.gg/lola-os)

**Philosophy:** Open Source for Developer Sovereignty, Proprietary for Sustainable Monetization, EVM-Native from Day One.  
**Motto:** "The Android OS for the On-Chain Agent Economy."  
**Meaning:** **L**ayered **O**rchestration for **L**ogic and **A**utomation.  
**Tagline:** **L**ive **O**nchain **L**ogical **A**gents.  

---

## 🌟 Welcome to LOLA OS!

Imagine a world where AI agents aren't just smart, they're sovereign, verifiable, and economically aligned, living directly on the blockchain. LOLA OS is the open-core operating system making this reality: the foundational platform for building, deploying, and monetizing autonomous AI agents in the EVM ecosystem. Whether you're a beginner tinkering with your first on-chain bot, a devops engineer scaling enterprise workflows, or an innovator shaping the agent economy, LOLA OS empowers you with radical simplicity and developer sovereignty.

- **For Beginners**: Jump in with our CLI scaffold an agent in seconds, query the web with Crawl4AI, or interact with EVM chains like Ethereum/Polygon without deep expertise.
- **For Builders**: Extend LangGraph for custom orchestration, route LLMs via LiteLLM, and handle full blockchain reads/writes with web3.py, all in Python for rapid prototyping.
- **For Enterprises**: Phased reliability: Start with V1 core, add monitoring (V2), security/HITL (V3), RAG (V4), evals (V5), Rust perf (V6), and proprietary scaling (TMVP2) for production.
- **For Visionaries**: Contribute to the OSS core, or upgrade to proprietary features like the $LOLA token economy, gas relaying, and fine-tuning garden to monetize your agents.

We're just getting started, Version 1 launches the core, with phased expansions based on your feedback. **Star ⭐ this repo**, fork it, and join the revolution. Your contributions could shape the next internet!

---

## 🚀 What is LOLA OS?

LOLA OS is the sovereign OS for on-chain AI agents, like Android for mobile, but for intelligent bots that read, reason, and act on blockchains. It's EVM-native from day one, fusing AI's cognitive power with blockchain's trustless execution.

### Key Highlights
- **Phased Rollout for Speed**: We release incrementally to hit the market fast and iterate on feedback. Version 1 (TMVP1) focuses on agents, CLI, and full EVM integration, build and run your first on-chain agent today!
- **Open-Core Model**: ~85% free OSS for sovereignty (full code ownership, no lock-in), ~15% proprietary for sustainability (e.g., $LOLA economy and fine-tuning in TMVP2).
- **Developer Sovereignty**: Adapters and configs let you swap components (e.g., LLMs via LiteLLM, chains via web3.py), your agents, your rules.
- **Real-World Utility**: From web research with Crawl4AI (structured extraction from dynamic sites) to secure EVM writes, LOLA agents solve practical problems like arbitrage detection or content analysis.
- **Future-Proof**: Python-first for rapid dev, Rust placeholders for perf (V6+), multi-chain expansion beyond EVM.

Join thousands of developers building the agent economy. Whether you're a solo hacker, team lead, or ecosystem builder, LOLA OS scales with you.

---

## ✨ Features

LOLA OS rolls out features in versions for focused delivery:

### Version 1 (Current Release: TMVP1 - Core Essentials)
- **Agent Orchestration**: Extended LangGraph with templates (ReAct, Plan-Execute, Conversational) for workflows, supervision (turn limits/reflection to prevent loops/context loss).
- **CLI Tools**: `lola create` scaffolds projects, `lola run` executes agents asynchronously.
- **Blockchain Integration**: Full EVM read/write via web3.py (contract calls, events, transactions with simulation/interoperability across chains like ETH/Polygon).
- **Web Research**: Crawl4AI for async crawling of JS-heavy sites, yielding structured JSON/Markdown with selectors.
- **LLM Routing**: LiteLLM for provider-agnostic calls (switch OpenAI/Ollama/Anthropic via config) with basic fallback.
- **Configuration**: .env/yaml for keys/RPCs/models, with validation.

### Upcoming Versions (Roadmap)
- **V2: Monitoring**: Local FastAPI dashboard for traces/metrics, OpenTelemetry export.
- **V3: Security/HITL**: Guardrails (safety/PII/perms/shield), TX limits/lists/confirmation, human approval/escalation.
- **V4: RAG/Data**: LangChain/LlamaIndex for retrieval, vector DB adapters (Pinecone/FAISS/Chroma/Postgres).
- **V5: Evals**: Benchmarking and graph visualization.
- **V6: Rust/Multi-Chain**: Performance ports, non-EVM support (e.g., Solana).
- **V7 (TMVP2: Proprietary)**: $LOLA token (gas/staking/gov), relayer, fine-tuning garden (Axolotl/Unsloth with flywheel/evals/observatory), agent registry/marketplace.

See [docs/roadmap.md](docs/roadmap.md) for details. Your feedback shapes priorities!

---

## 📦 Installation

LOLA OS is Python-based and easy to install. Requirements: Python 3.12+.

```bash
pip install lola-os
```

For development/contribution:
```bash
git clone https://github.com/lola-os/open-core.git
cd open-core
poetry install  # Or pip install -r requirements.txt
```

See [docs/quickstart.md](docs/quickstart.md) for platform-specific tips.

---

## 🏃 Quickstart: Build Your First Agent

1. **Scaffold a Project**:
   ```bash
   lola create my-agent --template react
   cd my-agent
   ```

2. **Set Up Config** (Edit .env from .env.sample):
   ```
   LITELLM_OPENAI_API_KEY=sk-your-key
   EVM_RPC_URL_ETHEREUM=https://mainnet.infura.io/v3/your-project-id
   EVM_PRIVATE_KEY=0x-your-private-key  # Use testnet for safety!
   ```

3. **Run the Agent**:
   ```bash
   lola run --query "What is the current ETH price on mainnet?"
   ```
   Output: Agent crawls web (via Crawl4AI), queries EVM (via web3.py), responds logically.

Customize: Edit agent.py to add tools or change models. Full tutorial in [docs/tutorials/first_agent.md](docs/tutorials/first_agent.md).

---

## 📈 Roadmap & Future Vision

We're phasing for rapid iteration:
- **V1 (Now)**: Core agents/CLI/EVM, market entry!
- **V2-V6**: Add monitoring, security, RAG, evals, Rust/multi-chain.
- **TMVP2 (V7)**: Proprietary economy/fine-tuning, post-grants.

Projections: 1M+ agents, 10M+ TX/day by Year 3 (estimated; depends on adoption). Full details in [docs/roadmap.md](docs/roadmap.md).

---

## 🤝 Contributing: Join the Community!

We ❤️ contributions! Whether fixing bugs, adding features, or improving docs, your input shapes LOLA OS.

- **Get Started**: Fork the repo, create a branch (`git checkout -b feature/awesome-thing`), commit with clear messages.
- **Guidelines**: Follow [development rules](docs/development_rules.md) (SRP, docstrings, >80% test coverage). Use example-driven dev, add 2 examples per feature.
- **PR Process**: Update docs/examples/tests, pass CI. We'll review quickly!
- **Ideas/Bugs**: Open issues, label "enhancement" or "bug".
- **Community**: Join Discord for discussions, Twitter for updates. Star ⭐ and share to help us grow!

Special thanks to early contributors, your names in changelog! Let's build the agent future together.

---

## 📜 License

OSS core: Apache 2.0, free to use/modify. Proprietary extensions (TMVP2+): Closed-source. See [LICENSE](LICENSE).

---

## 🔥 Call to Action: Be Part of the Revolution!

- **Star This Repo ⭐**: Show support and stay updated!
- **Fork & Build**: Create your agent today, share on Twitter with #LOLAOS.
- **Join Us**: Discord for chats, issues for ideas. Developers, enterprises, visionaries, LOLA OS is for you.
- **Spread the Word**: Tweet/share: "Building on-chain agents with @lola_os, EVM-native, sovereign, and ready for the agent economy! 🚀"

Questions? Open an issue. Let's make agents live on-chain!

--- 

*Built with ❤️ by the LOLA OS community. Date: October 31, 2025.*