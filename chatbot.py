# Import necessary libraries
import os
import random
import sqlite3
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from db import save_student_details
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the Google API key environment variable
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Initialize Gemini 1.5 Pro for chatbot functionality
# Optional: gemini-1.5-flash or gemini-1.5-pro
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)  

# Data model to represent student details
class studentDetails(BaseModel):
    language: Optional[str] = Field(
        None, enum=["Arabic", "English"],
        description="The preferred language of the student."
    )
    first_name: Optional[str] = Field(
        None,
        description="The student's first name."
    )
    last_name: Optional[str] = Field(
        None,
        description="The student's last name or surname."
    )
    city: Optional[str] = Field(
        None,
        description="The city where the student resides."
    )
    email: Optional[str] = Field(
        None,
        description="The student's email address."
    )
    course: Optional[str] = Field(
        None, enum=["1", "2", "3"],
        description="The course selected by the student: '1' for Python, '2' for Math, '3' for Machine Learning."
    )

# Function to connect to the SQLite database
def connect_db():
    return sqlite3.connect('student_details.db')

# Function to extract student details from the input text using a language model
def extract_student_details(input_text: str) -> studentDetails:
    # Use a parser to parse the details from text into the studentDetails model
    parser = JsonOutputParser(pydantic_object=studentDetails)

    # Create a prompt to instruct the model to extract details from the input text
    extraction_prompt = PromptTemplate(
        template="""Extract the following personal details from the text and provide them:
        {input}   \n \n {format_instructions}""",
        input_variables=["input"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Chain the prompt and language model together for processing the input
    chain = extraction_prompt | llm | parser
    return chain.invoke(input_text)

# Function to merge new details with existing student details
def merge_student_details(current_details: studentDetails, new_details: dict) -> studentDetails:
    print("Data received:", new_details)
    try:
        # Extract the personal details from the provided dictionary
        personal_details = new_details
    except KeyError as e:
        print(f"KeyError: {e}. The key 'personaldetails' is not in the data dictionary.")
        personal_details = {}

    # Update only fields that are currently empty in the student details
    updated_details = {
        'language': personal_details.get('language', current_details.language) if not current_details.language else current_details.language,
        'first_name': personal_details.get('first_name', current_details.first_name) if not current_details.first_name else current_details.first_name,
        'last_name': personal_details.get('last_name', current_details.last_name) if not current_details.last_name else current_details.last_name,
        'city': personal_details.get('city', current_details.city) if not current_details.city else current_details.city,
        'email': personal_details.get('email', current_details.email) if not current_details.email else current_details.email,
        'course': personal_details.get('course', current_details.course) if not current_details.course else current_details.course
    }

    # Return an updated studentDetails object with the merged information
    return studentDetails(
        language=updated_details.get('language'),
        first_name=updated_details.get('first_name'),
        last_name=updated_details.get('last_name'),
        city=updated_details.get('city'),
        email=updated_details.get('email'),
        course=updated_details.get('course')
    )

# Function to identify missing details in the studentDetails object
def find_missing_details(student_details: studentDetails) -> List[str]:
    empty_fields = []
    # Iterate over the fields of the studentDetails object and check for empty values
    for field in vars(student_details):
        value = getattr(student_details, field)
        if value in [None, "", 0]:
            print(f"Field '{field}' is empty.")
            empty_fields.append(field)
    return empty_fields

# Function to prompt the student for missing information based on the missing fields
def prompt_for_missing_info(missing_fields: List[str], student_input: str) -> str:
    # Create a system prompt template to engage with the student and collect missing data
    system_prompt = """You are a chatbot that collects student data that is needed for registration. You talk to the student in a friendly way.
    Interact with student message:
    {student_input}
    If the user writes in Arabic, you must reply in Arabic. If the user writes in English, you must reply in English.
    Here are some things to ask the student for in a conversational way:
    ### Missing fields list: {missing_fields}

    Only ask one question at a time, even if you don't get all the info.
    If there are four items in the list, say hello.
    If there are less than four items and the list is not empty, make the conversation seem continuous.
    If the list is empty, thank the student, tell them you've collected their registration data, and say goodbye.
    """
    # Create the prompt using the template
    prompt = PromptTemplate(template=system_prompt, input_variables=['missing_fields', "student_input"])

    # Chain the prompt and language model to generate a conversational response
    chain = prompt | llm
    ai_response = chain.invoke({"missing_fields": missing_fields, "student_input": student_input})
    return ai_response.content

# Initialize an empty studentDetails object to store data across conversations
current_student_details = studentDetails()

# The main chatbot function that processes user input and manages the conversation flow
def chatbot_response(text_input: str) -> str:
    global current_student_details

    # Extract details from the student's input text
    extracted_details = extract_student_details(text_input)

    # Merge the extracted details with the current stored details
    current_student_details = merge_student_details(current_student_details, extracted_details)

    # Identify any missing fields in the student's information
    missing_fields = find_missing_details(current_student_details)

    # If no missing fields, save the student's details and thank them for registering
    if not missing_fields:
        save_student_details(current_student_details)
        messages = [
            "Thank you, I've collected your data that we need for registration. See you soon!",
            "Thanks! Your information has been recorded. Have a great day!",
            "Data saved! You're all set. See you next time!",
            "All done! Your registration is complete. See you soon!",
            "Got it! Your data is safe with us. See you next time!"
        ]
        thanks_message = random.choice(messages)
        current_student_details = studentDetails()  # Reset the details for the next interaction
        return f"{thanks_message} [redirect]"

    # Otherwise, prompt the student for any missing information
    return prompt_for_missing_info(missing_fields, text_input)
