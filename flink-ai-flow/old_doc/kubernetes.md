# How to run ai flow on kubernetes

## 1. Build docker images

### Init container image
Initializing docker image is responsible for downloading user code to the docker container.
```bash
cd resources/init_docker
sh build_init_image.sh
```
Then push the docker image to docker repository.

### AI Flow run environment image
The dependent environment of AI flow including Python 3.7, numpy, etc.
```bash
cd resources/base_docker
sh build_env_image.sh
```
### AI Flow image

The AI flow running environment can run AI flow master and AI flow worker. 
Currently, the running engine is supported by cmd_line, python and flink.

```bash
cd resources/docker_image
sh build_image.sh
```
Then push the docker image to docker repository.


## 2. Create AI Flow master configuration

Create kubernetes authorization configuration.


ai-flow-cluster-rbac.yaml
```yaml
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: ai-flow-master
subjects:
- kind: ServiceAccount
  name: default
  namespace: ai-flow
roleRef:
  kind: ClusterRole
  name: ai-flow-master
  apiGroup: rbac.authorization.k8s.io
```

Create ai-flow-master role configuration.


ai-flow-cluster-role.yaml
```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: ai-flow
  name: ai-flow-master
rules:
  - apiGroups: [""]
    resources: ["services", "pods", "configmaps"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: ["extensions", "apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: ["batch", "extensions"]
    resources: ["jobs"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

Create ai-flow-master job configuration.


ai-flow-master.yaml
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ai-flow-master
spec:
  template:
    metadata:
      labels:
        app: ai-flow
        component: ai-flow-master
    spec:
      restartPolicy: Never
      containers:
        - name: ai-flow-master-container
          image: '${ai flow image}'
          command: ["python3", "/opt/server_runner.py", "--config", "/opt/conf/master.yaml"]
          imagePullPolicy: Always
          ports:
            - containerPort: 50051
              name: master
          env:
            - name: PYTHONUNBUFFERED
              value: '1'
            - name: PYTHONIOENCODING
              value: 'UTF-8'
          volumeMounts:
            - name: ai-flow-master-config
              mountPath: /opt/conf
      volumes:
        - name: ai-flow-master-config
          configMap:
            name: ai-flow-master-config
            items:
              - key: master.yaml
                path: master.yaml
```
Create ai-flow-master ConfigMap configuration.


ai-flow-master-configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-flow-master-config
  labels:
    app: ai-flow
data:
  master.yaml: |+
    server_ip: localhost
    server_port: ${export port}
    db_uri:  ${date base uri}
    db_type: ${data base type}
    k8s_namespace: ai-flow
    ai_flow_base_init_image: ${init daocker image}
    ai_flow_worker_image: ${ai flow docker image}
    flink_ai_flow_base_image: ${ai flow docker image}
```

Create ai-flow-master service configuration.


ai-flow-master-service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-flow-master-svc
  labels:
    app: ai-flow
    component: ai-flow-master
spec:
  ports:
  - name: master
    port: ${port}
  type: LoadBalancer
  selector:
    app: ai-flow
    component: ai-flow-master
```


## 3. Start AI Flow master 

Create kubernetes namespace.
```bash
kubectl create ns ai-flow
```

Set ai-flow-master kubernetes role.
```bash
kubectl apply -f ai-flow-cluster-role.yaml -n ai-flow
```

Set ai-flow-master kubernetes authorization.
```bash
kubectl apply -f ai-flow-cluster-rbac.yaml -n ai-flow
```
Create ai-flow-master configuration.

```bash
kubectl apply -f ai-flow-master-configmap.yaml -n ai-flow
```

Start ai-flow-master service.
```bash
kubectl apply -f ai-flow-master-service.yaml -n ai-flow
```

Start ai-flow-master job.
```bash
kubectl apply -f ai-flow-master.yaml -n ai-flow
```

Get ai-flow-master service ip and port.
```bash
kubectl get svc -n ai-flow
```

You can get the output:
```bash
NAME                 TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)           AGE
ai-flow-master-svc   LoadBalancer   172.21.7.11   39.102.53.198   50051:30435/TCP   29d
```
ai-flow-master ip: 39.102.53.198
ai-flow-master port: 50051


## 4. Set project configuration

```yaml
project_name: ${project name}
server_ip: ${master ip}
server_port: ${master port}
ai_flow_home: /opt/ai_flow
blob_server.type: oss
blob_server.endpoint: ${oss endpoint}
blob_server.bucket: ${oss bucket}
blob_server.access_key_id: ${oss access key}
blob_server.access_key_secret: ${oss access secret}
```


At last you can submit the ai flow project to kubernetes platform.

