# Azure with NOS
## Objective
Set up a local Kubernetes cluster on a Scaleway GPU instance with Minikube,
and dynamically manage the mig-configuration using [NOS](https://github.com/nebuly-ai/nos)

## Steps

They gave us quota for Standard_NC24ads_A100_v4 on west us
## Create the VM.

### If you already have an image created use:
```bash
IMAGE_ID="/subscriptions/ff93c44e-caa6-4caf-856a-03e71711c699/resourceGroups/benchmark/providers/Microsoft.Compute/galleries/benchmark/images/benchmark/versions/latest"
az vm create \
  -g benchmark -n benchmark -l westus \
  --image "$IMAGE_ID" \
  --size Standard_NC24ads_A100_v4 \
  --specialized \
  --security-type TrustedLaunch \
  --admin-username azureuser \
  --ssh-key-name saguirregaray1 \
  --public-ip-sku Standard \
  --os-disk-size-gb 64
```

## If not

```bash
az vm create \
  -g benchmark -n benchmark -l westus \
  --image Canonical:ubuntu-24_04-lts:server:latest \
  --size Standard_NC24ads_A100_v4 \
  --admin-username azureuser \
  --ssh-key-name saguirregaray1 \
  --public-ip-sku Standard \
  --os-disk-size-gb 64 \
  --tags env=gpu os=ubuntu24.04
```

### Install NVIDIA drivers

```bash
sudo apt update && sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers install
```

Reboot
```bash
sudo reboot
```

Install cuda-toolkit
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo apt install -y ./cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt -y install cuda-toolkit-12-5
```

Reboot
```bash
sudo reboot
```

Check that it worked
```bash
nvidia-smi
```

### Install Docker

```bash
docker --version || true

sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
 | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

source /etc/os-release
echo \
  "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $VERSION_CODENAME stable" \
| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
                        docker-buildx-plugin docker-compose-plugin

sudo systemctl enable --now docker

sudo docker run --rm hello-world
```

Add user to docker group
```bash
sudo usermod -aG docker $USER
newgrp docker    
```

### Install nvidia-container-toolkit

```bash
# add NVIDIA’s repo
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)  # e.g., ubuntu24.04
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list \
 | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.gpg] https://#' \
 | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```


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
Check with this
```bash
nvidia-smi -i 0 -q | grep -A3 "MIG Mode"
```

If it didn't work, try rebooting
```bash
sudo reboot
```
### Generate CDI spec and enable CDI mode

```bash
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo nvidia-ctk config --in-place --set nvidia-container-runtime.mode=cdi
sudo systemctl restart docker
```

### Create the kubernetes cluster

```bash
minikube start -p custom-nos-test \
--driver=docker \
--container-runtime=docker  \
--cpus=22 \
--memory=200g  \
--gpus nvidia.com  \
--force
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
