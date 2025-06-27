
# 🏆 Open RL Gymnasium gRPC Server

[![Docker Pulls](https://img.shields.io/docker/pulls/kotlinrl/open-rl-gymnasium-grpc-server)](https://hub.docker.com/r/kotlinrl/open-rl-gymnasium-grpc-server)
[![GitHub](https://img.shields.io/badge/source-GitHub-blue?logo=github)](https://github.com/open-rl-env/open-rl-gymnasium-grpc-server)

A production-grade **gRPC server for OpenAI Gymnasium environments**, enabling reinforcement learning (RL) agents in any language (Kotlin, Python, Java, Go, and more) to interact with Gymnasium environments over the network.

---

## 🚀 Features

- **Standard gRPC API** for creating, resetting, stepping, and rendering RL environments
- **Supports discrete and continuous action spaces**
- **Isolated environments per client/session**
- **Frame streaming endpoint** for remote visualization/debugging
- **Runs anywhere with Docker**

---

## 🐳 Quickstart with Docker

```bash
docker pull kotlinrl/open-rl-gymnasium-grpc-server:latest
docker run --rm -p 50051:50051 kotlinrl/open-rl-gymnasium-grpc-server:latest
```
The gRPC server will listen on port `50051`.

---

## 🧩 gRPC API Overview

See the [Env.proto specification](https://github.com/open-rl-env/open-rl-env-proto/blob/main/Env.proto) for message and service details.

| Method     | Description                     |
|------------|---------------------------------|
| Make       | Create an environment           |
| GetSpace   | Query action or observation space |
| Reset      | Reset environment to initial state |
| Step       | Take a step in the environment  |
| Render     | Render current environment frame |
| Close      | Close an environment session    |

- **Compatible with any gRPC client** (Python, Kotlin, Java, Go, etc.)

---

## 🧬 Example Python Client

```python
import grpc
from open_rl_env_proto import env_pb2, env_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = env_pb2_grpc.EnvStub(channel)

# Create an environment
make_resp = stub.Make(env_pb2.MakeRequest(env_id="CartPole-v1"))
handle = make_resp.env_handle

# Reset the environment
reset_resp = stub.Reset(env_pb2.ResetRequest(env_handle=handle))
obs = reset_resp.observation

# Step through the environment
step_resp = stub.Step(env_pb2.StepRequest(env_handle=handle, action=...))
```

---

## 🌍 Why Use This Server?

- **Run Gymnasium environments anywhere (local, cloud, cluster)**
- **Train agents in any language**
- **Decouple environment simulation from agent implementation**
- **Standardize RL pipelines for distributed training**

---

## 🤝 Contributing

Contributions, issues, and PRs welcome!
- For bug reports and feature requests, open an issue.
- For contributing, see [CONTRIBUTING.md](CONTRIBUTING.md) (if available).

---

## 📄 License

Apache License Version 2.0

---

> **Open RL Gymnasium gRPC Server:**  
> Powering the next generation of multi-language, multi-platform RL research and production.

---
