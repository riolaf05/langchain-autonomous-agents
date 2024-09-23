import base64
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import TransformChain
from langchain_core.runnables import chain
from utils.rabbitmq import RabbitMQClient
import logging
from dotenv import load_dotenv
load_dotenv(override=True)
import os

QUEUE_NAME=os.getenv('RABBITMQ_QUEUE_NAME')
RABBITMQ_URL=os.getenv('RABBITMQ_URL')
image_path = '/tmp/TRUPPE-CAMMELLATE.jpg' #FIXME

logger = logging.getLogger(__name__)
rabbit_client=RabbitMQClient(
    host=RABBITMQ_URL
)
rabbit_client.declare_queue(QUEUE_NAME)
prompt = f"""
   Data l'immagine ricevuta, descrivila nei dettagli . 
"""

def load_image(inputs: dict) -> dict:
    """Load image from file and encode it as base64."""
    image_path = inputs["image_path"]
  
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    image_base64 = encode_image(image_path)
    return {"image": image_base64}


@chain
def image_model(inputs: dict) -> str | list[str] | dict:
 """Invoke model with image and prompt."""
 model = ChatOpenAI(temperature=0.1, model="gpt-4o", max_tokens=1024)
 msg = model.invoke(
             [HumanMessage(
                content=[
                {"type": "text", "text": inputs["prompt"]},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{inputs['image']}"}},
             ])]
             )
 return msg.content

load_image_chain = TransformChain(
    input_variables=["image_path"],
    output_variables=["image"],
    transform=load_image
)

def get_image_informations(vision_prompt, image_path: str) -> dict:
   vision_chain = load_image_chain | image_model
   return vision_chain.invoke({'image_path': f'{image_path}', 
                               'prompt': vision_prompt})

result = get_image_informations(prompt, image_path)
rabbit_client.send_message('', QUEUE_NAME, {'story': result})