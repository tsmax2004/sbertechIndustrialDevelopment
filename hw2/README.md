### Запуск:

1. Подготовить окружение:
```bash
docker-compose up
```

2. Зайти в контейнер `control-node`

3. Запустить плейбук:

```bash
ansible-playbook playbook.yml
```

### Проверка:

1. Зайти на любой хост (`host1`, `host2`)

2. Приложение доступно на 8080 и 80 (проксирует Nginx) портах:

```bash
apk add curl
curl localhost:80
curl localhost:8080
```
