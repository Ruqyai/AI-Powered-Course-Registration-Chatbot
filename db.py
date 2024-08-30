import sqlite3

def create_student_details_tables():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('student_details.db')

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Create the student_details table if it doesn't already exist
    # This table will store the details of students like name, language, city, etc.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT,
        first_name TEXT,
        last_name TEXT,
        city TEXT,
        email TEXT,
        course INTEGER,
        FOREIGN KEY (course) REFERENCES Courses(course_id))''')

    # Create the Courses table if it doesn't already exist
    # This table will store details of available courses
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Courses (
        course_id INTEGER PRIMARY KEY,
        course_name TEXT NOT NULL,
        course_description TEXT)''')

    # Insert predefined courses into the Courses table if they don't exist
    cursor.execute('''
    INSERT OR IGNORE INTO Courses (course_id, course_name, course_description) VALUES
    (1, 'Python', 'An introductory course on Python programming.'),
    (2, 'Math', 'A comprehensive course on Mathematics.'),
    (3, 'Machine Learning', 'A course on the fundamentals of Machine Learning.')''')

    # Commit the changes and close the connection to the database
    conn.commit()
    conn.close()

def save_student_details(student_details):
    # Connect to the SQLite database
    conn = sqlite3.connect('student_details.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Insert the student's details into the student_details table
    cursor.execute('''
    INSERT INTO student_details (language, first_name, last_name, city, email, course)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_details.language, student_details.first_name, student_details.last_name, student_details.city, student_details.email, int(student_details.course)))

    # Commit the transaction and close the connection to the database
    conn.commit()
    conn.close()

def get_latest_student():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_details.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Query to get the most recent student's details, joined with their course information
    query = '''
    SELECT sd.id, sd.language, sd.first_name, sd.last_name, sd.city, sd.email, c.course_name
    FROM student_details sd
    JOIN Courses c ON sd.course = c.course_id
    ORDER BY sd.id DESC LIMIT 1
    '''
    # Execute the query and fetch the latest student's data
    cursor.execute(query)
    student = cursor.fetchone()

    # Close the connection to the database and return the student data
    conn.close()
    return student

def get_all_students():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_details.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    try:
        # Query to get all student details along with their course information
        query = '''
        SELECT sd.id, sd.language, sd.first_name, sd.last_name, sd.city, sd.email, c.course_name
        FROM student_details sd
        JOIN Courses c ON sd.course = c.course_id
        '''
        cursor.execute(query)
        students = cursor.fetchall()  # Fetch all student data
    except Exception as e:
        print(f"Error fetching students: {e}")
        students = []  # If there is an error, return an empty list
    finally:
        # Close the connection to the database
        conn.close()
    return students

def delete_student(student_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('student_details.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Delete the student with the given ID from the student_details table
    cursor.execute("DELETE FROM student_details WHERE id = ?", (student_id,))

    # Commit the transaction and close the connection to the database
    conn.commit()
    conn.close()

# Function to save course details to the Courses table
def save_course_details(course_details):
    # Connect to the SQLite database
    conn = sqlite3.connect('student_details.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Insert the new course details into the Courses table
    cursor.execute('''
    INSERT INTO Courses (course_id, course_name, course_description)
    VALUES (?, ?, ?)
    ''', (course_details['course_id'], course_details['course_name'], course_details['course_description']))

    # Commit the transaction and close the connection to the database
    conn.commit()
    conn.close()

# Function to retrieve all courses from the Courses table
def get_all_courses():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_details.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    try:
        # Query to retrieve all courses from the Courses table
        cursor.execute("SELECT * FROM Courses")
        courses = cursor.fetchall()  # Fetch all course data
    except Exception as e:
        print(f"Error fetching courses: {e}")
        courses = []  # If there is an error, return an empty list
    finally:
        # Close the connection to the database
        conn.close()
    return courses

# Function to retrieve students by a specific course ID
def get_students_by_course(course_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('student_details.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    try:
        # Query to get students based on the selected course ID
        query = '''
        SELECT sd.id, sd.language, sd.first_name, sd.last_name, sd.city, sd.email, c.course_name
        FROM student_details sd
        JOIN Courses c ON sd.course = c.course_id
        WHERE sd.course = ?
        '''
        cursor.execute(query, (course_id,))
        students = cursor.fetchall()  # Fetch the students who are enrolled in the specified course
    except Exception as e:
        print(f"Error fetching students for course {course_id}: {e}")
        students = []  # If there is an error, return an empty list
    finally:
        # Close the connection to the database
        conn.close()
    return students
