#!/bin/bash

set -e

NAMESPACE="grading-pdf"
IMAGE_TAG=${1:-master}

echo "🚀 Deploying grading-pdf to K3s..."
echo "Image tag: $IMAGE_TAG"

# Update image tags in deployments
echo "🔄 Updating image tags..."
sed -i "s|chunchiehdev/grading-pdf:latest|chunchiehdev/grading-pdf:$IMAGE_TAG|g" deployment.yaml

# Apply ConfigMap
echo "⚙️  Applying ConfigMap..."
kubectl apply -f configmap.yaml

# Deploy Redis first
echo "🗄️  Deploying Redis..."
kubectl apply -f redis.yaml

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s

# Apply Services
echo "🔗 Applying Services..."
kubectl apply -f service.yaml

# Deploy Applications (includes namespace)
echo "🚀 Deploying Applications..."
kubectl apply -f deployment.yaml

# Apply Ingress
echo "🌐 Applying Ingress..."
kubectl apply -f ingress.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl rollout status deployment grading-pdf-api -n $NAMESPACE
kubectl rollout status deployment grading-pdf-worker -n $NAMESPACE

echo "✅ Deployment completed!"
echo ""
echo "📊 Deployment status:"
kubectl get pods -n $NAMESPACE
echo ""
echo "🌐 Services:"
kubectl get svc -n $NAMESPACE
echo ""
echo "🔗 Ingress:"
kubectl get ingress -n $NAMESPACE 