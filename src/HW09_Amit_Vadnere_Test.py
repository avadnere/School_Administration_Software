"""
Created on 2019-11-12 16:27:10
@author: Amit Vadnere
Test the Data repository of courses, students, and instructor
"""

import unittest
import os
from HW09_Amit_Vadnere import Repository, Student, Instructor, get_instructor_course_summary

class TesTInstructorSummaryFunction(unittest.TestCase):
    "Test the get_instructor_course_summary"

    def test_get_instructor_course_summary(self):
        """Test the get_instructor_course_summary"""
        data = get_instructor_course_summary()
        self.assertEqual(data[0]["cwid"],"98763")
        self.assertEqual(data[0]["Name"],"Rowland, J")

class TestRepository(unittest.TestCase):

    """Test the Repository Class"""

    def test_init(self):
        """ Test the init function """
        repository = Repository("STEVENS", "F:", False)
        self.assertEqual(repository.get_directory(),"F:")
        self.assertEqual(repository.get_university_name(), "STEVENS")

    def test_file_reading_gen(self):
        """ Reading File Properly"""
        
        expected_case_1 = [ ("10103","Jobs, S","SFEN"),
                            ("10115","Bezos, J","SFEN"),
                            ("10183","Musk, E","SFEN"),
                            ("11714","Gates, B","CS")
                           ]

        repository = Repository( "STEVENS", os.getcwd(), False)
        self.assertEqual(list(repository.file_reading_gen(path="students.txt", sep="\t", fields=3, header=True)),
                         expected_case_1)
        with self.assertRaises(ValueError):
            list(repository.file_reading_gen(path="students.txt", sep="\t", fields=4, header=True))
            
        with self.assertRaises(FileNotFoundError):
            list(repository.file_reading_gen(path="random_file.txt", fields=3, header=True))

    def test_get_student(self):

        """ Reading student file properly """
        repository = Repository("STEVENS", os.getcwd(), False)
        student_summary_dict = repository.get_student_summary()
        student = student_summary_dict["10103"]
        self.assertEqual(student.get_name(), "Jobs, S")
        self.assertEqual(student.get_major(), "SFEN")

    def test_get_instructor(self):

        """ Reading Instructor file properly """
        repository = Repository("STEVENS", os.getcwd(), False)
        instructor_summary_dict = repository.get_instructor_summary()
        instructor = instructor_summary_dict["98764"]
        self.assertEqual(instructor.get_name(), "Cohen, R")
        self.assertEqual(instructor.get_department(), "SFEN")

    def test_get_grade(self):
    
        """ Reading and processing grade file properly  """
        repo = Repository("STEVENS", os.getcwd(), False)
        student_summary_dict = repo.get_student_summary()
        student = student_summary_dict["10115"]
        self.assertEqual(student.get_courses(), {"SSW 810":"A"})

    def test_instructor_table_db(self):
        
        """ Test the function that prints preety table with instructor summary using database  """
        repo = Repository("STEVENS", os.getcwd(), False)
        instructor_summary_table = repo.instructor_table_db(Repository.DB_FILE)
        temp = instructor_summary_table[0]
        first_row_cwid = temp.get_string(header=False,border=False,fields=["CWID"]).strip()
        self.assertEqual(first_row_cwid, "98763")

class TestStudent(unittest.TestCase):
    
    "Test that it Holds all of the details of a student"

    def test__init__(self):
    
        """ Test that the student variables are intialized properly """
        student = Student("10442085", "abc","Medicaps")
        self.assertEqual(student.get_cwid(), "10442085")
        self.assertEqual(student.get_name(), "abc")
        self.assertEqual(student.get_major(), "Medicaps")
    
    def test_get_remaining_required(self):

        """ Test function that return remaining required"""
        repository = Repository("NYU", os.getcwd(), False)
        student_summary = repository.get_student_summary()
        student_detail = student_summary["10103"]
        self.assertEqual(student_detail.get_remaining_required(), {'SSW 555', 'SSW 540'})
    
    def test_get_remaining_elective(self):
        
        """ Test function that return remaining elective"""
        repository = Repository("NYU", os.getcwd(), False)
        student_summary = repository.get_student_summary()
        student_detail = student_summary["10103"]
        self.assertEqual(student_detail.get_remaining_elective(), None)
        student_detail = student_summary["10115"]
        self.assertEqual(student_detail.get_remaining_elective(), {'CS 501', 'CS 546'})

class TestInstructor(unittest.TestCase):
    
    "Test that it Holds all of the details of a Instructor"

    def test_init__(self):
    
        """ Test the Instructor variables are  intialize properly """
        instructor = Instructor("1042055","abc","Medicaps")
        self.assertEqual(instructor.get_cwid(), "1042055")
        self.assertEqual(instructor.get_name(), "abc")
        self.assertEqual(instructor.get_department(), "Medicaps")

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    repo = Repository("NYU", os.getcwd(), True)
