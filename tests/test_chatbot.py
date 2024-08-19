import unittest
from chatbot import extract_student_details, merge_student_details, find_missing_details, chatbot_response
from chatbot import studentDetails

class TestChatbot(unittest.TestCase):
    def setUp(self):
        """Set up any necessary initial conditions for the tests."""
        # You can initialize the base student details here
        self.base_student_details = studentDetails(
            language=None,
            first_name=None,
            last_name=None,
            city=None,
            email=None,
            course=None
        )

    def test_extract_student_details(self):
        """Test the extraction of student details from a sample input text."""
        input_text = "My name is John Doe, I live in New York, and my email is john@example.com. I want to register for the Python course."
        details = extract_student_details(input_text)
        self.assertEqual(details['first_name'], "John")
        self.assertEqual(details['last_name'], "Doe")
        self.assertEqual(details['city'], "New York")
        self.assertEqual(details['email'], "john@example.com")
        self.assertEqual(details['course'], "1")  # Assuming "Python" corresponds to course "1"

    def test_merge_student_details(self):
        """Test merging new details with the existing student details."""
        new_details = {
            "first_name": "Jane",
            "last_name": "Doe",
            "city": "Los Angeles",
            "email": "jane@example.com",
            "course": "2"
        }

        updated_student_details = merge_student_details(self.base_student_details, new_details)
        self.assertEqual(updated_student_details.first_name, "Jane")
        self.assertEqual(updated_student_details.city, "Los Angeles")
        self.assertEqual(updated_student_details.email, "jane@example.com")
        self.assertEqual(updated_student_details.course, "2")

    def test_find_missing_details(self):
        """Test identifying missing fields in the student details."""
        incomplete_student_details = studentDetails(
            first_name="John",
            city="New York"
        )
        missing_fields = find_missing_details(incomplete_student_details)
        self.assertIn("last_name", missing_fields)
        self.assertIn("email", missing_fields)
        self.assertIn("course", missing_fields)

    def test_chatbot_response_complete(self):
        """Test chatbot response when all details are provided."""
        input_text = "My name is John Doe, I live in New York, and my email is john@example.com. I want to register for the Python course."
        response = chatbot_response(input_text)
        self.assertIn("Thank you", "Thank you")  
    def test_chatbot_response_missing_fields(self):
        """Test chatbot response when details are missing."""
        input_text = "My name is John, I live in New York."
        response = chatbot_response(input_text)
        self.assertIn("email", "email")  
        self.assertIn("course", "course")  

if __name__ == '__main__':
    unittest.main()
