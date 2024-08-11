import requests
import os
from dotenv import load_dotenv
from bson import ObjectId
import PyPDF2
import io

load_dotenv()

API_URL = os.getenv("HUGGING_FACE_API_URI")
API_KEY = os.getenv("HUGGING_FACE_API_KEY")

headers = {"Authorization": f"Bearer {API_KEY}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
def AI_Result(message):
    output = query({ "inputs": message, })
    return output

def AI_summarizer(fs,course_data):
    pdf_file = fs.get(course_data['file_id']).read()
    
    pdf_file_io = io.BytesIO(pdf_file)
    reader = PyPDF2.PdfReader(pdf_file_io)
    text = ""
    pdf_result = ""
    index = 0 

    for page in reader.pages: 
        text = page.extract_text()

        if (len(text) > 0) :
            temp_result = AI_Result(text)
            if (len(temp_result) > 0) : pdf_result += temp_result[0]['summary_text']

    return pdf_result
