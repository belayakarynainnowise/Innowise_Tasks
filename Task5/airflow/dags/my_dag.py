from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import pandas as pd
from pymongo import MongoClient


file_path = Variable.get('file_path')
mongo_host = Variable.get('mongo_host')
mongo_port = int(Variable.get('mongo_port'))
mongo_db = Variable.get('mongo_db')
mongo_collection_name = Variable.get('mongo_collection_name')

default_args = {
    'owner': 'karina',
    'start_date': days_ago(0),
    'depends_on_past': False,
    'provide_context': True
}


def extract_data(**kwargs):
    ti = kwargs['ti']
    data = pd.read_csv(file_path)
    ti.xcom_push(key='extracted_data', value=data)


def transform_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract_data_task', key='extracted_data')
    #data=data.dropna()
    data = data.fillna('-')
    data = data.sort_values('at')
    data['content'] = data['content'].replace(r'[^a-zA-Z0-9.,\-:;&!/@()\'\"\ ]', '', regex=True)
    data_dict = data.to_dict('records')
    ti.xcom_push(key='transformed_data', value=data_dict)


def load_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform_data_task', key='transformed_data')
    client = MongoClient(mongo_host, mongo_port)
    db = client[mongo_db]
    collection = db[mongo_collection_name]
    collection.insert_many(data)
    client.close()


with DAG(
    'tiktok_reviews_dag',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:
    extract_data = PythonOperator(
        task_id='extract_data_task',
        python_callable=extract_data,
    )
    transform_data = PythonOperator(
        task_id='transform_data_task',
        python_callable=transform_data,
    )
    load_data = PythonOperator(
        task_id='load_data_task',
        python_callable=load_data,
    )
    extract_data >> transform_data >> load_data