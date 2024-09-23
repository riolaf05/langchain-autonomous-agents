from langchain_openai import OpenAI
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
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
db = SQLDatabase.from_uri("sqlite:///test.db")

# Initialize ChatGroq model for language understanding
llm = ChatGroq(model_name="llama3-70b-8192", groq_api_key=GROQ_API_KEY, temperature=0)

# Create ReAct agent
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=db, llm=llm),
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

rabbit_client=RabbitMQClient(
    host=RABBITMQ_URL
)
rabbit_client.declare_queue(QUEUE_NAME)

def callback(body):
        print(f" [x] Received {body}")
        try:
            response = agent_executor.run({"input": body['story']})
            rabbit_client.send_message('', QUEUE_NAME, {'story': response})
            print('saved!')
        except Exception as e:
            print(e)
            logger.error(e)
            return


rabbit_client.receive_messages(QUEUE_NAME, callback)