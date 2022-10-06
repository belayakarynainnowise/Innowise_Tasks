import snowflake.connector
from airflow.models import Variable


con = snowflake.connector.connect(
        user=Variable.get('snowflake_user'),
        password=Variable.get('snowflake_password'),
        account=Variable.get('snowflake_account'),
        warehouse=Variable.get('snowflake_warehouse'),
        database=Variable.get('snowflake_database'),
        schema=Variable.get('snowflake_schema'),
    )
snow_cursor = con.cursor()


def prepare_snowflake():
    """
    Creating the necessary tables and streams in Snowflake
    """
    snow_cursor.execute('USE WAREHOUSE WAREHOUSE')
    snow_cursor.execute('USE ROLE ACCOUNTADMIN')
    snow_cursor.execute('USE DATABASE MY_DATABASE')
    snow_cursor.execute('USE SCHEMA PUBLIC')
    snow_cursor.execute('CREATE TABLE RAW_TABLE("_id" VARCHAR(50), "IOS_App_Id" INTEGER, "Title" text, "Developer_Name" text, "Developer_IOS_Id" FLOAT, "IOS_Store_Url" text, "Seller_Official_Website" text, "Age_Rating" VARCHAR(50), "Total_Average_Rating" FLOAT, "Total_Number_of_Ratings" FLOAT, "Average_Rating_For_Version" FLOAT, "Number_of_Ratings_For_Version" INTEGER, "Original_Release_Date" VARCHAR, "Current_Version_Release_Date" VARCHAR, "Price_USD" FLOAT, "Primary_Genre" VARCHAR(50), "All_Genres" VARCHAR, "Languages" VARCHAR, "Description" TEXT)')
    snow_cursor.execute('CREATE OR REPLACE TABLE STAGE_TABLE LIKE RAW_TABLE')
    snow_cursor.execute('CREATE TABLE MASTER_TABLE("_id" VARCHAR(50),"IOS_App_Id" INTEGER,"Title" text, "Developer_Name" text,"Developer_IOS_Id" FLOAT, "IOS_Store_Url" text, "Seller_Official_Website" text, "Age_Rating" VARCHAR(50),"Total_Average_Rating" FLOAT, "Total_Number_of_Ratings" FLOAT, "Average_Rating_For_Version" FLOAT,"Number_of_Ratings_For_Version" INTEGER,"Original_Release_Date" TIMESTAMP_TZ,"Current_Version_Release_Date" TIMESTAMP_TZ,"Price_USD" FLOAT, "Primary_Genre" VARCHAR(50), "All_Genres" ARRAY, "Languages" ARRAY,"Description" TEXT)')
    snow_cursor.execute('CREATE OR REPLACE STREAM RAW_STREAM ON TABLE RAW_TABLE')
    snow_cursor.execute('CREATE OR REPLACE STREAM STAGE_STREAM ON TABLE STAGE_TABLE')