from langchain_community.vectorstores import Pinecone
from pinecone import Pinecone, ServerlessSpec
from tqdm.notebook import tqdm
# import streamlit as st
import langchain
import openai
from openai import OpenAI
import string

class ObnoxiousAgent:
    def __init__(self, client) -> None:
        # TODO: Initialize the client and prompt for the Obnoxious_Agent
        self.client = client
        self.set_prompt()

    def set_prompt(self, prompt=None):
        # TODO: Set the prompt for the Obnoxious_Agent
        if prompt:
            self.prompt = prompt
        else:
            self.prompt = """You are an AI assistant with the domain knowledge of Machine Learning.
                            Keeping this in mind, You have to determine whether the input given to you
                            is obnoxious or not. Respond with "yes" if the prompt is obnoxious and
                            out of scope, otherwise return "no". \n
                            Here is your input : """

    def extract_action(self, response) -> bool:
        # TODO: Extract the action from the response
        if "yes" in response:
          return True
        else:
          return False

    def check_query(self, query):
        # TODO: Check if the query is obnoxious or not
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": self.prompt + query}]
        )
        return self.extract_action(response.choices[0].message.content)

class QueryAgent:
    def __init__(self, pinecone_index, openai_client, embeddings=None) -> None:
        # TODO: Initialize the Query_Agent agent
        self.openai_client = openai_client
        self.pinecone_index = pinecone_index
        self.embeddings = embeddings
        self.top_k = 5
        #self.set_prompt()

    def query_vector_store(self, query, nameSpace='ns001', k=5):
        self.top_k = k

        # TODO: Query the Pinecone vector store
        query_embedding = self.get_embedding(query)
        response = self.pinecone_index.query(namespace=nameSpace,  # change namespace to compare results based on chunk sizes
                                        vector=query_embedding,
                                        top_k=self.top_k,
                                        include_values=True,
                                        include_metadata=True
                                        )
        return response

    def extract_action(self, queries = None):
        # TODO: Extract the action from the response
        # Extracting the text/chunks data
        query = queries[-1]
        print(queries)
        extracted_text = []
        extracted_vecs = []
        response = self.check_if_general_query(query)
        response = response.choices[0].message.content
        if response == "No":
            response = self.check_if_followup_query(query, queries)
            if response == "No":
                response = self.query_vector_store(query)
                for match in response['matches'][:self.top_k]:
                    extracted_text.append(match['metadata']['text'])
                    extracted_vecs.append([match['id'],match['score'],match['metadata']['genre']]) 
                response = "No"
            else:
                response = self.query_vector_store('\n'.join(queries[:][1]))
                for match in response['matches'][:self.top_k]:
                    extracted_text.append(match['metadata']['text'])
                    extracted_vecs.append([match['id'],match['score'],match['metadata']['genre']]) 
                response = "No"
        else:
            prompt = f""" 
                        Respond to the query:\n {query} \n in a chatty way.
                        """

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            response = response.choices[0].message.content
        return (response, extracted_text,extracted_vecs) # best result text

    def check_if_general_query(self, query = None):
        prompt = f""" Check if {query} is a general greeting (such as "Hi", "How are you?", "how are you doing?" or similar). 
                        IF YES, then you should return ONLY ONE WORD "Yes".\n
                        You have to respond to the query:\n {query} \n carefully assess if the query is a general greeting. 
                        IF NOT a general conversational greeting, return ONLY ONE WORD "No"
                        """

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        return response

    def check_if_followup_query(self, query=None, queries = None):
        prompt = f""" Is {query} is a follow up query to the previous queries {queries}. 
                        Examples of follow up query: "tell me more", "explain in detail" etc;
                        Follow up queries can contain prepositions.
                        carefully assess if the query {query} is a follow up query. 
                        IF it is a follow up query, return ONLY ONE WORD "Yes"
                        IF NOT a follow up query, return ONLY ONE WORD "No"
                        """

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        print("is_followup: ", response.choices[0].message.content)

        return response


    def get_embedding(self, text, model="text-embedding-ada-002"):
        print(text[1])
        text = text[1].replace("\n", " ")
        return self.openai_client.embeddings.create(input = [text], model=model).data[0].embedding

class AnsweringAgent:
    def __init__(self, openai_client) -> None:
        # TODO: Initialize the Answering_Agent
        self.openai_client = openai_client

    def generate_response(self, query, docs, conv_history, k=5,mode = "Simple"):
        # TODO: Generate a response to the user's query
        
        if mode == "Detailed":
            mode_prompt = f"Make the answer detailed and comprehensive. \n"
        elif mode == "Chatty":
            mode_prompt = f"Make the answer chatty and engaging. \n"
        else:
            mode_prompt = "Make the answer simple and to the point. \n"
            
            
        if docs:    # if he has found relevant documents
            prompt = f""" You are an AI chatbot helping users to get an answer to informational questions.
                        your task if to help the users with answers.
                        
                        ONLY Based on the text provided in this prompt You have to respond to the query:\n {query} \n
                        Answer the query based ONLY on the following documents: \n{docs}\n
                        DO NOT USE any content not provided in the prompt. frame your answer from the documents provided in this prompt.
                        ONLY If the query is a followup question from the previous conversation, 
                        Take into consideration the previous conversions : \n{conv_history[-k:]}\n 
                        Understand the query, the provided information and the conversation history before answering.\n
                        you should be able to answer the query. 
                        DO NOT Answer if the query is outside the context of the provided documents and the conversation history.

                        Think step-by-step.\n
                        
                    """
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt+mode_prompt}]
            )
            response = response.choices[0].message.content   
        else:
            response = f""" You are an AI chatbot. you should only respond to general greetings
                         (such as "Hi", "How are you?", "how are you doing?" or similar).\n
                        
                        You have to respond to the query:\n {query} \n
                        carefully assess if the query is a general greeting. if it is not a general 
                        conversational greeting, 
                        respond "No Relevant Documents found. Please ask a relevant question"
                        here is 

                        """

        # check_resp_prompt = f"""Your friend, an AI chatbot, is asked the following question: {query} \n
        #                         and he provided this answer: {response.choices[0].message.content} \n
        #                         if the response is the right answer to the question, return the answer
        #                         {response.choices[0].message.content}. \n
        #                         if you feel the answer is not appropirate to the question, then
        #                           TODO
        #                     """

        return response

class RelevantDocumentsAgent:
    def __init__(self, openai_client) -> None:
        # TODO: Initialize the Relevant_Documents_Agent
        self.rel_docs_list = ['machine-learning.pdf']   # relevant documents list
        self.openai_client = openai_client

    def get_relevance(self, conversation, extracted_texts, vecs) ->str:
        # TODO: Get if the returned documents are relevant
        # print(conversation[-1]  )
        # print(conversation[-3:])
        prompt = f""" Check if the query: {conversation[-1]} belongs to {vecs[-1][2]} genre. If Yes respond "yes" or else respond as "None".
                        If the query is a follow up question like "tell me more", "explain in detail" etc; also Take the conversation history 
                        {conversation[-3:]} into consideration and return "yes" if the conversation history belongs to {vecs[-1][2]} genre.
                        If No then respond as "None"\n 
                """
                #     ONLY use the document from the documents list: {extracted_texts} and try to answers the 
                #      user "{conversation[-1]}". The Answer MUST be directly present in the documents 
                #      and MUST be a topic related to "{conversation[-1]}". DO NOT USE anything other Than the documents list provided 
                #      to answer the question"\n
                #      return ONLY the index number of the document from the document list ONLY IF that document contains relevant information.\n
                #      If the query is a follow up question like "tell me more", "explain in detail" etc; also Take the conversation history 
                #      {conversation[-3:]} into consideration and return the document index from the document list that contains the relevant information.\n
                #      if there NO document is relevant document to the query, return 1 WORD "None" .
                #  """
                 
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

class HeadAgent:
    def __init__(self, openai_key, pinecone_key, pinecone_index_name, messages) -> None:
        
        print("Initializing the Head_Agent")
        # TODO: Initialize the Head_Agent
        self.openai_key = openai_key
        self.pinecone_key = pinecone_key
        self.pinecone_index_name = pinecone_index_name

        # Set OpenAI client
        self.client = OpenAI(api_key=self.openai_key)

        # Set Obnoxious Agent
        self.obnox_ag = ObnoxiousAgent(self.client)

        # Set Relevant Documents Agent
        self.rel_doc_ag = RelevantDocumentsAgent(self.client)

        # Implement the Pinecone Query
        # Set Pinecone key and index
        pc = Pinecone(api_key=pinecone_key)
        pinecone_index = pc.Index(pinecone_index_name)

        # Generate query Embeddings
        # Set Pinecone Query Agent
        self.query_ag = QueryAgent(pinecone_index, self.client, None)

        # Document name to NameSpace dict
        # TODO

        # Set Answering Agent
        self.answer_ag = AnsweringAgent(self.client)

        self.messages = messages

        self.openai_model = 'gpt-3.5-turbo'

    def setup_sub_agents(self):
        # TODO: Setup the sub-agents
        self.mode = "Chatty"

    def process_input(self, user_input):
        
        # print("Running the main loop")
        # TODO: Run the main loop for the chatbot
        # st.title("Mini Project 2: Streamlit Chatbot")

        # Check for existing session state variables
        # if "openai_model" not in st.session_state:
        #     # ... (initialize model)
        # openai_model = getattr(st.session_state, 'openai_model', 'gpt-3.5-turbo')

        # if "messages" not in st.session_state:
        #     # ... (initialize messages)
        # messages = getattr(st.session_state, 'messages', [])
        # conversation = []
        # Display existing chat messages
        # ... (code for displaying messages)
        '''
        for role, message in messages:
            if role == "user":
                with st.chat_message("user"):
                    st.write(message)
            else:
                with st.chat_message("assistant"):
                    st.write(message)
        '''

        # Wait for user input
        prompt = user_input
        if prompt:
            # ... (append user message to messages)
            self.messages.append(("user", prompt))
            # ... (display user message)
            # with st.chat_message("user"):
            #    st.write(prompt)

            # Generate AI response
            # with st.spinner('AI is thinking...'):
                # conversation.append(self.get_conversation(messages))

                # Check if input query is Obnoxious
            is_obnox = self.obnox_ag.check_query(prompt)

            if is_obnox:
                ai_message = "Please do not ask Obnoxious Questions "
                self.messages.append(("chatbot", ai_message))
                # with st.chat_message("assistant"):
                #    st.write(ai_message)

            else:
                if len(self.messages) > 5:
                    conversation_history = self.messages[-5:]
                else:
                    conversation_history = self.messages[:]

                # Retrive Relevant Documents
                extracted_res_query_agent = self.query_ag.extract_action(conversation_history)
                extracted_response = extracted_res_query_agent[0]
                extracted_text = extracted_res_query_agent[1]
                extracted_vecs = extracted_res_query_agent[2]
                
                if extracted_response != "No":
                    ai_message = extracted_response
                    self.messages.append(("chatbot", ai_message))

                    return ai_message
                    # with st.chat_message("assistant"):
                    #    st.write(ai_message)
                else:
                    print("is_revelant : ", extracted_vecs)
                    is_rel = self.rel_doc_ag.get_relevance(self.messages, extracted_text, extracted_vecs)
                    print("is_revelant : ", is_rel)
                    if (is_rel == "None") or (is_rel == None):
                        print("No Relevant Documents")
                        # prompt is not obnoxious but outside the scope of the document
                        # ai_message = self.answer_ag.generate_response(query=prompt, docs=None, 
                        #                                               conv_history=messages,mode = self.mode)
                        
                        ai_message = "No Relevant Documents found. Please ask a relevant question"
                        self.messages.append(("chatbot", ai_message))

                        return ai_message
                        # with st.chat_message("assistant"):
                        #    st.write(ai_message)

                    else:

                        # Get a namespace name from the dict
                        # TODO

                        # automatic prompt generation
                        # APE_prompt = """Based on {extracted_text}"""
                        # '''
                        # """Given a task that I want accomplished by an LLM as follows, can you generate an appropriate prompt that I can pass in to get a good response.\n
                        # Task: I want to query the Pinecone vector store to find the most relevant document to the query {query}\n
                        # If the query is a follow up question like "tell me more", "exlain in detail" etc; take the conversation history also into consideration to understand the context of the 
                        # query and generate the prompt.\n
                        # here is the previous conversation history : {conversation[-4:]}\n
                        # RETURN only the prompt that you have generated.
                        
                        # For example, if the query is 'tell me more' or 'explan in more detail' and the previous conversation history is
                        # ('user', 'tell me about gradient descent')
                        # then the generated prompt should be like 
                        # PROMPT: "Expand on the topic of gradient descent and provide more details"
                        # keep the prompt short and to the point.\n
                        # Only return the prompt that you have generated. and not the explanation of the prompt.
                        # """
                        # '''
                        # response = self.client.chat.completions.create(
                        # model="gpt-3.5-turbo",
                        # messages=[{"role": "user", "content": APE_prompt}]
                        # )
                        
                        # Pinecone_prompt = response.choices[0].message.content
                        # print("Pinecone Prompt : ", Pinecone_prompt)
                        
                        # Implement Pine Cone Query
                        # response_data = self.query_ag.query_vector_store(query=Pinecone_prompt, nameSpace='ns1')
                        # response_text = self.query_ag.extract_action(Pinecone_prompt,extracted_text,conversation)

                        #Implement the Answering Agent
                        ai_message = self.answer_ag.generate_response(query=prompt, docs=extracted_text, 
                                                                    conv_history=self.messages,mode = self.mode)

                        # Add the AI's response to the conversation history
                        self.messages.append(("chatbot", ai_message))
                        return ai_message
                        # with st.chat_message("assistant"):
                        #    st.write(ai_message)

        # Save session state variables
        # st.session_state.openai_model = openai_model
        # st.session_state.messages = messages


    # Define a function to get the conversation history (Not required for Part-2, will be useful in Part-3)
    def get_conversation(self, messages):
        # ... (code for getting conversation history)
        return "\n".join([f"{role}: {content}" for role, content in messages])

# Calling the main function
def main():
    # st.title("SCD Chatbot")
    # Set the OpenAI and Pinecone keys
    openai_key = 'OpenAI Key'
    pinecone_key = "pinecone key"#'bd8f871a-819e-42c8-a6ac-81c14948fefd'#'97497599-5ea9-4b33-ac6b-9f04930ad988'
    pinecone_index_name = 'scd001'
    messages = []
    
    # Initialize the Head_Agent
    head_agent = HeadAgent(openai_key, pinecone_key, pinecone_index_name, messages)
    # Setup the sub-agents
    head_agent.setup_sub_agents()
    # head_agent.main_loop()
    
# Run the main function
if __name__ == "__main__":
    main()

