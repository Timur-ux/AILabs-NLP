# AILab 2 NLP

Студент: Бучкин Тимур Артемович
Группа: М8О-401Б-22 (на момент последнего коммита)

# Реализовано

Развертывание сервиса из двух контейнеров (ollama с qwen2.5:0.5b и fastapi backend).

На backend есть 2 точки доступа:

- /AskOllama: POST запрос к модели qwen.

Тело запроса:
```json
{
	"message": string
}
```

Тело ответа:

```json
string
```

- /docs: FastApi swagger документация

# Развертывание

Будучи в корне репозитория введите в терминал:

```bash
docker compose up -d
```

# Датасет

Т.к. я работаю с заданием определения спама, я выбрал kaggle датасет [spam-or-not-spam](https://www.kaggle.com/datasets/ozlerhakan/spam-or-not-spam-dataset), в котором 2500 обычных сообщений и 500 сообщений спама

# TODO

- [ ] Проанализировать различные техники промтинга
