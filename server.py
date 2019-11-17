"""
    School_Adminstration_Software Server
"""

from flask import Flask, render_template
from src.HW09_Amit_Vadnere import get_instructor_course_summary

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template("index.html",
                            heading="Hello Professor",
                            para_body="Thank you for your help! I really enjoyed the course!"

                        )

@app.route('/Goodbye')
def see_ya():
    return "see you later!"

@app.route('/instructor_course')
def template_demo():
    
    data = get_instructor_course_summary()
    return render_template("instructorSummary.html",
                            header1="Stevens Repository",
                            header2="Number of students by course and instructor",
                            data=data)

app.run(debug=True)