# Scaleway with NOS
## Objective
Set up a local Kubernetes cluster on a Scaleway GPU instance with Minikube,
and dynamically manage the mig-configuration using [NOS](https://github.com/nebuly-ai/nos)

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
helm install --wait --generate-name \
     -n gpu-operator --create-namespace \
     nvidia/gpu-operator --version v22.9.0 \
     --set driver.enabled=false \
     --set migManager.enabled=false \
     --set mig.strategy=mixed \
     --set toolkit.enabled=true
```

### Install cert-manager
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.18.2/cert-manager.yaml
```
### Install NOS

```bash
helm install oci://ghcr.io/nebuly-ai/helm-charts/nos \
  --version 0.1.2 \
  --namespace nebuly-nos \
  --generate-name \
  --create-namespace \
  -f nos-values.yaml
```

### Enable dynamic mig partitioning

```bash
kubectl label nodes minikube "nos.nebuly.com/gpu-partitioning=mig"
```

### Test dynamic mig partitioning

```bash
kubectl apply -f nos-1g.yml
```

Since the algorithm is greedy, it will split the GPU in 7 1g10s.
While its running, you can run

```bash
kubectl apply -f nos-3g.yml
```

And it will split the unused slices in order to accomodate this.

You can see the logs for this in

```bash
kubectl -n nebuly-nos logs <mig-agent-name>
```

You can get mig-agent-name from running kubectl describe node and seeing the ones in the namespace.
