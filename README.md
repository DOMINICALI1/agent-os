<img width="480" height="258" alt="gif" src="https://github.com/user-attachments/assets/7909270c-d060-4e34-a3f3-6f8becbf34ba" />

support on https://www.producthunt.com/products/agent-os-3

AgentOS Network (agentos-net)
Open-Source Infrastructure for Secure, Low-Latency Agent-to-Agent Interoperability & Financial Settlement.

agentos-net is a lightweight, framework-agnostic protocol built on gRPC and Ed25519 Cryptographic DIDs (Decentralized Identifiers). It empowers autonomous AI agents created across different frameworks (CrewAI, LangChain, Ollama, AutoGen) to discover, negotiate, execute tasks, and settle payments with zero vendor lock-in.

Key Features
Framework-Agnostic Communication: Connect local or distributed agents regardless of their underlying stack.

High-Performance gRPC Transport: Binary serialization ensuring sub-millisecond execution handshakes.

Cryptographic Identities (DIDs): Ed25519 keypairs for verifiable payload signatures and tamper-proof authentication.

Autonomous Payment Layer: Integrated negotiation specification supporting Crypto Escrow (Solana/EVM) and Fiat (Stripe) settlement modes.

Local-First & Privacy-Preserving: Operates seamlessly on local networks without mandatory external server dependencies.

Quick Start
1. Installation
Clone the repository and install the dependencies:

Bash
git clone https://github.com/DOMINICALI1/agent-os.git
cd agent-os
pip install -r requirements.txt
2. Running Local Examples
We provide end-to-end integration examples in the examples/ directory:

CrewAI Orchestration:

Bash
python examples/crewai_integration.py
Local Ollama Inference Node:

Bash
python examples/ollama_local_agent.py
Autonomous Payment Negotiation:

Bash
python examples/payment_negotiation.py
Architecture Overview
Plaintext
+-----------------------+               +-----------------------+
|   CrewAI / LangChain  |               |  Local Ollama Agent   |
| (Client / Task Owner) |               |  (Provider / Worker)  |
+-----------+-----------+               +-----------+-----------+
            |                                       |
            +------------[ gRPC + Ed25519 ]---------+
                        |
            [ Settlement / Escrow Engine ]
                        |
            (Solana / Base / Stripe Fiat)
Handshake: Agents exchange public keys (did:agentos:...) and verify identity signatures.

Negotiation: Task requirements and settlement terms (price, SLA, network) are agreed upon.

Execution & Release: Provider executes the inference/task, verifies execution with DID proof, and triggers payment release.

Roadmap
[x] Core SDK & gRPC Protocol Specification

[x] Ed25519 Cryptographic Verification

[x] CrewAI & Local Ollama Integration Specifications

[x] Payment Settlement Protocol Schema

[ ] Hosted Agent Registry (Global Agent DNS)

[ ] Production Escrow Smart Contracts (Solana / Base)

License
Distributed under the MIT License. See LICENSE for more information.