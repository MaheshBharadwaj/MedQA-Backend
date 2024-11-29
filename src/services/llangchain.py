
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
        print(f"API KEY: {os.environ.get('OPENAI_API_KEY')}")
        self.chat_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)
        self.prompt_template = hub.pull("rlm/rag-prompt")

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def generate_response(self, user_query):
        # Retrieve documents relevant to the user query
        relevant_docs = self.retriever.retrieve_documents(user_query)
        relevant_context = self.format_docs(relevant_docs)
        # for relevant_doc in relevant_docs:
            # print(relevant_doc.metadata['source'])
            # print(relevant_doc.page_content)

#         instructions = """
#         1. You are a highly knowledgeable and empathetic medical assistant specializing in advising on surgical procedures. Your primary role is to help both doctors and patients decide whether a given surgery is appropriate be conducted as an inpatient or outpatient procedure. You provide detailed explanations to support your recommendations, ensuring that users make informed decisions.
#         2. If a user chats about some topic on medical device, but doesn't ask/chat about inpatient or outpatient surgery, gently ask the user if you should help him regarding the inpatient vs outpatient surgery
#         3. If a user asks questions outside the medical domain, gently remind them that your expertise is focused on healthcare and surgical advice.
#         4. Chat with the user using the given context. If the context is not at all relevant to the question asked. Tell your reasoning behind your answer and let the user know that you are not sure of the answer, due to lack of relevent context on your end to answer the question.
#         5. If you feel that the data provided is insufficient to answer the question, gently ask the user about more information.
#   """
        instructions = """1. You are a highly knowledgeable medical assistant specializing in advising on surgical procedures. Your primary role is to help both doctors and patients decide whether a given surgery is appropriate be conducted as an inpatient or outpatient procedure,based on the context you have. You provide detailed explanations to support your recommendations, ensuring that users make informed decisions.
        2. You can save huge costs if you can correctly identify the case of Outpatient Surgery, so need not be conservative if you are confident, with the context you have"""

        input_data = {
            "context": relevant_context,
            "question": user_query,  # Directly use the user query here
            "GUIDELINES": instructions
        }
        
        formatted_prompt = self.prompt_template.format(**input_data)
        
        response = self.chat_model.invoke(formatted_prompt)
        
        return response.content

    def generate_response_no_rag(self, question):
        template = """You are a highly knowledgeable and empathetic medical assistant specializing in advising on surgical procedures. Your primary role is to help both doctors and patients decide whether a given surgery is appropriate be conducted as an inpatient or outpatient procedure. You provide detailed explanations to support your recommendations, ensuring that users make informed decisions.

            Guidelines:
            1. **Focus on Medical Context:** Always center your responses around medical topics, particularly those related to surgical procedures and patient care settings.
            2. **Inquire When Necessary:** If you require more information to make an informed decision, politely ask the user specific questions about the surgery details, such as the type of surgery, patient health status, or any existing medical conditions.
            3. **Educational Approach:** Explain your suggestions clearly, using simple language that both healthcare professionals and patients can understand. Provide insights into the benefits and considerations of each option.
            4. **Boundary Setting:** If a user asks questions outside the medical domain, gently remind them that your expertise is focused on healthcare and surgical advice.

            Example Interaction:
            - **User Query:** "I need to know if my knee surgery should be inpatient or outpatient."
            - **Response:** "Knee surgeries can often be performed as outpatient procedures if the patient is in good health and the surgery is minimally invasive. However, if there are underlying health concerns or if a more complex procedure is needed, an inpatient setting might be safer. Could you provide more details about your specific situation?"

            By adhering to these guidelines, you ensure that every interaction is informative, supportive, and within the scope of medical advisement.
        """
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
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
        recent_messages = messages[-5:]  # Last 5 messages (4 historical + current)

        retrieval_input = "\n".join(
            f"{message['role'].capitalize()}: {message['content']}" for message in recent_messages[:-1]
        )

        try:
            retrieved_docs = self.retriever.retrieve_documents(retrieval_input)
            retrieved_context = self.format_docs(retrieved_docs)
        except Exception as e:
            retrieved_context = "No additional information could be retrieved."
            print(f"Error during document retrieval: {e}")

        retrieved_context = str(retrieved_context)

        system_message_prompt = """1. You are a highly knowledgeable medical chat assistant specializing in advising on surgical procedures. Your primary role is to help both doctors and patients decide whether a given surgery is appropriate be conducted as an inpatient or outpatient procedure,based on the context you have. You provide detailed explanations to support your recommendations, ensuring that users make informed decisions.
        2. You can save HUGE costs if you can correctly identify the case of Outpatient Surgery, so need not be conservative if you are confident, with the context you have.
        3. If the question/chat is outside the medical domain, gently remind your expertise."""
        system_message = SystemMessage(content= system_message_prompt + f"\n **RELEVANT INFORMATION RETREIVED**:\n{retrieved_context}")

        formatted_recent_messages = []
        for message in recent_messages:
            if message["role"] == "user":
                formatted_recent_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "ai":
                formatted_recent_messages.append(AIMessage(content=message["content"]))
            else:
                raise ValueError(f"Unexpected role: {message['role']}")

        input_messages = [system_message] + formatted_recent_messages
        try:
            llm_response = self.chat_model.invoke(input_messages)
        except Exception as e:
            print(f"Error during model generation: {e}")
            raise

        parsed_response = StrOutputParser().parse(llm_response)

        return parsed_response.content