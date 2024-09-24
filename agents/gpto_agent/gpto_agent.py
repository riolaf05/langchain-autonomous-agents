import base64
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import TransformChain
from langchain_core.runnables import chain
from utils.rabbitmq import RabbitMQClient
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import logging
from dotenv import load_dotenv
load_dotenv(override=True)
import os

QUEUE_NAME=os.getenv('RABBITMQ_QUEUE_NAME')
RABBITMQ_URL=os.getenv('RABBITMQ_URL')
UPLOAD_FOLDER = '/tmp/upload'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

logger = logging.getLogger(__name__)
rabbit_client=RabbitMQClient(
    host=RABBITMQ_URL
)
rabbit_client.declare_queue(QUEUE_NAME)
prompt = f"""
   Data l'immagine ricevuta, descrivila nei dettagli . 
"""
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.savefile_path
            flash('File successfully uploaded')
            result = get_image_informations(prompt, file_path)
            flash(result)
            rabbit_client.send_message('', QUEUE_NAME, {'story': result})
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
