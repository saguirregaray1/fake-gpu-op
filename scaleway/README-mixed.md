# Scaleway Mixed
## Objective
Set up a local Kubernetes cluster on a Scaleway GPU instance with Minikube,
and configure it to have a mixed configuration using GPU Operator

## Steps

### Install minikube

```bash
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

### Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```
And check with 

```bash
kubectl version --client
```

### Install helm

```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

### Enable MIG
```bash
sudo nvidia-smi -i 0 -mig 1
```

### Generate CDI spec and enable CDI mode

```bash
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo nvidia-ctk config --in-place --set nvidia-container-runtime.mode=cdi
sudo systemctl restart docker
```

### Create the kubernetes cluster

```bash
minikube start --driver=docker --container-runtime=docker --gpus nvidia.com --force
```

### Disable the default addon

```bash
minikube addons disable nvidia-device-plugin
kubectl -n kube-system delete ds nvidia-device-plugin-daemonset --ignore-not-found
```

### Install GPU Operator using helm

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia && helm repo update
helm upgrade --install gpu-operator nvidia/gpu-operator \
  -n gpu-operator --create-namespace \
  --set driver.enabled=false \
  --set toolkit.enabled=true
```

### Set MIG strategy to mixed

```bash
kubectl patch clusterpolicies.nvidia.com/cluster-policy --type='json' \
  -p='[{"op":"replace","path":"/spec/mig/strategy","value":"mixed"}]'
```

### Tell the operator to use this ConfigMap

```bash
kubectl patch clusterpolicies.nvidia.com/cluster-policy --type='json' \
  -p='[{"op":"replace","path":"/spec/migManager/config/name","value":"custom-mig-config"}]'
```

### Apply the configuration
```bash
kubectl label node minikube nvidia.com/mig.config=mix-3g40-4x1g10 --overwrite
```

Wait until it finishes (should see `SUCCESS`)
```bash
kubectl get node minikube -L nvidia.com/mig.config -L nvidia.com/mig.config.state -w
```

Verify it worked
```bash
kubectl describe node
```

### Run a test job
```bash
kubectl apply -f jobs-mixed.yml
```

```bash
kubectl logs -f job/job-big-3g40
kubectl logs -f job/job-small-1g10-a
kubectl logs -f job/job-small-1g10-b
kubectl logs -f job/job-small-1g10-c
```
You should see under MIG Devices the appropiate amount of memory for each job.

### Applying another configuration
```bash
kubectl label node minikube nvidia.com/mig.config=mix-2x2g20-3x1g10 --overwrite
kubectl get node minikube -L nvidia.com/mig.config -L nvidia.com/mig.config.state -w
```

```bash
kubectl describe node
```