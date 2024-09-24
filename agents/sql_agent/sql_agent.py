from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import sqlite3
load_dotenv(override=True)
from utils.rabbitmq import RabbitMQClient
import logging
from dotenv import load_dotenv
load_dotenv(override=True)
import os

logger = logging.getLogger(__name__)

QUEUE_NAME=os.getenv('RABBITMQ_QUEUE_NAME')
RABBITMQ_URL=os.getenv('RABBITMQ_URL')
GROQ_API_KEY=os.getenv('GROQ_API_KEY')

conn = sqlite3.connect('example.db')
# llm = ChatGroq(model_name="llama3-70b-8192", groq_api_key=GROQ_API_KEY, temperature=0)
model = ChatOpenAI(temperature=0)

# Define your desired data structure.
class Observation(BaseModel):
    title: str = Field(description="the title of the observation")
    description: str = Field(description="the detailed description of the observation")

# Set up a parser + inject instructions into the prompt template.
parser = JsonOutputParser(pydantic_object=Observation)

prompt = PromptTemplate(
    template="Rispondi alla domanda.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
chain = prompt | model | parser

rabbit_client=RabbitMQClient(
    host=RABBITMQ_URL
)
rabbit_client.declare_queue(QUEUE_NAME)

def create_tables():
    sql_statements = [ 
        """CREATE TABLE IF NOT EXISTS example_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title text NOT NULL, 
                description TEXT
        );"""
    ]
    try:
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)
            
            conn.commit()
    except sqlite3.Error as e:
        print(e)

def callback(body):
        print(f" [x] Received {body}")
        try:
            create_tables() #FIXME
            data = chain.invoke({"query": body['description']})
            conn.execute("INSERT INTO example_table (title, description) VALUES (?, ?)", 
                (data["title"], data["description"]))
            print('saved!')
        except Exception as e:
            print(e)
            logger.error(e)
            return


rabbit_client.receive_messages(QUEUE_NAME, callback)