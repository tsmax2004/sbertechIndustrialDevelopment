## To run:

1. Подготовить minikube и собрать образ приложения

```
minikube start
eval $(minikube docker-env)
docker build -t custom-app:v2 .
```

2. Применить манифесты

```
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/daemonset.yaml
```

3. Проверить запущенные компоненты

```
kubectl get deployments
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
custom-app   3/3     3            3           7m32s


kubectl get pods
NAME                         READY   STATUS    RESTARTS   AGE
custom-app-798bc77d5-2m5bc   1/1     Running   0          8m
custom-app-798bc77d5-nh2b8   1/1     Running   0          8m
custom-app-798bc77d5-pzhc8   1/1     Running   0          8m
log-agent-qt6k7              1/1     Running   0          8m


kubectl get daemonsets
NAME        DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
log-agent   1         1         1       1            1           <none>          8m38s
```

4. Проверить API приложения

```
kubectl port-forward service/custom-service 8080:80

curl http://localhost:8080/
Hello! (Pod: custom-app-798bc77d5-2m5bc)

curl http://localhost:8080/status
{"pod":"custom-app-798bc77d5-2m5bc","status":"ok"}

curl -X POST -H "Content-Type: application/json" -d '{"message":"some log"}' http://localhost:8080/log
{"pod":"custom-app-798bc77d5-2m5bc","status":"ok"}

curl http://localhost:8080/logs
2025-04-06 10:48:24,822 INFO: [Pod: custom-app-798bc77d5-2m5bc] some log [in /app/app.py:37]
```

5. Проверить, что агент собрал лог

```
kubectl logs -l app=log-agent --tail 100
=== Starting log collection ===
2025-04-06 10:48:24,822 INFO: [Pod: custom-app-798bc77d5-2m5bc] some log [in /app/app.py:37]

kubectl exec -it log-agent-qt6k7 -- cat /var/log/node-logs/app.log
2025-04-06 10:48:24,822 INFO: [Pod: custom-app-798bc77d5-2m5bc] some log [in /app/app.py:37]
```

6. Проверим балансировку запросов. Для этого используем временный под внутри кластера (тк туннель устанавливает TCP соединения с одним подом)

```
kubectl apply -f k8s/test-pod.yaml

kubectl exec -it test-pod -- sh -c 'for i in $(seq 1 5); do curl -s http://custom-service/status; echo; sleep 0.1; done'
{"pod":"custom-app-798bc77d5-pzhc8","status":"ok"}
{"pod":"custom-app-798bc77d5-2m5bc","status":"ok"}
{"pod":"custom-app-798bc77d5-2m5bc","status":"ok"}
{"pod":"custom-app-798bc77d5-pzhc8","status":"ok"}
{"pod":"custom-app-798bc77d5-nh2b8","status":"ok"}

kubectl exec -it test-pod -- sh -c 'for i in $(seq 1 10); do curl -X POST -H "Content-Type: application/json" -d "{\"message\":\"log $i\"}" http://custom-service/log; sleep 0.1; done'

kubectl logs -l app=log-agent --tail 100
=== Starting log collection ===
2025-04-06 10:48:24,822 INFO: [Pod: custom-app-798bc77d5-2m5bc] some log [in /app/app.py:37]
2025-04-06 11:05:25,017 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 1 [in /app/app.py:37]
2025-04-06 11:05:25,124 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 2 [in /app/app.py:37]
2025-04-06 11:05:25,261 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 3 [in /app/app.py:37]
2025-04-06 11:05:25,366 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 4 [in /app/app.py:37]
2025-04-06 11:05:25,471 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 5 [in /app/app.py:37]
2025-04-06 11:05:25,582 INFO: [Pod: custom-app-798bc77d5-pzhc8] log 6 [in /app/app.py:37]
2025-04-06 11:05:25,687 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 7 [in /app/app.py:37]
2025-04-06 11:05:25,792 INFO: [Pod: custom-app-798bc77d5-pzhc8] log 8 [in /app/app.py:37]
2025-04-06 11:05:25,906 INFO: [Pod: custom-app-798bc77d5-pzhc8] log 9 [in /app/app.py:37]
2025-04-06 11:05:26,016 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 10 [in /app/app.py:37]
```

7. Попробовать удалить поды

```
kubectl delete pod -l app=custom-app --force
pod "custom-app-798bc77d5-2m5bc" force deleted
pod "custom-app-798bc77d5-nh2b8" force deleted
pod "custom-app-798bc77d5-pzhc8" force deleted

kubectl logs -l app=log-agent --tail 100
=== Starting log collection ===
2025-04-06 10:48:24,822 INFO: [Pod: custom-app-798bc77d5-2m5bc] some log [in /app/app.py:37]
2025-04-06 11:05:25,017 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 1 [in /app/app.py:37]
2025-04-06 11:05:25,124 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 2 [in /app/app.py:37]
2025-04-06 11:05:25,261 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 3 [in /app/app.py:37]
2025-04-06 11:05:25,366 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 4 [in /app/app.py:37]
2025-04-06 11:05:25,471 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 5 [in /app/app.py:37]
2025-04-06 11:05:25,582 INFO: [Pod: custom-app-798bc77d5-pzhc8] log 6 [in /app/app.py:37]
2025-04-06 11:05:25,687 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 7 [in /app/app.py:37]
2025-04-06 11:05:25,792 INFO: [Pod: custom-app-798bc77d5-pzhc8] log 8 [in /app/app.py:37]
2025-04-06 11:05:25,906 INFO: [Pod: custom-app-798bc77d5-pzhc8] log 9 [in /app/app.py:37]
2025-04-06 11:05:26,016 INFO: [Pod: custom-app-798bc77d5-2m5bc] log 10 [in /app/app.py:37]
2025-04-06 11:12:33,052 INFO: [Pod: custom-app-798bc77d5-5rnrj] log 11 [in /app/app.py:37]
2025-04-06 11:12:33,164 INFO: [Pod: custom-app-798bc77d5-5rnrj] log 12 [in /app/app.py:37]
2025-04-06 11:12:33,273 INFO: [Pod: custom-app-798bc77d5-ns78l] log 13 [in /app/app.py:37]
2025-04-06 11:12:33,397 INFO: [Pod: custom-app-798bc77d5-h5kmx] log 14 [in /app/app.py:37]
2025-04-06 11:12:33,507 INFO: [Pod: custom-app-798bc77d5-5rnrj] log 15 [in /app/app.py:37]
2025-04-06 11:12:33,628 INFO: [Pod: custom-app-798bc77d5-h5kmx] log 16 [in /app/app.py:37]
2025-04-06 11:12:33,748 INFO: [Pod: custom-app-798bc77d5-ns78l] log 17 [in /app/app.py:37]
2025-04-06 11:12:33,861 INFO: [Pod: custom-app-798bc77d5-5rnrj] log 18 [in /app/app.py:37]
2025-04-06 11:12:33,966 INFO: [Pod: custom-app-798bc77d5-5rnrj] log 19 [in /app/app.py:37]
2025-04-06 11:12:34,073 INFO: [Pod: custom-app-798bc77d5-ns78l] log 20 [in /app/app.py:37]
```
