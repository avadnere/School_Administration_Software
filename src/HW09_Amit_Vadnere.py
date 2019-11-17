"""
Created on 2019-11-12 16:27:18
@author: Amit Vadnere
Data repository of courses, students, and instructor
"""
import collections
import os
import sqlite3
from prettytable import PrettyTable


def get_instructor_course_summary():
        
        """ prints the preety table with instructor summary using database"""
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "810_startup.db")
        try:
            db = sqlite3.connect(db_path)

        except sqlite3.OperationalError:
            return f"Error unable to open database at {db_path}"
        
        else:
            SQL_STATEMENT = """SELECT instructors.cwid, 
                            instructors.name, 
                            instructors.Dept, 
                            grades.Course, 
                            count(grades.StudentCWID) as Student_Count
                            FROM Grades
                            inner join instructors on 
                            instructors.CWID = Grades.InstructorCWID 
                            group by 
                            Grades.course , 
                            instructors.cwid 
                            order by count(*) 
                            DESC"""

            
            data = [{'cwid': cwid, 'Name':name, 'Department':department, 'Course':course, 'Student':Student_Count}
                    for cwid, name, department, course, Student_Count in db.execute(SQL_STATEMENT)]

            db.close()
            
            return data

class Repository:

    """ Holds the information about the students, instructors and grades for a single University"""

    COURSE_CATALOG = collections.defaultdict(lambda: collections.defaultdict(set))
    DB_FILE = "810_startup.db"
    def __init__(self, university_name, directory, pretty_print):

        """initalize the variables."""
        self.__university_name = university_name
        self.__directory = directory
        self.__student_summary = dict()
        self.__instructor_summary = dict()

        self.get_student()
        self.get_instructor()
        self.get_grade()
        self.create_course_catalog()
        if pretty_print:
            print("Major Summary")
            print(self.pretty_print_major_summary())
            print("Student Summary")
            print(self.pretty_print_student_summary())
            print("Instructor Summary")
            print(self.pretty_print_instructor_summary())
            print("Instructor Summary using Database")
            print(self.instructor_table_db(Repository.DB_FILE))
            
        

    def file_reading_gen(self, path, fields, sep='\t', header=False):

        """ yield a tuple with all of the values from a single line in the file """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"cannot open the {path}")
        fp = open(path, 'r')
        with fp:
            for (indx, line) in enumerate(fp):
                fields_array = line.strip().split(sep)
                if len(fields_array) != fields:
                    raise ValueError(f"‘{path}’ has {len(fields_array)} fields on line {indx+1} but expected {fields}")
                else:
                    if header:
                        header = False
                        continue
                    else:
                        yield tuple(i for i in fields_array)

    def get_student(self):

        """ get the student detail"""
        file_name = os.path.join(self.__directory, "students.txt")
        try:
            for student in self.file_reading_gen(file_name, 3, '\t', header=True):
                self.__student_summary[student[0]] = Student(cwid=student[0], name=student[1],
                                                             major=student[2])

        except FileNotFoundError as fnfe:
            print(fnfe)

        except ValueError as ve:
            print(ve)

        except Exception as error:
            print(f"File cannot be open {self.__directory} {error}")

    def get_instructor(self):

        """ get the instructor details"""
        file_name = os.path.join(self.__directory, "instructors.txt")
        try:
            for instructor in self.file_reading_gen(file_name, 3, '\t', header=True):
                self.__instructor_summary[instructor[0]] = Instructor(instructor[0], instructor[1],
                                                                      instructor[2])

        except FileNotFoundError as fnfe:
            print(fnfe)

        except ValueError as ve:
            print(ve)

        except Exception as error:
            print(f"File cannot be open {self.__directory} {error}")

    def get_grade(self):

        """ get the instructor details"""
        file_name = os.path.join(self.__directory, "grades.txt")
        try:
            for student in self.file_reading_gen(file_name, 4, '\t', header=True):
                student_instance = self.__student_summary[student[0]]
                instructor_instance = self.__instructor_summary[student[3]]
                instructor_instance.add_course(student[1])
                if student[2] in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']:
                    student_instance.add_course_and_grade(student[1], student[2])

        except FileNotFoundError as fnfe:
            print(fnfe)

        except ValueError as ve:
            print(ve)

        except Exception as error:
            print(f"File cannot be open {self.__directory} {error}")

    def create_course_catalog(self):

        "creates course catalog for all majors"
        file_name = os.path.join(self.__directory, "majors.txt")
        try:
            for major in self.file_reading_gen(file_name, 3, '\t', header=True):
                if major[1] == "R":
                    major_Requirement = Repository.COURSE_CATALOG[major[0]]
                    major_Requirement["Required"].add(major[2])

                elif major[1] == "E":    
                    major_Requirement = Repository.COURSE_CATALOG[major[0]]
                    major_Requirement["Elective"].add(major[2])

                else:
                    raise ValueError("Unexpected Value of flag in major.txt")

        except FileNotFoundError as fnfe:
            print(fnfe)

        except ValueError as ve:
            print(ve)

        except Exception as error:
            print(f"File cannot be open {self.__directory} {error}")


    def pretty_print_student_summary(self):

        """ prints the preety table with student summary"""
        try:

            table = PrettyTable(field_names=Student.FIELD_NAME)

            for student_detail in self.__student_summary.values():
                pretty_row = student_detail.get_student_row()
                table.add_row(pretty_row)
            
            return table

        except ValueError as ve:
            print(ve)

    def pretty_print_major_summary(self):
    
        """ prints the preety table with major summary"""
        MAJOR_FIELD_NAME = ["Dept", "Reuquired", "Electives"]
        table = PrettyTable(field_names=MAJOR_FIELD_NAME)
        for dept, major_details in Repository.COURSE_CATALOG.items():
            pretty_row = (dept, major_details["Required"], major_details["Elective"])
            table.add_row(pretty_row)

        return table

    def instructor_table_db(self, db_path):
        
        """ prints the preety table with instructor summary using database"""
        table = PrettyTable(field_names=Instructor.FIELD_NAME)

        SQL_STATEMENT = """SELECT instructors.cwid, 
                        instructors.name, 
                        instructors.Dept, 
                        grades.Course, 
                        count(grades.StudentCWID) as Student_Count
                        FROM grades
                        inner join instructors on 
                        instructors.CWID = grades.InstructorCWID 
                        group by 
                        grades.course , 
                        instructors.cwid 
                        order by count(*) 
                        DESC"""

        db = sqlite3.connect(db_path)
        for row in db.execute(SQL_STATEMENT):
            table.add_row(row)

        return table

    def pretty_print_instructor_summary(self):

        """ prints the preety table with Instructor summary"""
        table = PrettyTable(field_names=Instructor.FIELD_NAME)

        for instructor_details in self.__instructor_summary.values():
            for row in instructor_details.get_instructor_row():
                table.add_row(row)

        return table

    def get_university_name(self):

        """ return the university name """
        return self.__university_name

    def get_directory(self):

        """ return the department"""
        return self.__directory

    def get_instructor_summary(self):

        """ return the list of instructor with id as cwid and instructor object"""
        return self.__instructor_summary

    def get_student_summary(self):

        """ return the list of student  with id as cwid and student object """
        return self.__student_summary

class Student:

    "Holds all of the details of a student"

    FIELD_NAME = ['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required', 'Remaining Electivies']

    def __init__(self, cwid, name, major):

        """ initializing the student variables """
        self.__name = name
        self.__major = major
        self.__cwid = cwid
        self.__courses = collections.defaultdict(str)

    def add_course_and_grade(self, course, grade):

        """ Store the classes taken and the grade """
        self.__courses[course] = grade

    def get_student_row(self):

        """ return the student detail for pretty row """
        courseList = [course for course in self.__courses]
        pretty_row = (self.__cwid, self.__name, self.__major, sorted(courseList), 
                      self.get_remaining_required(), self.get_remaining_elective())
        return pretty_row

    def get_cwid(self):

        """ return the cwid for student """
        return self.__cwid

    def get_major(self):

        """ return the major for student """
        return self.__major

    def get_name(self):

        """ return the courses for student"""
        return self.__name

    def get_courses(self):

        """ return the courses for student"""
        return self.__courses
    
    def get_remaining_required(self):
        
        """return remaining required courses"""
        courseList = set(course for course in self.__courses)
        major_detail = Repository.COURSE_CATALOG[self.__major]
        if len(major_detail) < 1:
            raise ValueError(f"No Major as {self.__major} found in Course Catalog for cwid:{self.__cwid}")
        required_courses = major_detail["Required"]

        return required_courses-courseList
    
    def get_remaining_elective(self):
        
        """return remaining elective courses"""
        courseList = set(course for course in self.__courses)
        major_detail = Repository.COURSE_CATALOG[self.__major]
        if len(major_detail) < 1:
            raise ValueError(f"No Major as {self.__major} found in Course Catalog for cwid:{self.__cwid}")
        elective_courses = major_detail["Elective"]
        remaining_elective = elective_courses-courseList
        if len(remaining_elective) == len(elective_courses):
            return remaining_elective
        else:
            return None

class Instructor:

    "Holds all of the details of a Instructor"

    FIELD_NAME = ['CWID', 'Name', 'Department', 'Course', 'Student']

    def __init__(self, cwid, name, department):

        """ initializing the Instructor variables """
        self.__cwid = cwid
        self.__name = name
        self.__department = department
        self.__courses = collections.defaultdict(int)

    def add_course(self, course):

        "Store the count of student per course "
        self.__courses[course] += 1

    def get_instructor_row(self):

        """ return the instructor detail for pretty row """
        for course_name, enrolment_count in self.__courses.items():
            yield[self.__cwid, self.__name, self.__department, course_name, enrolment_count]

    def get_cwid(self):

        """ return the cwid for instructor """
        return self.__cwid

    def get_department(self):

        """ return the department for instructor """
        return self.__department

    def get_name(self):

        """ return the name for instructor """
        return self.__name

    def get_courses(self):

        """ return the courses for instructor """
        return self.__courses

get_instructor_course_summary()