import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_LLM_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE},
)

response_schemas = [
    ResponseSchema(name="heading", description="The heading of a section in the summary"),
    ResponseSchema(name="sentence", description="A sentence or detail under the heading")
]


# Define the prompt template
template = '''
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
    template=template
)

# Example summary
test = '''
## Decision Trees: A Comprehensive Summary

Decision trees are a powerful machine learning technique for approximating discrete-valued target functions. Their key strengths lie in their interpretability, represented as easily understandable if-then rules, and their ability to handle various data complexities.

**Key Features:**

* **Interpretability:** Decision trees are highly interpretable, making them ideal for understanding the decision-making process.
* **Data Handling:** They excel in handling attribute-value pairs, discrete target functions, disjunctive descriptions, noisy data, and missing attribute values.
* **Types:** Different types of decision trees exist, including ID3, C4.5, and CART, each with unique strengths and weaknesses.
* **Construction:** Decision tree construction is an inductive learning process that is greedy, top-down, and recursive. It involves partitioning data based on attributes that minimize a chosen loss function, often misclassification loss.
* **Information Gain:** Entropy, a measure of homogeneity, is used to calculate information gain, which quantifies the reduction in uncertainty about the target value when an attribute is known.
* **Inductive Bias:** Decision trees exhibit an inductive bias favoring shorter trees, reflecting a preference for simplicity and generalizability. They prioritize attributes with high information gain, placing them closer to the root for efficient and accurate classifications.

**Specific Algorithms:**

* **ID3:** Focuses on categorical features, maximizing information gain for categorical targets.
* **C4.5:** Extends ID3 to handle both categorical and numerical features by dynamically creating discrete intervals from continuous attributes.
* **CART:** Similar to C4.5 but supports numerical target variables for regression and does not generate rule sets.

In summary, decision trees offer a powerful and interpretable approach to machine learning, particularly well-suited for handling complex data and providing clear insights into the decision-making process.
'''

promptValue = prompt.format(summary=test)

llm_output = llm.invoke(promptValue)
text = llm_output.content[9:len(llm_output.content)-3]

