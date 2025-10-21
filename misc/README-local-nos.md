## Steps

```bash
```

```bash
cd ~/Projects/walkai/nos
```

```bash
kubectl label node custom-nos-test nos.nebuly.com/gpu-partitioning=mig --overwrite
```
```bash
kubectl apply -k config/migagent/default
kubectl apply -k config/gpuagent/default
kubectl apply -k config/gpupartitioner/default
```

```bash
kubectl get pods -n nos-system -w
```
