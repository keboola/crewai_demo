# Kubernetes Deployment

This document provides comprehensive information about deploying the AI Agent Platform on Kubernetes.

## Overview

Kubernetes deployment is recommended for production environments. It provides scalability, high availability, and better resource management.

## Prerequisites

- Kubernetes cluster (version 1.19 or later)
- Helm (version 3.0.0 or later)
- kubectl configured to access your cluster

## Deployment Options

The AI Agent Platform can be deployed on Kubernetes in two ways:

1. **Helm Chart**: The recommended way to deploy the platform
2. **Custom Resource Definitions (CRDs)**: For advanced use cases

## Helm Chart Deployment

### Add the Helm Repository

```bash
helm repo add ai-agent-platform https://keboola.github.io/agentic-runtime/charts
helm repo update
```

### Install the Platform

```bash
helm install ai-agent-platform ai-agent-platform/ai-agent-platform \
  --namespace ai-agent-platform \
  --create-namespace \
  --set global.openaiApiKey=your-api-key
```

### Configuration Values

The Helm chart supports the following configuration values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.openaiApiKey` | OpenAI API key | `""` |
| `global.anthropicApiKey` | Anthropic API key | `""` |
| `global.openrouterApiKey` | OpenRouter API key | `""` |
| `image.repository` | Image repository | `ghcr.io/keboola/agentic-runtime` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `replicaCount` | Number of replicas | `1` |
| `resources.requests.cpu` | CPU requests | `100m` |
| `resources.requests.memory` | Memory requests | `128Mi` |
| `resources.limits.cpu` | CPU limits | `500m` |
| `resources.limits.memory` | Memory limits | `512Mi` |
| `persistence.enabled` | Enable persistence | `true` |
| `persistence.size` | Persistence size | `1Gi` |
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress hosts | `[]` |
| `ingress.tls` | Ingress TLS configuration | `[]` |

### Custom Values File

You can create a custom values file to override the default values:

```yaml
# values.yaml
global:
  openaiApiKey: your-api-key
  anthropicApiKey: your-api-key
  openrouterApiKey: your-api-key

replicaCount: 2

resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 1Gi

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: ai-agent-platform.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ai-agent-platform-tls
      hosts:
        - ai-agent-platform.example.com
```

Then install the platform with the custom values file:

```bash
helm install ai-agent-platform ai-agent-platform/ai-agent-platform \
  --namespace ai-agent-platform \
  --create-namespace \
  -f values.yaml
```

## Custom Resource Definitions (CRDs)

The AI Agent Platform provides Custom Resource Definitions (CRDs) for managing AI Agent Runtimes in a Kubernetes cluster.

### Install the CRDs

```bash
kubectl apply -f https://raw.githubusercontent.com/keboola/agentic-runtime/main/kubernetes/crds/aiagentruntime.yaml
```

### Install the Operator

```bash
kubectl apply -f https://raw.githubusercontent.com/keboola/agentic-runtime/main/kubernetes/operator/deployment.yaml
```

### Create an AI Agent Runtime

```yaml
apiVersion: ai-agent-platform.keboola.com/v1
kind: AIAgentRuntime
metadata:
  name: my-agent
spec:
  codeSource:
    type: git
    git:
      repository: https://github.com/example/repo.git
      branch: main
      authType: none
      entrypoint: src/my_agent.py
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  env:
    - name: OPENAI_API_KEY
      valueFrom:
        secretKeyRef:
          name: openai-credentials
          key: api-key
```

Save this to a file (e.g., `my-agent.yaml`) and apply it:

```bash
kubectl apply -f my-agent.yaml
```

## Production Considerations

For production deployments, consider the following:

### High Availability

- Deploy multiple replicas for high availability
- Use pod disruption budgets to ensure minimum availability
- Configure horizontal pod autoscaling for automatic scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-agent-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-agent-platform
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
```

### Security

- Use Kubernetes secrets for sensitive information
- Configure network policies to restrict traffic
- Use pod security policies to enforce security standards
- Enable RBAC for access control

### Monitoring

- Deploy Prometheus for metrics collection
- Configure Grafana for visualization
- Set up alerts for critical conditions

### Logging

- Configure centralized logging with Elasticsearch, Fluentd, and Kibana (EFK) or Elasticsearch, Logstash, and Kibana (ELK)
- Set up log retention policies

## Troubleshooting

### Common Issues

1. **Pod fails to start**: Check the pod events and logs
2. **CRD not found**: Ensure the CRDs are installed
3. **Operator not working**: Check the operator logs
4. **Resource limits**: Ensure the resource limits are sufficient

### Viewing Logs

```bash
# View pod logs
kubectl logs -n ai-agent-platform deployment/ai-agent-platform

# View operator logs
kubectl logs -n ai-agent-platform deployment/ai-agent-platform-operator

# Follow logs in real-time
kubectl logs -n ai-agent-platform deployment/ai-agent-platform -f
```

### Debugging

```bash
# Get pod details
kubectl describe pod -n ai-agent-platform pod-name

# Get CRD details
kubectl describe aiagentruntime -n ai-agent-platform my-agent

# Get operator details
kubectl describe deployment -n ai-agent-platform ai-agent-platform-operator
```

## Related Documentation

- [Docker Deployment](docker.md): Deploying the platform using Docker
- [Local Development](local-development.md): Running the platform locally
- [Kubernetes Operator](kubernetes-operator.md): Detailed information about the Kubernetes Operator
- [Custom Resource Definitions](custom-resource-definitions.md): Detailed information about the CRDs 