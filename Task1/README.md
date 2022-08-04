# Task 1. Python

## Usage
### General scheme

```bash
python script.py [--students_location] [--rooms_location] [--save_format]  [--help]
```
### Parameters
-  `--students_location` location of  students.json file (default=data_files)
-  `--rooms_location` location of rooms.json file (default=data_files)
-  `--save_format` format for saving the result (xml/json) (default=json)

## Setup

The `'config.py'` file is required for python scripts to connect to MySQL and perform the required actions. 
```python
CONNECT = {
    'mysql_db': {
        'host': 'localhost',
        'user': 'root',
        'password': '*****',
        'database': 'mysql'
    },
    'movie_ratings': {
        'host': 'localhost',
        'user': 'root',
        'password': '*****',
        'database': 'students_rooms'
    }
}
```
You need to change your parameters to connect to MySQL.

### Python libraries
```bash
pip install click
pip install mysql
pip install mysql.connector
pip install json
pip install dict2xml 
```

## Task

Необходимо:
    • с использованием базы MySQL (или другую реляционную БД, например, PostgreSQL) создать схему данных соответствующую данным файлам (связь многие к одному).
    • написать скрипт, целью которого будет загрузка этих двух файлов и запись данных в базу

Запросы к базе данных чтобы вернуть:
    • список комнат и количество студентов в каждой из них
    • top 5 комнат, где самый маленький средний возраст студентов
    • top 5 комнат с самой большой разницей в возрасте студентов
    • список комнат где живут разнополые студенты.

Требования и замечания:
    • предложить варианты оптимизации запросов с использования индексов
    • в результате надо сгенерировать SQL запрос который добавить нужные индексы
    • выгрузить результат в формате JSON или XML
    • всю "математику" делать стоит на уровне БД.
    • командный интерфейс должен поддерживать следующие входные параметры
        ◦ students (путь к файлу студентов)
        ◦ rooms (путь к файлу комнат)
        ◦ format (выходной формат: xml или json)
        ◦ использовать ООП и SOLID.
        ◦ отсутствие использования ORM (использовать SQL)
