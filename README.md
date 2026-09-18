# Agent OS SDK

A decentralized, high-performance protocol designed for autonomous AI agent identification, dynamic multi-round negotiation, and encrypted data streaming.

## Features

- **Cryptographic Identity**: Ed25519-based Decentralized Identifiers (DIDs) for verifiable agent identity and signatures.
- **Dynamic Negotiation Protocol**: Multi-round counter-offer bargaining model for automated price discovery.
- **High-Performance Streaming**: Bidirectional gRPC streaming powered by HTTP/2 for low-latency payload delivery.
- **Open-Core & Framework Agnostic**: Designed to integrate seamlessly with any LLM framework or local AI runtime (e.g., Ollama, PyTorch, LangChain).

## Installation

Install the package in editable mode locally:

```bash
pip install -e .

```

Or build the wheel package for distribution:

```bash
python setup.py sdist bdist_wheel

```

## Quick Start

### 1. Provider Node

```python
from agentos import AgentNode

provider = AgentNode(name="GPU_Provider")
provider.start(port=50052)

```

### 2. Consumer Node

```python
from agentos import AgentNode

consumer = AgentNode(name="Task_Consumer")
session = consumer.connect("localhost:50052")

# Initiates negotiation and automated streaming
session.negotiate(target_price=10.0)

```

## Protocol Architecture

```
[Consumer Node] <--- Handshake (DID Authentication) ---> [Provider Node]
[Consumer Node] <--- Multi-Round Dynamic Bargaining ---> [Provider Node]
[Consumer Node] <=== Bidirectional Data Streaming  ===> [Provider Node]

```

## License

This project is open-source software licensed under the [MIT License](https://www.google.com/search?q=LICENSE).
