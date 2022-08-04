import click
import mysql
from mysql.connector import connection, Error
from config import CONNECT
import json
from dict2xml import dict2xml


@click.command(name="main")
@click.option("--students_location", type=str, default="data_files", help="location of  \"students.json\" file",
              metavar="students")
@click.option("--rooms_location", type=str, default="data_files", help="location of \"rooms.json\" file",
              metavar="rooms")
@click.option("--save_format", type=str, default="json", help="format for saving the result (xml/json) ",
              metavar="format")


def main(students_location, rooms_location, save_format):
 create_database()
 try:
     conn = connection.MySQLConnection(**CONNECT["students_rooms"])
     cursor = conn.cursor()
     filling_rooms_table(rooms_location, conn, cursor)
     filling_students_table(students_location, conn, cursor)
     menu(cursor, save_format)
     conn.close()
 except mysql.connector.Error as err:
     print("Something went wrong: {}".format(err))


def filling_rooms_table(rooms_location, conn, cursor):
    """
    Reading rooms.json file and writing data to the database table
    :param rooms_location:location of rooms.json file
    :param conn:MySQLConnection object
    :param cursor:cursor, which abstracts the process of accessing database records
    """
    try:
        rooms_file = open(f"{rooms_location}/rooms.json", mode="r", encoding="UTF-8").read()
        rooms_obj = json.loads(rooms_file)
    except OSError:
        print('Error with file. Not enough access rights or invalid file name')
    except MemoryError:
        print('Not enough memory')
    for item in rooms_obj:
        room_id = item.get("id")
        room_name = item.get("name")
        cursor.execute("INSERT INTO rooms (room_id, room_name) VALUES (%s, %s)", (room_id, room_name))
    conn.commit()


def filling_students_table(students_location, conn, cursor):
    """
    Reading students.json file and writing data to the database table
    :param students_location:location of students.json file
    :param conn:MySQLConnection object
    :param cursor:cursor, which abstracts the process of accessing database records
    """
    try:
        students_file = open(f"{students_location}/students.json", mode="r", encoding="UTF-8").read()
        students_obj = json.loads(students_file)
    except OSError:
        print('Error with file. Not enough access rights or invalid file name')
    except MemoryError:
        print('Not enough memory')
    for item in students_obj:
        student_id = item.get("id")
        student_name = item.get("name")
        student_birthday = item.get("birthday")
        student_sex = item.get("sex")
        student_room = item.get("room")
        cursor.execute(
            "INSERT INTO students (student_id, student_name, birthday, sex , room_id) VALUES (%s, %s,%s, %s,%s)",
            (student_id, student_name, student_birthday, student_sex, student_room))
    conn.commit()


def create_database():
    """
    Connecting to MYSQL.Running sql-script to create a database and tables
    """
    try:
        conn = connection.MySQLConnection(**CONNECT["mysql_db"])
        cursor = conn.cursor()
        reader = open("sql/create_database.sql", 'r')
        sqlFile = reader.read()
        reader.close()
        sqlCommands = sqlFile.split(';')
        for command in sqlCommands:
            cursor.execute(command)
        conn.close
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


def menu(cursor, save_format):
    """
    Selecting a database query
    :param cursor:cursor, which abstracts the process of accessing database records
    :param save_format: format for saving the result (xml/json)
    """
    print(" 1 - a list of rooms and the number of students in each room / список комнат и количество студентов в каждой из них ")
    print(" 2 - top 5 rooms with the smallest average age of students / top 5 комнат, где самый маленький средний возраст студентов ")
    print(" 3 - Top 5 rooms with the largest age difference between students / top 5 комнат с самой большой разницей в возрасте студентов ")
    print(" 4 - a list of rooms where different-sex students live / список комнат где живут разнополые студенты ")
    print(" 0 - exit ")

    response = input("Enter your choice:  ")

    if response == '1':
        find_student_count(cursor, save_format)
    elif response == '2':
        find_min_avg_age(cursor, save_format)
    elif response == '3':
        find_age_difference(cursor, save_format)
    elif response == '4':
        find_rooms_different_sex(cursor, save_format)
    elif response == '0':  # Exit the program
        print('Goodbye')
    else:
        print('Unrecognized command.  Try again.')


def find_student_count(cursor, save_format):
    """
    Execution of the query to the database, getting the result, calling the function of saving the result to the file
    :param cursor:cursor, which abstracts the process of accessing database records
    :param save_format: format for saving the result (xml/json)
    """
    cursor.execute("select room_name, count(*) as student_count from rooms inner join students on rooms.room_id=students.room_id group by room_name")
    result = cursor.fetchall()
    items = [dict(zip([key[0] for key in cursor.description], row)) for row in result]
    save_file(items, save_format)


def find_min_avg_age(cursor, save_format):
    """
    Execution of the query to the database, getting the result, calling the function of saving the result to the file
    :param cursor:cursor, which abstracts the process of accessing database records
    :param save_format: format for saving the result (xml/json)
    """
    cursor.execute(
        "select room_name, avg(TIMESTAMPDIFF(year,birthday, now())) as min_avg_age  from rooms inner join students on rooms.room_id=students.room_id  group by rooms.room_id ORDER BY min_avg_age LIMIT 5")
    result = cursor.fetchall()
    items = [dict(zip([key[0] for key in cursor.description], row)) for row in result]
    save_file(items, save_format)


def find_age_difference(cursor, save_format):
    """
    Execution of the query to the database, getting the result, calling the function of saving the result to the file
    :param cursor:cursor, which abstracts the process of accessing database records
    :param save_format: format for saving the result (xml/json)
    """
    cursor.execute(
        "select room_name, max((TIMESTAMPDIFF(year,birthday, now())))-min( (TIMESTAMPDIFF(year,birthday, now()))) as age_difference  from rooms inner join students on rooms.room_id=students.room_id  group by rooms.room_id order by age_difference desc limit 5")
    result = cursor.fetchall()
    items = [dict(zip([key[0] for key in cursor.description], row)) for row in result]
    save_file(items, save_format)


def find_rooms_different_sex(cursor, save_format):
    """
    Execution of the query to the database, getting the result, calling the function of saving the result to the file
    :param cursor:cursor, which abstracts the process of accessing database records
    :param save_format: format for saving the result (xml/json)
    """
    cursor.execute(
        "select distinct room_name from rooms inner join students on rooms.room_id=students.room_id  where sex in('F','M') order by room_name")
    result = cursor.fetchall()
    items = [dict(zip([key[0] for key in cursor.description], row)) for row in result]
    save_file(items, save_format)


def save_file(items, save_format) -> bool:
    """
    Saving the result to a file of the selected format
    :param items:query Result
    :param save_format:format for saving the result (xml/json)
    """

    file_name = input("Enter a file name to save the result:  ")
    if save_format == "xml":
        xml_format = dict2xml(items, wrap='room', indent="   ")
        try:
            with open(f"{file_name}.xml", "w") as f:
                f.write(xml_format)
        except MemoryError:
            print('Not enough memory')
    else:
        try:
            json_format = json.dumps(items, ensure_ascii=False, default=str)
            with open(f"{file_name}.json", "w") as f:
                f.write(json_format)
        except MemoryError:
            print('Not enough memory')
    return True


if __name__ == '__main__':
    main()