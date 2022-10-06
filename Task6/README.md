# Task 6. Snowflake


## Задание запускалось в Google Cloud Platform(Cloud Composer)

### Подготовка среды

#### Snowflake

- Создать Warehouse(у меня WAREHOUSE)
- Создать базу данных(у меня MY_DATABASE)

#### Cloud Composer

- Создать bucket в Google Storage, закинуть туда файл с данными(763_plus_IOS_Apps_Info.scv) и файл с командами Snowflake(transorm_data.txt)
![Image alt](https://github.com/belayakarynainnowise/Innowise_Tasks/blob/main/Task6/images/bucket_cloud_storage.PNG)

- Установить необходимые библиотеки для работы с Snowflake
![Image alt](https://github.com/belayakarynainnowise/Innowise_Tasks/blob/main/Task6/images/python-libraries.PNG)

- В AirFlow создать переменные с нужными данными 
![Image alt](https://github.com/belayakarynainnowise/Innowise_Tasks/blob/main/Task6/images/airflow_variables.PNG)

- В папку DAGS закинуть python- скрипты 
- ![Image alt](https://github.com/belayakarynainnowise/Innowise_Tasks/blob/main/Task6/images/dags_folder.PNG)






