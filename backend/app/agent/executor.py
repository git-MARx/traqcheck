from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from app.agent.prompts import AGENT_SYSTEM_PROMPT
from app.agent.tools import check_existing_requests, create_document_request, get_candidate_profile

load_dotenv()

TOOLS = [get_candidate_profile, check_existing_requests, create_document_request]

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

PROMPT = ChatPromptTemplate.from_messages([
    ("system", AGENT_SYSTEM_PROMPT),
    ("human", "Collect PAN and Aadhaar documents from candidate {candidate_id}."),
    MessagesPlaceholder("agent_scratchpad"),
])

agent          = create_tool_calling_agent(llm, TOOLS, PROMPT)
agent_executor = AgentExecutor(agent=agent, tools=TOOLS, return_intermediate_steps=True)


def run_document_request_agent(candidate_id: str) -> dict:
    result = agent_executor.invoke({"candidate_id": candidate_id})

    for action, output in reversed(result["intermediate_steps"]):
        if action.tool == "create_document_request":
            return {"status": "created", **output}
        if action.tool == "check_existing_requests" and output.get("exists"):
            return {"status": "existing", "message_body": output["message_body"],
                     "upload_link": output["upload_link"], "token_expiry": output["token_expiry"]}

    return {"status": "no_request", "detail": result["output"]}
