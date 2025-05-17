#!/bin/bash

curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
cd ../

istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled


kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f gateway.yaml
kubectl apply -f virtual-service.yaml
kubectl apply -f destination-rule.yaml

kubectl wait --for=condition=ready pod -l app=custom-app --timeout=300s
