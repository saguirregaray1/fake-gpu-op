# Objective

Partition a H100 from Scaleway using MIG, and deploy concurrent workflows that require this slices.

Specifically, we plan to partition it into 7 slices of 1g.10gb, and deploy three workflows that require 3 partitions, 3 partitions and 1 partition each.
# Setup

Rent a H100 in Scaleway.
Create an ssh key and add it to the Scaleway Instance.
Launch the instance and ssh into it.

# MIG Partitioning

### Checking MIG Status

```bash
nvidia-smi -i 0
```

You should see Disabled, in the middle right square.

```
Sun Aug 17 22:09:14 2025
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.169                Driver Version: 570.169        CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA H100 PCIe               Off |   00000000:01:00.0 Off |                    0 |
| N/A   41C    P0             54W /  350W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

### Enabling MIG

```bash
sudo nvidia-smi -i 0 -mig 1
```

```
Enabled MIG Mode for GPU 00000000:01:00.0

Warning: persistence mode is disabled on device 00000000:01:00.0. See the Known Issues section of the nvidia-smi(1) man page for more information. Run with [--help | -h] switch to get more information on how to enable persistence mode.
All done.
```

#### Checking that it's actually enabled

```bash
nvidia-smi -i 0 --query-gpu=pci.bus_id,mig.mode.current --format=csv
```

```
pci.bus_id, mig.mode.current
00000000:01:00.0, Enabled
```

### Check possible configurations

```bash
nvidia-smi mig -lgip
```

```
+-------------------------------------------------------------------------------+
| GPU instance profiles:                                                        |
| GPU   Name               ID    Instances   Memory     P2P    SM    DEC   ENC  |
|                                Free/Total   GiB              CE    JPEG  OFA  |
|===============================================================================|
|   0  MIG 1g.10gb         19     7/7        9.75       No     14     1     0   |
|                                                               1     1     0   |
+-------------------------------------------------------------------------------+
|   0  MIG 1g.10gb+me      20     1/1        9.75       No     14     1     0   |
|                                                               1     1     1   |
+-------------------------------------------------------------------------------+
|   0  MIG 1g.20gb         15     4/4        19.62      No     14     1     0   |
|                                                               1     1     0   |
+-------------------------------------------------------------------------------+
|   0  MIG 2g.20gb         14     3/3        19.62      No     30     2     0   |
|                                                               2     2     0   |
+-------------------------------------------------------------------------------+
|   0  MIG 3g.40gb          9     2/2        39.50      No     46     3     0   |
|                                                               3     3     0   |
+-------------------------------------------------------------------------------+
|   0  MIG 4g.40gb          5     1/1        39.50      No     62     4     0   |
|                                                               4     4     0   |
+-------------------------------------------------------------------------------+
|   0  MIG 7g.80gb          0     1/1        79.25      No     114    7     0   |
|                                                               8     7     1   |
+-------------------------------------------------------------------------------+
```

### Partition with 7 slices of 1g.10gb (id=19)

```bash
sudo nvidia-smi mig -cgi 19,19,19,19,19,19,19 -C
```

```
Successfully created GPU instance ID  9 on GPU  0 using profile MIG 1g.10gb (ID 19)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID  9 using profile MIG 1g.10gb (ID  0)
Successfully created GPU instance ID  7 on GPU  0 using profile MIG 1g.10gb (ID 19)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID  7 using profile MIG 1g.10gb (ID  0)
Successfully created GPU instance ID  8 on GPU  0 using profile MIG 1g.10gb (ID 19)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID  8 using profile MIG 1g.10gb (ID  0)
Successfully created GPU instance ID 11 on GPU  0 using profile MIG 1g.10gb (ID 19)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID 11 using profile MIG 1g.10gb (ID  0)
Successfully created GPU instance ID 12 on GPU  0 using profile MIG 1g.10gb (ID 19)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID 12 using profile MIG 1g.10gb (ID  0)
Successfully created GPU instance ID 13 on GPU  0 using profile MIG 1g.10gb (ID 19)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID 13 using profile MIG 1g.10gb (ID  0)
Successfully created GPU instance ID 14 on GPU  0 using profile MIG 1g.10gb (ID 19)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID 14 using profile MIG 1g.10gb (ID  0)
```
#### Check that the partitioning was successful

```bash
nvidia-smi -l
```

```
Sun Aug 17 22:12:44 2025
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.169                Driver Version: 570.169        CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA H100 PCIe               Off |   00000000:01:00.0 Off |                   On |
| N/A   40C    P0             54W /  350W |     102MiB /  81559MiB |     N/A      Default |
|                                         |                        |              Enabled |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| MIG devices:                                                                            |
+------------------+----------------------------------+-----------+-----------------------+
| GPU  GI  CI  MIG |                     Memory-Usage |        Vol|        Shared         |
|      ID  ID  Dev |                       BAR1-Usage | SM     Unc| CE ENC  DEC  OFA  JPG |
|                  |                                  |        ECC|                       |
|==================+==================================+===========+=======================|
|  0    7   0   0  |              15MiB /  9984MiB    | 14      0 |  1   0    1    0    1 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+
|  0    8   0   1  |              15MiB /  9984MiB    | 14      0 |  1   0    1    0    1 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+
|  0    9   0   2  |              15MiB /  9984MiB    | 14      0 |  1   0    1    0    1 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+
|  0   11   0   3  |              15MiB /  9984MiB    | 14      0 |  1   0    1    0    1 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+
|  0   12   0   4  |              15MiB /  9984MiB    | 14      0 |  1   0    1    0    1 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+
|  0   13   0   5  |              15MiB /  9984MiB    | 14      0 |  1   0    1    0    1 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+
|  0   14   0   6  |              15MiB /  9984MiB    | 14      0 |  1   0    1    0    1 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

Make sure to ctrl+c after the date appears again.
