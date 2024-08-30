# Import necessary libraries and modules for the Flask application
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from chatbot import studentDetails, chatbot_response
from db import create_student_details_tables, get_latest_student, get_all_students, delete_student, get_students_by_course
from dotenv import load_dotenv

# Load environment variables from the .env file for secure configuration
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Set the Google API Key from environment variables
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Ensure the database table for student details is created when the app starts
create_student_details_tables()

# Initialize an empty studentDetails object to hold current student data
current_student_details = studentDetails()

##############################################
# Routes: Define the endpoints for the web app
##############################################

# Route for the main index page (landing page)
@app.route('/')
def index():
    return render_template('index.html')


# Route for handling chatbot messages
@app.route('/chatbot', methods=['POST'])
def chatbot():
    if request.method == 'POST':
        # Extract the student's message from the request
        student_input = request.json['message']
        # Generate the chatbot's response based on the student's input
        bot_response = chatbot_response(student_input)
        
        # Return the chatbot's response in JSON format
        return jsonify({'response': bot_response})
    

# Route for displaying the latest student details
@app.route('/student-details', methods=['GET'])
def student_details():
    # Fetch the latest student details from the database
    student = get_latest_student()
    # Render the details in the student_details.html template
    return render_template('student_details.html', student=student)


# Route for displaying all students and filtering by course
@app.route('/all-students', methods=['GET', 'POST'])
def all_students():
    selected_course = '0'  # Default value for selecting all courses
    if request.method == 'POST':
        # Fetch the selected course ID from the form submission
        course_id = request.form.get('course_id')
        if course_id == '0':
            # If '0' is selected, show all students
            students = get_all_students()
        else:
            # Filter students by the selected course
            selected_course = course_id
            students = get_students_by_course(course_id)
    else:
        # If no course is selected, show all students
        students = get_all_students()
    
    # Render the student list in the all_students.html template
    return render_template('all_students.html', students=students, selected_course=selected_course)


# Route for deleting a student's record based on their ID
@app.route('/delete/<int:student_id>')
def delete(student_id):
    # Delete the student from the database
    delete_student(student_id)
    # Redirect back to the all students page after deletion
    return redirect(url_for('all_students'))


# Run the Flask application when this script is executed directly
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)  # Host the app on all available network interfaces at port 8080
