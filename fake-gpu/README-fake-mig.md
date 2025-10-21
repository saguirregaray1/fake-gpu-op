# fake-gpu-operator

## Objective
Set up a local Kubernetes cluster and use fake-gpu-operator to simulate multiple gpu mig partitions

## Necessary tools
[Minikube installation docs](https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Frpm+package)

[Helm installation docs](https://helm.sh/docs/intro/install/)

[kubectl installation docs](https://kubernetes.io/docs/tasks/tools/#kubectl)

## Spin up a single node minikube cluster

```bash
  minikube start --driver=docker -p fake-mig-demo
```

Check that the nodes where created:

```bash
kubectl get nodes
```


## Set up fake-gpu-operator

#### Label the nodes

```bash
kubectl label node fake-mig-demo run.ai/simulated-gpu-node-pool=default --overwrite
kubectl annotate node fake-mig-demo kwok.x-k8s.io/node=fake --overwrite
```

#### Create a custom values.yaml
Node pools is a map of node pool name to node pool configuration.
This means that, nodes with the label run.ai/simulated-gpu-node-pool=pool1
will be assigned to the pool1 node pool

#### Applies our fake-gpu-operator configuration using helm

```bash
helm upgrade -i gpu-operator oci://ghcr.io/run-ai/fake-gpu-operator/fake-gpu-operator --namespace gpu-operator --create-namespace -f mig-values.yaml
kubectl -n gpu-operator rollout status deploy/status-updater 
kubectl -n gpu-operator rollout status deploy/kwok-gpu-device-plugin
```

In order to make sure it applied correctly

```bash
kubectl describe node fake-mig | grep -A10 -i "capacity\|allocatable"
```

You should see the different nvidia.com/mig-* counts described in mig-values.yaml

## Run a test workload.

```bash
kubectl apply -f mig-wl.yml
```

To check it is being run on the correct node:

```bash
kubectl get pod w1-1g -o wide
kubectl get pod w1-3g40 -o wide
```

To check it has the appropiate GPUs assigned:

```bash
kubectl describe pod w1-1g
kubectl describe pod w1-3g40
```

## Re-configure the node

```bash
helm upgrade -i gpu-operator oci://ghcr.io/run-ai/fake-gpu-operator/fake-gpu-operator --namespace gpu-operator -f mig-alt-values.yaml
kubectl -n gpu-operator delete cm -l node-topology=true
kubectl -n gpu-operator rollout restart deploy/status-updater
```


