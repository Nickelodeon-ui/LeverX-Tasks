import json
import xml.etree.ElementTree as xml
from pathlib import Path
import argparse

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

class CombineDataManager():
    def __init__(self, stud_data, room_data):
        self.stud_data = stud_data
        self.rooms_data = room_data

    def combine_data(self):
            for student in self.stud_data:
                room = student["room"]
                name = student["name"]
                room_data = self.rooms_data[room]
                if "students" not in room_data.keys():
                    room_data["students"] = [name,]
                else:
                    room_data["students"].append(name)
            return self.rooms_data

class BaseStudentsRoomsManager():
    def __init__(self, stud_file_path, rooms_file_path):
        file_manager = FileManager(stud_file_path, rooms_file_path)
        combine_manager = CombineDataManager(file_manager.open_students_file(), file_manager.open_rooms_file())
        self.combined_data = combine_manager.combine_data()
          
    def output_data(self):
        raise NotImplementedError ("Subclass must contain output_data method")

class JSONStudentsRoomsManager(BaseStudentsRoomsManager):
    def output_data(self):
        with open("output.json", "w") as output_file:
            json.dump(self.combined_data, output_file, indent=4)
        return "The report was formed!"

class XMLStudentsRoomsManager(BaseStudentsRoomsManager):
    def output_data(self):
        root = xml.Element("rooms")
        for room in self.combined_data:
            room_id = str(room["id"])
            student_names = room["students"]
            room = xml.Element("room", attrib={"id": room_id})
            root.append(room)
            for student_name in student_names:
                student = xml.SubElement(room, "student")
                student.text = student_name
                
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
        "json": JSONStudentsRoomsManager(stud_file_path, rooms_file_path),
        "xml": XMLStudentsRoomsManager(stud_file_path, rooms_file_path),
        }
    
    manager = format_manager_dict.get(output_format, False)
    
    if not manager:
        raise NotImplementedError("We don't support this output format yet")

    output = manager.output_data()
    print(output)