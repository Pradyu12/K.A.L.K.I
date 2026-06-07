# SUDARSHANA OS — Mainframe

Cinematic FUI HUD and Intelligent AI Backend.

## Quick Start

1. Install: `pip install -r requirements.txt`
2. Run Backend: `uvicorn main:app --host 0.0.0.0 --port 8000`
3. View HUD: `http://localhost:8000`
4. Run CLI: `python3 sudarshana_cli.py` (requires `GOOGLE_API_KEY` for full cognitive functions)

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured

### Deploy
```bash
# Build Docker image
docker build -t sudarshana:latest .

# Update the secret with your Google API key
kubectl create namespace sudarshana-system
kubectl apply -k .

# Or deploy individual files
kubectl apply -f k8s-secret.yaml
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
kubectl apply -f k8s-ingress.yaml
```

### Verify
```bash
kubectl get pods -n sudarshana-system
kubectl get services -n sudarshana-system
kubectl port-forward svc/sudarshana-service 8080:80 -n sudarshana-system
```

## Production

The Dockerfile uses gunicorn with uvicorn workers for production-ready deployment.