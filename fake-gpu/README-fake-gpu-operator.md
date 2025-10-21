# fake-gpu-operator

## Objective
Set up a local Kubernetes cluster and use fake-gpu-operator to simulate multiple gpus.

## Necessary tools
[Minikube installation docs](https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Frpm+package)

[Helm installation docs](https://helm.sh/docs/intro/install/)

[kubectl installation docs](https://kubernetes.io/docs/tasks/tools/#kubectl)

## Spin up a minikube cluster

```bash
  minikube start \
    --driver=docker \
    --nodes=3 \
    --cpus=2 \
    --memory=2g \
    -p fake-gpu-demo
```

Check that the nodes where created:

```bash
kubectl get nodes
```

Open a browser dashboard
```bash
minikube dashboard -p multinode-demo
```

## Set up fake-gpu-operator

#### Label the nodes

```bash
kubectl label node fake-gpu-demo run.ai/simulated-gpu-node-pool=pool1
kubectl label node fake-gpu-demo-m02 run.ai/simulated-gpu-node-pool=pool2
kubectl label node fake-gpu-demo-m03 run.ai/simulated-gpu-node-pool=pool3
```

#### Create a custom values.yaml
Node pools is a map of node pool name to node pool configuration.
This means that, nodes with the label run.ai/simulated-gpu-node-pool=pool1
will be assigned to the pool1 node pool

#### Applies our fake-gpu-operator configuration using helm

```bash
helm upgrade -i gpu-operator oci://ghcr.io/run-ai/fake-gpu-operator/fake-gpu-operator --namespace gpu-operator --create-namespace -f values.yaml
```

In order to make sure it applied correctly

```bash
kubectl describe node <node-name> | grep -A10 -i "capacity\|allocatable"
```

You should see nvidia.com/gpu: followed by the correct number

## Run workloads on the cluster

Let's first run w1, here we are using node selector to tell in which node to run the task.

```bash
kubectl apply -f w1.yml
```

To check it's being run on the correct node:

```bash
kubectl get pod w1 -o wide
```

To check it has an assigned GPU:

```bash
kubectl describe pod w1
```

After that, try running w2, which requires 4 GPUs and thus will be assigned to node 2

```bash
kubectl apply -f w2.yml
```

Use the same checks as before

For w3, we ask for three gpus and use nodeSelector to choose node 3, which only has one.

```bash
kubectl apply -f w3.yml
```

You can see the error clearly running

```bash
kubectl describe pod w3
```

## Making sure that fake-gpu-operator is simulating properly

Run gpu-test workload in order to make sure that the nodes do have nvidia-smi access.

```bash
kubectl apply -f gpu-test.yml
```

