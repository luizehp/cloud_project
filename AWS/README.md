# Luiz Eduardo Herreros Pini - Projeto Nuvem - Deploy na AWS com EKS

**[`Vídeo AWS`](https://youtu.be/QS4ealz4iTE)**

## 1. Configuração do AWS CLI (Command Line Interface)

- Link para consulta: [Amazon CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) 

## 2. Instalar o eksctl para o EKS (Amazon Elastic Kubernetes Service)
- Link para consulta: [Amazon eksctl Installation Guide](https://eksctl.io/installation/) 

## 3. Criar o cluster
-  Esse comando cria um novo cluster Kubernetes no Amazon Elastic Kubernetes Service (EKS) chamado AA-cluster na região sa-east-1 (São Paulo). Ele configura o cluster com 2 nós de tipo t3.medium
```bash
eksctl create cluster --name AA-cluster --region us-east-2 --nodes 2 --node-type t3.medium
```
- Esse comando atualiza o arquivo de configuração do kubectl (kubeconfig) para incluir o cluster EKS chamado projeto-nuvem-cluster
```bash
aws eks --region sa-east-1 update-kubeconfig --name AA-cluster
```

## 4. Fazer o deploy da api e do sql
### Deploy sql
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
        - name: mysql
          image: mysql:9.1.0
          env:
            - name: MYSQL_ROOT_PASSWORD
              value: "projeto"
            - name: MYSQL_DATABASE
              value: "projeto"
            - name: MYSQL_USER
              value: "projeto"
            - name: MYSQL_PASSWORD
              value: "projeto"
          ports:
            - containerPort: 3306
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
spec:
  type: ClusterIP
  ports:
    - port: 3306
      targetPort: 3306
  selector:
    app: mysql


```
Esse comando da o faz do sql 
```bash
kubectl apply -f sql-deployment.yaml
```
### Deploy api
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: luizehp/app:3
          env:
            - name: USER
              value: "projeto"
            - name: PASSWORD
              value: "projeto"
            - name: SERVER
              value: "mysql-service"
            - name: PORT
              value: "3306"
            - name: NAME
              value: "projeto"
            - name: SECRET_KEY
              value: "CAVALO"
            - name: ALGORITHM
              value: "HS256"
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  type: LoadBalancer
  ports:
    - port: 8000
      targetPort: 8000
  selector:
    app: api
```
Esse comando da o faz da api 
```bash
kubectl apply -f api-deployment.yaml
```

## 5. Acesso ao serviço e pods
```bash
kubectl get svc
kubectl get pods
```

