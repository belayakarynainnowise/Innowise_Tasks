from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.window import Window
from pyspark.sql.functions import *



def main():
    spark = SparkSession\
        .builder\
        .config("spark.jars", "./postgresql-42.2.5.jar") \
        .master("local")\
        .appName("PySpark_Postgres")\
        .getOrCreate()

    connection = spark.read\
        .format("jdbc")\
        .option("url", "jdbc:postgresql://172.17.0.2:5432/pagila")\
        .option("user", "postgres")\
        .option("password", "secret")\
        .option("driver", "org.postgresql.Driver")


    menu(connection)


def get_table(connection, table_name):
    """
    Loading a table from the database into a dataframe
    :param connection: connection to the "pagila" database
    :param table_name: table name from the database
    :return: loaded table from the database,on the basis of which the dataframe will be created
    """
    return connection.option("dbtable", table_name).load()


def find_num_film_in_category(connection):
    """
    Executing of query N1
    :param connection: connection to the "pagila" database
    :return: query result
    """
    df_category = get_table(connection, "category")
    df_film_category = get_table(connection, "film_category")
    df_category_film_category = df_category\
        .join(df_film_category, "category_id", how="inner")
    df_num_film = df_category_film_category\
        .groupBy("name")\
        .count()
    return df_num_film.orderBy("count", ascending=False)


def find_films_not_in_inventory(connection):
    """
    Executing of query N4
    :param connection: connection to the "pagila" database
    :return: query result
    """
    df_film = get_table(connection, "film")
    df_inventory = get_table(connection, "inventory")
    df_film_inventory = df_film\
        .join(df_inventory, df_film.film_id == df_inventory.film_id, how="left")
    films_not_in_inventory = df_film_inventory\
        .filter(df_inventory.film_id.isNull())
    return films_not_in_inventory.select("title")


def find_top_category_by_money(connection):
    """
    Executing of query N3
    :param connection: connection to the "pagila" database
    :return: query result
    """
    df_payment = get_table(connection, "payment")
    df_rental = get_table(connection, "rental")
    df_film = get_table(connection, "film")
    df_inventory = get_table(connection, "inventory")
    df_category = get_table(connection, "category")
    df_film_category = get_table(connection, "film_category")
    df_join_tables = df_payment\
        .join(df_rental, "rental_id", how="inner") \
        .join(df_inventory, "inventory_id") \
        .join(df_film, "film_id") \
        .join(df_film_category, "film_id") \
        .join(df_category, "category_id")
    df_category_with_money = df_join_tables\
        .groupBy("name").sum("amount")\
        .orderBy("sum(amount)", ascending=False)
    return df_category_with_money.limit(1)


def find_cities_with_active_inactive_customers(connection):
    """
    Executing of query N6
    :param connection: connection to the "pagila" database
    :return: query result
    """
    df_city = get_table(connection, "city")
    df_address = get_table(connection, "address")
    df_customer = get_table(connection, "customer")
    df_city_address_customer = df_city\
        .join(df_address, "city_id", how="inner")\
        .join(df_customer, "address_id")
    df_active_customers = df_city_address_customer\
        .select("city", "active")\
        .where(col("active") == 1)
    df_active_customers_count = df_active_customers\
        .groupBy("city")\
        .agg(count("active").alias("active_count"))
    df_inactive_customers = df_city_address_customer\
        .select("city", "active")\
        .where(col("active") == 0)
    df_inactive_customers_count = df_inactive_customers\
        .groupBy("city")\
        .agg(count("active").alias("not_active_count"))
    df_active_inactive_customers = df_active_customers_count\
        .join(df_inactive_customers_count, "city", how="full")\
        .na.fill(0)
    return df_active_inactive_customers\
        .orderBy("not_active_count", ascending=False)


def find_top_actors_by_rent_count(connection):
    """
    Executing of query N2
    :param connection: connection to the "pagila" database
    :return: query result
    """
    df_rental = get_table(connection, "rental")
    df_inventory = get_table(connection, "inventory")
    df_film = get_table(connection, "film")
    df_actor = get_table(connection, "actor")
    df_film_actor = get_table(connection, "film_actor")
    df_rental_inventory_film = df_rental\
        .join(df_inventory, "inventory_id", how="inner")\
        .join(df_film, "film_id")
    df_film_count_in_rental = df_rental_inventory_film\
        .groupBy("film_id")\
        .agg(count("title").alias("film_count_in_rental"))
    df_join = df_actor.join(df_film_actor, 'actor_id', how="inner")\
        .join(df_film_count_in_rental, 'film_id')
    df_actors_by_rent_count = df_join\
        .groupBy("actor_id", "first_name", "last_name")\
        .sum("film_count_in_rental")
    return df_actors_by_rent_count\
        .orderBy("sum(film_count_in_rental)", ascending=False)\
        .limit(10)


def find_top_actors_in_children_category(connection):
    """
    Executing of query N5
    :param connection: connection to the "pagila" database
    :return: query result
    """
    df_film = get_table(connection, "film")
    df_film_category = get_table(connection, "film_category")
    df_category = get_table(connection, "category")
    df_actor = get_table(connection, "actor")
    df_film_actor = get_table(connection, "film_actor")
    df_join_tables = df_film\
        .join(df_film_category, "film_id", how="inner")\
        .join(df_category, "category_id")\
        .join(df_film_actor, "film_id")\
        .join(df_actor, "actor_id")
    df_count_actor_in_children = df_join_tables\
        .filter(col("name") == "Children")\
        .groupBy("actor_id", "last_name", "first_name")\
        .agg(count("title").alias("actor_count_film"))
    w = Window.orderBy(desc("actor_count_film"))
    df_top_actors_in_children = df_count_actor_in_children\
        .select("actor_id", "last_name", "first_name", "actor_count_film",
                rank().over(w).alias("rank"))
    return df_top_actors_in_children.filter(col("rank") < 4).drop("rank")


def find_top_category_by_rent(connection):
    """
    Executing of query N7
    :param connection: connection to the "pagila" database
    :return: query result
    """
    df_category = get_table(connection, "category")
    df_film_category = get_table(connection, "film_category")
    df_film = get_table(connection, "film")
    df_inventory = get_table(connection, "inventory")
    df_rental = get_table(connection, "rental")
    df_customer = get_table(connection, "customer")
    df_address = get_table(connection, "address")
    df_city = get_table(connection, "city")
    df_rental_with_duration = df_rental\
        .withColumn("rental_time",
                    (col("return_date").cast("long")-
                     col("rental_date").cast("long"))/3600)
    df_join_tables = df_category\
        .join(df_film_category, "category_id", how="inner")\
        .join(df_film, "film_id")\
        .join(df_inventory, "film_id")\
        .join(df_rental_with_duration, "inventory_id")\
        .join(df_customer, "customer_id")\
        .join(df_address, "address_id")\
        .join(df_city, "city_id")

    w = Window.partitionBy("city").orderBy(desc("sum(rental_time)"))
    df_rental_time_category_city = df_join_tables.groupBy("name", "city").sum("rental_time")\
        .withColumn("rank", rank().over(w)).filter(col("rank") == 1).drop("rank")

    df_result = df_rental_time_category_city.withColumn("new_city", lower("city")).select("new_city", "name", "sum(rental_time)").where(col("new_city").startswith("a") | col("new_city").contains("-"))
    return df_result.orderBy("new_city", "name")


def menu(connection):
    """
    Selecting a query
    :param connection: connection to the "pagila" database
    :return: output the result
    """
    print("1 - Вывести количество фильмов в каждой категории, отсортировать по убыванию.")
    print("2 - Вывести 10 актеров, чьи фильмы большего всего арендовали, отсортировать по убыванию. ")
    print("3 - Вывести категорию фильмов, на которую потратили больше всего денег")
    print("4 - Вывести названия фильмов, которых нет в inventory. Написать запрос без использования оператора IN.")
    print("5 - Вывести топ 3 актеров, которые больше всего появлялись в фильмах в категории “Children”. Если у нескольких актеров одинаковое кол-во фильмов, вывести всех.")
    print("6 - Вывести города с количеством активных и неактивных клиентов (активный — customer.active = 1). Отсортировать по количеству неактивных клиентов по убыванию.")
    print("7 - Вывести категорию фильмов, у которой самое большое кол-во часов суммарной аренды в городах(customer.address_id в этом city),и которые начинаются на букву “a”. То же самое сделать для городов в которых есть символ “-”. Написать все в одном запросе.")
    print("0- exit")

    response = input("Enter your choice:  ")

    if response == "1":
        find_num_film_in_category(connection).show()
    elif response == "2":
        find_top_actors_by_rent_count(connection).show()
    elif response == "3":
        find_top_category_by_money(connection).show()
    elif response == "4":
        find_films_not_in_inventory(connection).show()
    elif response == "5":
        find_top_actors_in_children_category(connection).show()
    elif response == "6":
        find_cities_with_active_inactive_customers(connection).show()
    elif response == "7":
        find_top_category_by_rent(connection).show()
    elif response == "0":
        print("Goodbye")
    else:
        print("Unrecognized command. Try again.")


if __name__ == '__main__':
    main()