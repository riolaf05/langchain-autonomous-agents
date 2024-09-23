from langchain_openai import OpenAI
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from tools.tavily import web_search_tool 
from tools.utils import get_today_date_tool
from utils.rabbitmq import RabbitMQClient
import logging
from dotenv import load_dotenv
load_dotenv(override=True)
import os

logger = logging.getLogger(__name__)

QUEUE_NAME=os.getenv('RABBITMQ_QUEUE_NAME')
RABBITMQ_URL=os.getenv('RABBITMQ_URL')
GROQ_API_KEY=os.getenv('GROQ_API_KEY')

prompt_react = hub.pull("hwchase17/react")
tools = [get_today_date_tool, web_search_tool]

# Initialize ChatGroq model for language understanding
model = ChatGroq(model_name="llama3-70b-8192", groq_api_key=GROQ_API_KEY, temperature=0)

# Create ReAct agent
react_agent = create_react_agent(model, tools=tools, prompt=prompt_react)
react_agent_executor = AgentExecutor(
    agent=react_agent, tools=tools, verbose=True, handle_parsing_errors=True
)


rabbit_client=RabbitMQClient(
    host=RABBITMQ_URL
)
rabbit_client.declare_queue(QUEUE_NAME)

def callback(body):
        print(f" [x] Received {body}")
        try:
            response = react_agent_executor.invoke({"input": body['story']})
            rabbit_client.send_message('', QUEUE_NAME, {'story': response})
            print('saved!')
        except Exception as e:
            print(e)
            logger.error(e)
            return


rabbit_client.receive_messages(QUEUE_NAME, callback)