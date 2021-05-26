import json
import xml.etree.ElementTree as xml
from pathlib import Path
import argparse
from mysql.connector import connect, Error


class PathsEqualError(Exception):
    def __str__(self):
        return "Two files have the same path"

class FileManager():
    def __init__(self, stud_file_path, rooms_file_path):
        self.stud_file_path = stud_file_path
        self.rooms_file_path = rooms_file_path

    def open_rooms_file(self):
        try:
            with open(Path(self.rooms_file_path), "r") as rooms_file:
                rooms_data = json.load(rooms_file)
            self.rooms_data = rooms_data
            return rooms_data
        except FileNotFoundError:
            self.rooms_file_path = input("Enter the correct path to rooms file: ")
            if self.rooms_file_path and self.rooms_file_path[0] in ('\'', "\""):
                self.rooms_file_path = self.rooms_file_path[1:-1]
            if self.stud_file_path == self.rooms_file_path:
                raise PathsEqualError
            return self.open_rooms_file()

    def open_students_file(self):
        try:
            with open(Path(self.stud_file_path), "r") as stud_file:
                stud_data = json.load(stud_file)
            self.stud_data = stud_data            
            return stud_data
        except FileNotFoundError:
            self.stud_file_path = input("Enter the correct path to students file: ")
            # Check if user entered path with or without starting ' or " to work correctly
            # because input puts these at the beginning by default
            if self.stud_file_path and self.stud_file_path[0] in ('\'', "\""):
                self.stud_file_path = self.stud_file_path[1:-1]
            # Check if two paths equal each other
            if self.stud_file_path == self.rooms_file_path:
                raise PathsEqualError
            return self.open_students_file()    

class DatabaseManager():
    def __init__(self):
        try:
            self.user = input("Имя пользователя: ")
            self.password = input("Пароль: ")
            self.connection = connect(
                    host="localhost",
                    user=self.user,
                    password=self.password,
                )    
            self.cursor = self.connection.cursor()
            self.output_data = []
        except Error as e:
            print(e)
            exit()

    def create_db(self):
        try:
            create_db_query = "CREATE DATABASE rooms_students"
            self.cursor.execute(create_db_query)
        except Error as e:
            print(e)
            print("Using the existing database")
        finally:
            self.db = connect (
                host="localhost",
                user=self.user,
                password=self.password,
                database="rooms_students",
            )

    def create_tables(self):
        create_rooms_table_query = """
            CREATE TABLE rooms(
            id INT PRIMARY KEY,
            name VARCHAR(20)
            )
            """

        create_students_table_query = """
            CREATE TABLE students(
            id INT PRIMARY KEY,
            name VARCHAR(100),
            birthday DATETIME,
            sex varchar(1),
            room_id INT,
            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
            """
        
        try:
            with self.db.cursor() as cursor:
                cursor.execute(create_rooms_table_query)
                self.db.commit()
        except Error as e:
            print("The table \"rooms\" already exist")

        try:
            with self.db.cursor() as cursor:
                cursor.execute(create_students_table_query)
                self.db.commit()
        except Error as e:
            print("The table \"students\" already exist")

    def insert_into_talbes(self, rooms_data, stud_data):
        insert_into_rooms_data = [(room["id"], room["name"]) for room in rooms_data]
        insert_into_students_data = [(
            student["id"],
            student["name"],
            student["birthday"], 
            student["sex"], 
            student["room"]) 
            for student in stud_data]

        insert_rooms_query = """
            INSERT INTO rooms
            (id, name)
            VALUES ( %s, %s )
        """

        insert_students_query = """
            INSERT INTO students
            (id, name, birthday, sex, room_id)
            VALUES ( %s, %s, %s, %s, %s )
        """

        try:
            with self.db.cursor() as cursor:
                cursor.executemany(insert_rooms_query, insert_into_rooms_data)
                self.db.commit()
        except Error as e:
            print("The table \"rooms\" has been already populated with data")

        try:
            with self.db.cursor() as cursor:
                cursor.executemany(insert_students_query, insert_into_students_data)
                self.db.commit()
        except Error as e:
            print("The table \"students\" has been already populated with data")

    def get_room_list_and_qty_in_it(self):
        select_query = """
                select rooms.name, count(room_id) as qty_of_students
                from rooms 
                inner join students on students.room_id = rooms.id
                group by rooms.id;
            """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
                self.output_data.append(
                    {
                        "List of rooms and their students quantity": {row[0]: row[1] for row in result}
                    }
                )
        except Error as e:
            print(e)
        
    def top5_rooms_with_min_avg_age(self):
        select_query = """
            select rooms.name, avg(year(current_date()) - year(students.birthday)) as stud_age
            from rooms 
            inner join students on students.room_id = rooms.id
            group by rooms.name
            order by stud_age asc
            limit 5;
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
                self.output_data.append(
                    {
                        "Top 5 rooms with min avg age": {row[0]: str(row[1]) for row in result}
                    }
                )
        except Error as e:
            print(e)
    
    def top5_rooms_with_max_div_age(self):
        select_query = """
            select rooms.name, max(year(students.birthday)) - min(year(students.birthday)) as age_gap
            from rooms 
            inner join students on students.room_id = rooms.id
            group by rooms.name
            order by age_gap desc
            limit 5;
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
                self.output_data.append(
                    {
                        "Top 5 rooms with biggest age differences": {row[0]: str(row[1]) for row in result}
                    }
                )
        except Error as e:
            print(e)
    
    def rooms_with_dif_sex(self):
        select_query = """
            select a.id, a.name, count(a.id) as cnt
            from (
            select rooms.id, rooms.name
            from rooms 
            inner join students on students.room_id = rooms.id
            group by room_id, students.sex) as a
            group by a.id
            having cnt = 2;
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
                self.output_data.append(
                    {
                        "Rooms with different sex": {str(row[0]): row[1] for row in result}
                    }
                )
        except Error as e:
            print(e)
    
    def add_index(self):
        add_index_query = """
        alter table `students` add index `sex_index` (`sex`);
        alter table `students` add index `age_index` (`birthday`);
        """

        try:
            with self.db.cursor() as cursor:
                cursor.execute(add_index_query)
        except Error as e:
            print(e)

    def __del__(self):
        if hasattr(self, "connection"):
            self.cursor.close()
            self.connection.close()

class BaseStudentsRoomsManager():
    def __init__(self, stud_file_path, rooms_file_path):
        file_manager = FileManager(stud_file_path, rooms_file_path)
        file_manager.open_rooms_file()
        file_manager.open_students_file()
        
        db_manager = DatabaseManager()
        db_manager.create_db()
        db_manager.create_tables()
        db_manager.insert_into_talbes(file_manager.rooms_data, file_manager.stud_data)
        
        # Index
        db_manager.add_index()
        
        # Queries
        db_manager.get_room_list_and_qty_in_it()
        db_manager.top5_rooms_with_min_avg_age()
        db_manager.top5_rooms_with_max_div_age()
        db_manager.rooms_with_dif_sex()
        
        self.combined_data = db_manager.output_data
          
    def output_data(self):
        raise NotImplementedError ("Subclass must contain output_data method")

class JSONStudentsRoomsManager(BaseStudentsRoomsManager):
    def output_data(self):
        with open("output.json", "w") as output_file:
            json.dump(self.combined_data, output_file, indent=4)
        return "The report was formed!"

class XMLStudentsRoomsManager(BaseStudentsRoomsManager):
    def output_data(self):
        root = xml.Element("Result_of_queries")
        for query in self.combined_data:
            name_of_query, results_of_query = query.popitem()
            query_xml = xml.Element("query", attrib={"Name": name_of_query})
            root.append(query_xml)
            for result in results_of_query:
                result_of_query = xml.SubElement(query_xml, "result")
                result_of_query.text = result + " - " + str(results_of_query[result])
                
        tree = xml.ElementTree(root)
        with open("output.xml", "wb") as output_file:
            tree.write(output_file)
        return "The report was formed!"

def validate_input_format(ftype):
    availiable_formats = ["json", "xml"]
    if ftype not in availiable_formats:
        raise argparse.ArgumentTypeError(f"{ftype} is an invalid output format")
    return ftype

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-students", required=True)
    parser.add_argument("-rooms", required=True)
    parser.add_argument("-format", type=validate_input_format, default="json")
    return parser

if __name__ == "__main__":    
    parser = get_parser()
    params = parser.parse_args()

    stud_file_path = params.students
    rooms_file_path = params.rooms

    if stud_file_path == rooms_file_path:
        raise PathsEqualError

    output_format = params.format

    format_manager_dict = {
        "json": JSONStudentsRoomsManager,
        "xml": XMLStudentsRoomsManager,
        }
    
    manager = format_manager_dict.get(output_format, False)
    
    if not manager:
        raise NotImplementedError("We don't support this output format yet")

    output = manager(stud_file_path, rooms_file_path).output_data()
    print(output)