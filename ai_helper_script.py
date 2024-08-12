import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
import PyPDF2
import io

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_LLM_KEY")

llm = ChatGoogleGenerativeAI(
    model = "gemini-1.5-flash",
    google_api_key = GOOGLE_API_KEY,
    temperature = 0,
    max_tokens = None,
    timeout = None,
    max_retries = 2,
    safety_settings = { HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, },
)

def AI_summary(fs,course_data) :

    prompt_summary = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "As a professional summarizer, create a concise and comprehensive summary of the provided text, be it an article, post, conversation, or passage, while adhering to these guidelines:Craft a summary that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness. Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects. Rely strictly on the provided text, without including external information. Format the summary in paragraph form for easy understanding.",
            ),
            ("human", "{input}"),
        ]
    )

    pdf_file = fs.get(course_data['file_id']).read()
    
    pdf_file_io = io.BytesIO(pdf_file)
    reader = PyPDF2.PdfReader(pdf_file_io)
    pdf_text = ""

    for page in reader.pages:  pdf_text += page.extract_text()

    chain = prompt_summary | llm
    summarized_text = chain.invoke({"input": pdf_text,})

    return summarized_text.content

def AI_key_points(summary) :
    prompt_key_points = '''
        You will be given a summary with multiple headings and its detailed sentences.
        Return the headings and the sentences in the following Python dictionary format:

        {{
            "headings": [
                "sentence 1",
                "sentence 2",
                ".......",
            ],
            "headings": [
                "sentence 1",
                "sentence 2",
                "sentence 3",
                ".......",
            ],
            ...
            ...
        }}

        % SUMMARY:
        {summary}

        YOUR RESPONSE:
    '''

    prompt = PromptTemplate(
        input_variables=["summary"],
        template=prompt_key_points
    )

    final_prompt = prompt.format(summary=summary)

    chain = prompt | llm
    summarized_text = chain.invoke(final_prompt)
    key_points = eval(summarized_text.content[9:len(summarized_text.content)-3])

    # print(key_points)

    # for i in key_points:
    #     print ( "yo " , i, " check this out : ", type(key_points[i]) , " ------------------\n")
    
    # for i in key_points:
    #     if (len(key_points[i]) < 2) : continue
    #     print(key_points[i])
    #     key_points[i] = key_points[i].split('\n')

    # print(type(key_points))
    # print(type(key_points))

    return key_points