# 02 — Kubernetes Deployment

Deploys the sentiment-api container (from [`01-sentiment-api`](../01-sentiment-api))
to a local Kubernetes cluster, reachable from the browser. The focus of this
project is the **deployment layer**: how a container becomes a running,
self-healing, externally-reachable service on Kubernetes.

## What this demonstrates

- Deploying a containerized service to Kubernetes with a **Deployment**
- Exposing it internally with a **Service** and externally with an **Ingress**
- Health management via **liveness** and **readiness** probes
- Running a real (lightweight) cluster locally with **k3d**, no cloud cost

## The stack

| Piece | Role |
|-------|------|
| **k3d** | Runs a real, lightweight Kubernetes cluster inside Docker |
| **kubectl** | CLI to talk to the cluster |
| **Deployment** | Runs and maintains the app's Pod(s); handles rollouts |
| **Service** | Stable internal address that routes to the Pods |
| **Ingress** | Routes external browser traffic to the Service (via k3d's built-in Traefik) |

## How it fits together

External request → **Ingress** → **Service** (port 80) → **Pod** (port 8000)

Behind the scenes the ownership chain is:

**Deployment → ReplicaSet → Pod**

- The **Deployment** manages versions and rollouts.
- The **ReplicaSet** keeps the desired number of Pods alive (self-healing).
- The **Pod** runs the actual container.

The **Service** finds Pods by their `app: sentiment-api` label, so it keeps
routing correctly even when Pods are recreated (and get new IPs).

## Prerequisites

- Docker running (`sudo service docker start`)
- The sentiment-api image built locally:
```bash
  cd ../01-sentiment-api
  docker build -t sentiment-api:0.1.0 .
```

## Deploy it

```bash
# 1. Create a local cluster (maps localhost:8080 -> cluster ingress)
k3d cluster create playground --port "8080:80@loadbalancer"

# 2. Import the local image into the cluster (k3d can't see local Docker images by default)
k3d image import sentiment-api:0.1.0 -c playground

# 3. Apply the manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# 4. Check everything is running
kubectl get deployment,rs,pods,svc,ingress
```

## Use it

Once the Pod is `Running` (`kubectl get pods` shows `1/1`):

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "this is wonderful"}'
  -w "\n"
```

Or open the interactive API docs: http://localhost:8080/docs

## Useful commands

```bash
kubectl get pods                          # list Pods
kubectl describe pod -l app=sentiment-api # detailed status + events (best for debugging)
kubectl logs -l app=sentiment-api         # the app's logs
kubectl get endpoints sentiment-api       # confirms the Service found the Pods
kubectl delete pod -l app=sentiment-api   # kill a Pod and watch the ReplicaSet recreate it
```

## Cluster lifecycle

```bash
k3d cluster stop playground     # pause (frees memory, keeps everything)
k3d cluster start playground    # resume
k3d cluster delete playground   # remove entirely
```

## Notes & limitations

- `imagePullPolicy: IfNotPresent` + `k3d image import` is a local-dev shortcut.
  In production, images come from a registry (e.g. built and pushed by CI).
- Single replica, no resource limits or autoscaling — kept minimal on purpose;
  the goal is understanding the core objects, not a production-grade setup.