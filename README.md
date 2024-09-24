# Autonomous Agents Powered by LLMs and LangChain

## Project Overview

This project focuses on building a system of autonomous agents powered by Large Language Models (LLMs) and LangChain. Each agent is designed to complete specific tasks using various tools, and the agents are decoupled from each other. The architecture follows an event-driven design, allowing agents to communicate and react to events asynchronously.

### Key Features

- Autonomous Agents: Each agent is responsible for performing a dedicated task independently.
- Tool Integration: Agents are equipped to use different tools to fulfill their assigned tasks.
- Decoupled Architecture: The agents operate independently and are not tightly coupled to each other.
- Event-Driven System: The system is driven by events, enabling agents to react and process inputs asynchronously.

## Current Agents

### 1. GPT Image Processing Agent (`gpto_agent`)

- Description: This agent is responsible for interpreting images. It receives an image via a Flask API, processes it, and sends the resulting description to RabbitMQ for further use.
- How to invoke: 
  - Use the following Postman link to invoke this agent:  
    [Postman Request Link](https://weaving360.postman.co/workspace/weaving360~d5f2e462-78e1-41d0-9d6e-973d013d307d/request/25830852-dec4fda0-302f-40a7-bed1-f5d82dd9e744?tab=body)
  - Send the image data in the body of the request.
  
### 2. SQL Structuring Agent (`sql_agent`)

- Description: This agent is designed to handle unstructured input. It receives the input, processes it into a structured format, and saves it to an SQLite database.
  
## Architecture

The system uses an event-driven architecture, meaning that agents do not work in isolation but communicate through events. For example, one agent might trigger another agent's execution by sending a message through RabbitMQ. This decoupling allows for flexible and scalable workflows where each agent can be developed and scaled independently.

## Setup

To set up the system using Docker and Docker Compose, follow the steps below:

1. Clone the repository
2. Setup with Docker compose
```console
sudo docker-compose up -d
```