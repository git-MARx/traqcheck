from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.extraction.prompts import EXTRACTION_SYSTEM_PROMPT
from app.extraction.schemas import ResumeExtraction

load_dotenv()

PROMPT = ChatPromptTemplate.from_messages([
    ("system", EXTRACTION_SYSTEM_PROMPT),
    ("human", "Resume (Markdown):\n\n{resume_text}"),
])

llm            = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
structured_llm = llm.with_structured_output(ResumeExtraction)
chain          = PROMPT | structured_llm


def extract_with_groq(resume_text: str) -> ResumeExtraction:
    return chain.invoke({"resume_text": resume_text})


if __name__ == "__main__":
    sample_resume = """
    # Jane Doe
    Email: jane.doe@example.com | Phone: +91 9876543210

    ## Experience
    Senior Software Engineer, Acme Corp (2021-Present)

    ## Skills
    Python, Flask, SQL, React, AWS
    """

    result = extract_with_groq(sample_resume)
    print(result.model_dump_json(indent=2))
