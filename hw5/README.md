## HW 5

1. Запустить `minicube`:
```
minicube start
```

2. Поднять под с `postgresql` и с приложением:
```
kubectl create -f kube/postgres.yaml
kubectl create -f kube/deployment.yaml
```

3. Настраиваем сетевой доступ:
```
kubectl expose deployment simple-app --type=LoadBalancer --port=8080
```

4. Пробрасываем порты:
```
minikube service simple-app --url
```

5. Сходим в приложение:
```
curl http://127.0.0.1:56429/inc
curl http://127.0.0.1:56429/get 
```