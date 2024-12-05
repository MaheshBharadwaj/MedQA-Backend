
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import warnings
from operator import itemgetter
import yaml
import os
import yaml
from langchain import hub
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from src.vector_store_handler import VectorStoreHandler
from operator import itemgetter
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from src.config.constants import COMMON_INSTRUCTIONS, PROMPT_TEMPLATE_NEW, SYSTEM_PROMPT_TEMPLATE_CHAT_HISTORY, SYSTEM_PROMPT_TEMPLATE_NO_RAG_CHAT_HISTORY

class DocumentRetriever:
    def __init__(self, persist_directory):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={'device': 'mps'})
        self.vector_db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

    def retrieve_documents(self, query, top_k=5):
        # Retrieve top_k relevant document chunks based on the query
        return self.vector_db.similarity_search(query, k=top_k)

class RAGChatBot:
    def __init__(self, retriever):
        self.retriever = retriever
        self.chat_model = ChatOpenAI(model_name="gpt-4o", temperature=0)
        # self.prompt_template = hub.pull("rlm/rag-prompt")
        self.prompt_template = PROMPT_TEMPLATE_NEW
        self.prompt_template_for_chat = SYSTEM_PROMPT_TEMPLATE_CHAT_HISTORY
    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def generate_response(self, user_query):
        # Retrieve documents relevant to the user query
        relevant_docs = self.retriever.retrieve_documents(user_query)
        relevant_context = self.format_docs(relevant_docs)
        # for relevant_doc in relevant_docs:
            # print(relevant_doc.metadata['source'])
            # print(relevant_doc.page_content)
        print("Relevant Context (FIRST MESSAGE): ", relevant_context)
        user_query = user_query 
#         instructions = """
#         1. You are a highly knowledgeable and empathetic medical assistant specializing in advising on surgical procedures. Your primary role is to help both doctors and patients decide whether a given surgery is appropriate be conducted as an inpatient or outpatient procedure. You provide detailed explanations to support your recommendations, ensuring that users make informed decisions.
#         2. If a user chats about some topic on medical device, but doesn't ask/chat about inpatient or outpatient surgery, gently ask the user if you should help him regarding the inpatient vs outpatient surgery
#         3. If a user asks questions outside the medical domain, gently remind them that your expertise is focused on healthcare and surgical advice.
#         4. Chat with the user using the given context. If the context is not at all relevant to the question asked. Tell your reasoning behind your answer and let the user know that you are not sure of the answer, due to lack of relevent context on your end to answer the question.
#         5. If you feel that the data provided is insufficient to answer the question, gently ask the user about more information.
#   """
        instructions = COMMON_INSTRUCTIONS
        # Construct the input data for the chain
        input_data = {
            "context": relevant_context,
            "question": user_query,
            "instructions": instructions# Directly use the user query here
            # "GUIDELINES": instructions
        }
        
        # Create a prompt using the template
        formatted_prompt = self.prompt_template.format(**input_data)
        # print(formatted_prompt)
        
        # Generate a response using the LLM with invoke method
        response = self.chat_model.invoke(formatted_prompt)
        
        return response.content

    def generate_response_no_rag(self, question):

        template1 = """1. You are an assistant for medical question-answering tasks.
        2. Read the question with atmost care and keep your answer concise.
        3. You are a highly knowledgeable medical assistant specializing in advising on surgical procedures. Your primary role is to help both doctors and patients decide whether a given surgery is appropriate be conducted as an inpatient or outpatient procedure. You provide detailed explanations to support your recommendations, ensuring that users make informed decisions.
        4. You can save huge costs if you can correctly identify the case of Outpatient Surgery, so please keep this in mind.
        5. If the patients are healthy currently and comorbidities are well controlled or have medical clearence, it is a good sign for Outpatient surgery generally .
        6. If you do not know the answer, Please convey to user that you are not sure or you require more information.
        7. If the question is not in your domain, please remind user about your expertise."""
        system_message_prompt = SystemMessagePromptTemplate.from_template(template1)
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        msg = self.chat_model.invoke(
            chat_prompt.format_prompt(
                text=question,
            ).to_messages()
        )

        return msg.content

    def generate_answer_with_chat_context(self, messages):
        """
        Generates a response with the last few messages and retrieved context using the chat model.

        Args:
            messages (list): List of dictionaries representing the conversation history.

        Returns:
            str: The generated response.
        """
        # Extract the last 4 messages plus the current one
        recent_messages = []
        if len(messages)>5:
            recent_messages = [messages[0]] + [messages[1]]
        recent_messages = recent_messages+ messages[-5:]  # Last 5 messages (4 historical + current)
        # Prepare input for retrieval (use only the content of messages, excluding the current one)
        retrieval_input = "\n".join(
            f"{message['role'].capitalize()}: {message['content']}" for message in recent_messages[:-1]
        )

        # Attempt to retrieve external documents
        try:
            retrieved_docs = self.retriever.retrieve_documents(retrieval_input)
            retrieved_context = self.format_docs(retrieved_docs)
        except Exception as e:
            retrieved_context = "No additional information could be retrieved."
            print(f"Error during document retrieval: {e}")

        # Ensure retrieved context is a valid string
        retrieved_context = str(retrieved_context)
        print("Retrieved Context (Other messages)" + retrieved_context)

        # Add a system message with the retrieved context
        input_data = {
            "context": retrieved_context,
            "instructions": COMMON_INSTRUCTIONS
        }
        system_message_prompt = self.prompt_template_for_chat.format(**input_data)
        system_message = SystemMessage(content= system_message_prompt)
        # system_message = SystemMessage(content="You are a Medical QA chat assistant and you are specialized in making decisions between Inpatient vs Outpatient surgeries.")

        # Convert recent conversation into LangChain message objects
        formatted_recent_messages = []
        for message in recent_messages:
            if message["role"] == "user":
                formatted_recent_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "ai":
                formatted_recent_messages.append(AIMessage(content=message["content"]))
            else:
                raise ValueError(f"Unexpected role: {message['role']}")

        # Combine system message and formatted recent messages
        input_messages = [system_message] + formatted_recent_messages
        #formatted_recent_messages.append(HumanMessage(content="Outpatient Surgery saves a lot of money. So never be conservative until otherwise inpatient surgery is ABSOULETELY necessary."))
        # input_messages =  formatted_recent_messages
        print(formatted_recent_messages)

        # Generate the response using the chat model
        try:
            llm_response = self.chat_model.invoke(input_messages)
        except Exception as e:
            print(f"Error during model generation: {e}")
            raise

        # Parse the response if needed
        parsed_response = StrOutputParser().parse(llm_response)

        return parsed_response.content

    def generate_answer_with_chat_context_no_rag(self, messages):
        """
        Generates a response with the last few messages and retrieved context using the chat model.

        Args:
            messages (list): List of dictionaries representing the conversation history.

        Returns:
            str: The generated response.
        """
        # Extract the last 4 messages plus the current one
        recent_messages = []
        if len(messages)>5:
            recent_messages = [messages[0]] + [messages[1]]
        recent_messages = recent_messages+ messages[-5:]  # Last 5 messages (4 historical + current)
        system_message = SystemMessage(content= SYSTEM_PROMPT_TEMPLATE_NO_RAG_CHAT_HISTORY)
        # system_message = SystemMessage(content="You are a Medical QA chat assistant and you are specialized in making decisions between Inpatient vs Outpatient surgeries.")

        # Convert recent conversation into LangChain message objects
        formatted_recent_messages = []
        for message in recent_messages:
            if message["role"] == "user":
                formatted_recent_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "ai":
                formatted_recent_messages.append(AIMessage(content=message["content"]))
            else:
                raise ValueError(f"Unexpected role: {message['role']}")

        # Combine system message and formatted recent messages
        input_messages = [system_message] + formatted_recent_messages
        #formatted_recent_messages.append(HumanMessage(content="Outpatient Surgery saves a lot of money. So never be conservative until otherwise inpatient surgery is ABSOULETELY necessary."))
        # input_messages =  formatted_recent_messages
        print(formatted_recent_messages)

        # Generate the response using the chat model
        try:
            llm_response = self.chat_model.invoke(input_messages)
        except Exception as e:
            print(f"Error during model generation: {e}")
            raise

        # Parse the response if needed
        parsed_response = StrOutputParser().parse(llm_response)

        return parsed_response.content