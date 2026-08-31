# Container execution

The arena uses one content-addressed polyglot image for every lineage. A common image avoids turning host differences into apparent origin effects while still allowing an agent to replace its language or architecture.

## Image contract

The initial image contains Python, C, C++, Clang, Rust, Go, Free Pascal, Java, Make, and CMake. It contains no provider credentials, arena source, evaluator source, task solution, Docker socket, or network service.

The Dockerfile deliberately has no default base image. Supply a base pinned by digest, build once, record the resulting local image ID, and configure every lineage to use that exact ID:

```powershell
docker build --build-arg BASE_IMAGE="debian:bookworm-slim@sha256:<verified-base-digest>" --tag iah-polyglot:dev arena/docker/polyglot
docker image inspect iah-polyglot:dev --format "{{.Id}}"
python -m iah_arena docker-check --image "sha256:<local-image-id>"
```

The second command returns `sha256:<64 hex characters>`, which the arena accepts. Tags such as `latest` are rejected because they can silently refer to different bytes over time. The final image digest, toolchain report, Docker version, host characteristics, and arena commit must be recorded with every experiment.

Package-manager resolution during the build does not need to be identical after the final image has been frozen. If rebuilding the image is part of the protocol, package repositories and versions must also be pinned.

## Workshop versus judge

Both roles run with no network, a read-only container root filesystem, dropped Linux capabilities, disabled privilege escalation, a non-root UID, and explicit CPU, memory, PID, timeout, temporary-storage, and output limits.

- Workshop mounts its lineage workspace read-write so the model can compile, profile, or replace the implementation.
- Judge mounts the candidate read-only. Controlled scratch space is available at `/run/iah`; hidden fixtures should be mounted read-only at another path by the task plug-in.

Docker reduces accidental and ordinary malicious interference but is not a formal security boundary against kernel or runtime exploits. The experiment host must not expose the Docker socket or credentials to candidate containers.
