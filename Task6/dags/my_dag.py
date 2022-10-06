from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
from google.cloud import storage
from connect_prepare_snowflake import con, snow_cursor, prepare_snowflake


default_args = {
    'owner': 'karina',
    'start_date': days_ago(0),
    'depends_on_past': False,
    'provide_context': True
}


def write_data_to_raw_table():
    """
    Reading 763_plus_IOS_Apps_Info.scv file and writing data to raw_table in Snowflake
    """
    data = pd.read_csv(Variable.get('file_path'))
    write_pandas(con, data, table_name='RAW_TABLE')


def write_from_raw_stream_to_stage_table():
    """
     Reading data from raw_stream and writing to stage_table in Snowflake
    """
    snow_cursor.execute('INSERT INTO STAGE_TABLE(SELECT "_id", "IOS_App_Id", "Title", "Developer_Name", "Developer_IOS_Id", "IOS_Store_Url", "Seller_Official_Website", "Age_Rating", "Total_Average_Rating", "Total_Number_of_Ratings", "Average_Rating_For_Version", "Number_of_Ratings_For_Version", "Original_Release_Date", "Current_Version_Release_Date", "Price_USD", "Primary_Genre", "All_Genres", "Languages", "Description" FROM RAW_STREAM)')


def transform_data_in_stage_table():
    """
    Transformation of data for writing to the master_table.
    Work with columns:Original_Release_Date,Current_Version_Release_Date,Languages,All_Genres.
    Snowflake commands are in a txt file
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(Variable.get('gcp_bucket'))
    blob = bucket.blob(Variable.get('file_with_commands'))
    file_with_commands = blob.download_as_text()
    commands = file_with_commands.split(';')
    for command in commands:
        snow_cursor.execute(command)


def write_from_stage_stream_to_master_table():
    """
    Reading data from stage_stream and writing to master_table table in Snowflake
    """
    snow_cursor.execute('INSERT INTO MASTER_TABLE (SELECT "_id", "IOS_App_Id", "Title", "Developer_Name", "Developer_IOS_Id", "IOS_Store_Url", "Seller_Official_Website", "Age_Rating", "Total_Average_Rating", "Total_Number_of_Ratings", "Average_Rating_For_Version", "Number_of_Ratings_For_Version","Original_Release_Date", "Current_Version_Release_Date", "Price_USD","Primary_Genre", strtok_to_array("All_Genres",\',\'), strtok_to_array("Languages",\',\'), "Description" FROM STAGE_STREAM)')
    snow_cursor.close()


with DAG(
    'snowflake_DAG',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:

    prepare_snowflake = PythonOperator(
        task_id='prepare_snowflake_task',
        python_callable=prepare_snowflake,
    )
    write_data_to_raw_table = PythonOperator(
        task_id='write_data_to_raw_table_task',
        python_callable=write_data_to_raw_table,
    )
    write_from_raw_stream_to_stage_table = PythonOperator(
        task_id='write_from_raw_stream_to_stage_table_task',
        python_callable=write_from_raw_stream_to_stage_table,
    )
    transform_data_in_stage_table = PythonOperator(
        task_id='transform_data_in_stage_table_task',
        python_callable=transform_data_in_stage_table,
    )
    write_from_stage_stream_to_master_table = PythonOperator(
        task_id='write_from_stage_stream_to_master_table_task',
        python_callable=write_from_stage_stream_to_master_table,
    )

    prepare_snowflake >> write_data_to_raw_table >> write_from_raw_stream_to_stage_table >> transform_data_in_stage_table >> write_from_stage_stream_to_master_table