import urllib3
from kubernetes import client

urllib3.disable_warnings()

TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjF6M2xWT0xZOEM1YzI1bU5wem5lSGVCcmFKS2g2cTgzWE5kekZSZVM1emsifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJ0ZXN0LWFwaSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhcGktY2xpZW50LXBlcm1hbmVudC10b2tlbiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJhcGktY2xpZW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNDU5MjAzNTQtMGZiYy00NjFiLTkzMzktNWI2Njk4NTI5MjIyIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OnRlc3QtYXBpOmFwaS1jbGllbnQifQ.bpzNPhd4TfsdMtyoBnQMnc3J8qZ3aAMOxuf7VImS9EoIX3Aphugo48_lNkLEmH4PGdOtRbzTP6Z-lxd9motRMXtpQyoJm7VD04Ug1UPlR6EnDSNZ0pue0JidC_ph_Wir4Ub9ENwqudfLRHaSBWr0PTJAU8PIORy_UyKqkc3eBlzeOYImaDumQ4YC0gDbAcexwMrSj0YiVSYzFeoBgpFOQ1srjSAq041v2eyyarDP96y0FDS2F2xjyqCiHXn1gQLMbGiYKD9K7vn5XsCoy1JsBq2AetkXSlumjTUdJOTkqFJno-HJIiYiWYS0Z2D5n6k34KmoNYszFodSIIDFWPWFTg"
API_SERVER = "https://192.168.85.2:8443"

cfg = client.Configuration()
cfg.host = API_SERVER
cfg.verify_ssl = False  # mirrors curl --insecure (not for production)
cfg.api_key = {"authorization": TOKEN}
cfg.api_key_prefix = {"authorization": "Bearer"}

api_client = client.ApiClient(cfg)
v1 = client.CoreV1Api(api_client=api_client)
ret = v1.list_namespaced_pod(namespace="test-api", watch=False)
for i in ret.items:
    print(
        f"name {i.metadata.name} namespace: {i.metadata.namespace} status: {i.status.phase}"
    )
