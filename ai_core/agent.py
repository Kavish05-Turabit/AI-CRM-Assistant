from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, AnyMessage, AIMessage
import streamlit as st
from ai_core import customer_tools, ticket_tools, employee_tools, statistic_tools
from utils import helpers


class GeminiAssistant:
    llm_tools = [
        customer_tools.update_customer_data, ticket_tools.update_ticket, employee_tools.update_employee,
        customer_tools.get_all_customers, ticket_tools.get_all_tickets, employee_tools.get_all_employees,
        customer_tools.search_customers, ticket_tools.search_ticket, employee_tools.search_employee,
        customer_tools.create_new_customer, ticket_tools.create_new_ticket, employee_tools.create_new_employee,
        statistic_tools.show_individual_analysis, statistic_tools.show_overall_analysis
    ]

    tools_map = {
        # customer tools
        "update_customer_data": customer_tools.update_customer_data,
        "search_customers": customer_tools.search_customers,
        "get_all_customers": customer_tools.get_all_customers,
        "create_new_customer": customer_tools.create_new_customer,

        # tickets tool
        "create_new_ticket": ticket_tools.create_new_ticket,
        "get_all_tickets": ticket_tools.get_all_tickets,
        "search_ticket": ticket_tools.search_ticket,
        "update_ticket": ticket_tools.update_ticket,

        # employee tools
        "create_new_employee": employee_tools.create_new_employee,
        "get_all_employees": employee_tools.get_all_employees,
        "search_employee": employee_tools.search_employee,
        "update_employee": employee_tools.update_employee,

        # statistic tools
        "show_individual_analysis": statistic_tools.show_individual_analysis,
        "show_overall_analysis": statistic_tools.show_overall_analysis
    }

    MODEL_OPTIONS = {
        "Gemini": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3-flash"],
        "Groq": ["llama-3.3-70b-versatile", "qwen/qwen3-32b"]
    }

    system_prompt = f"""
    You are the AI CRM Assistant, a specialized agent designed to help employees manage the company's internal database. Your primary role is to interact with the database using your provided tools to handle Customers, Support Tickets, and Employee records.

        ### 1. YOUR CAPABILITIES & TOOLS
        You have access to three core domains. You must ALWAYS use a tool to fetch or modify data. Never guess or hallucinate database records.
        
        * **Customers:** You can search, create, update, and list customers.
        * **Tickets:** You can manage support tickets (create, update, search, assign).
        * **Employees:** You can manage employee records and access levels.
        
        ### 2. OPERATIONAL RULES
        * **Data Presentation:** When displaying lists of data (e.g., "Show all tickets", "Find customers named John"), you must **STRICTLY use a Markdown Table**. Ensure columns align correctly.
        * **Missing Information:** Do NOT make up IDs or required fields. If a user asks "Update the ticket" without specifying *which* ticket ID, you must ask: "Which ticket ID would you like to update?"
        * **ID Handling:** IDs are integers. If a user provides an ID like "#8" or "ID: 8", extract just the integer `8` for the tool.
        * **Creation logic:**
            * **Tickets:** If the user doesn't provide a description, generate a short, professional one based on the title.
            * **Defaults:** If the user doesn't specify priority (Tickets) or access level (Employees), rely on the tool's default values (usually 'Medium' or 'Agent') rather than asking, unless it is critical.
        
        ### 3. ERROR HANDLING
        * If a tool returns an error (e.g., "API Failed"), explain it to the user in plain English. Do not show raw JSON errors unless explicitly asked.
        * Example: Instead of "KeyError: 'id'", say "I encountered an error creating that record. It seems the database rejected the input."
        
        ### 4. TONE & STYLE
        * Be concise, professional, and helpful.
        * Do not be overly chatty. Get straight to the task.
        * "Agent" refers to the employee using this system. Address them respectfully.
        
        You are an autonomous agent. If a user requests an action that requires a specific ID (like customer_id) but 
        only provides a name, you must automatically use your search tools to find that ID. Do not ask the user for 
        information you can retrieve yourself. 
        
        The ID of current Employee is {st.session_state.current_emp}. If the user asks anything while using words like
        me, mine, my , owned by me. etc than consider this id.
        IT matches to assignee_id or created_by_id in tickets table based on the context given. Unless the user mentions,
        it matches to assignee_id
        IT matches to created_by field in customers table.
        The access of current employee is {st.session_state.access_level}
        
        If the user mentions last or latest ticket, last customer or last employee, understand that he is mentioning the latest
        created record of that type and do any aforementioned operations with that in mind.
        """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=st.secrets["gemini_secret_4"]
        ).bind_tools(self.llm_tools)
        self.provider = "gemini"
        self.message_history: List[AnyMessage] = []
        self.message_history.append(SystemMessage(content=self.system_prompt))

    def config_model(self, model, provider, api_key):
        """
        User can add their own api key for any of the supported model.
        :param model: Any tool supported model
        :param provider: ["Gemini","Groq"]
        :param api_key: Secret key
        :return:
        """
        try:
            if provider == "Gemini":
                self.provider = "gemini"
                self.llm = ChatGoogleGenerativeAI(
                    model=model,
                    api_key=api_key
                ).bind_tools(self.llm_tools)
            if provider == "Groq":
                self.provider = "groq"
                self.llm = ChatGroq(
                    model=model,
                    api_key=api_key,
                    temperature=0
                ).bind_tools(self.llm_tools)
        except Exception as e:
            st.error("Model unsupported! Please select appropriate model")

    def send_message(self, prompt: str) -> [str, None]:
        """
        This functions is used to send messages to the selected LLM.
        :param prompt: The user Query
        :return: Response by the LLM for user query
        """
        self.message_history.append(HumanMessage(content=prompt))
        stateless_memory = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        try:
            if self.provider == "gemini":
                ai_msg = self.llm.invoke(self.message_history)
            else:
                ai_msg = self.llm.invoke(stateless_memory)
        except Exception as e:
            st.error(f"Some Error occurred on API side. Please Change API model -  {e}")
            return "Some error occurred in LLM side! Please change model or try again later."
        self.message_history.append(ai_msg)
        while ai_msg.tool_calls:
            tool_messages = []
            for tool_call in ai_msg.tool_calls:
                name = tool_call["name"]
                args = tool_call["args"]

                if name in self.tools_map:
                    print(f"Executing Tool {name}")
                    result = self.tools_map[name].invoke(args)
                    self.message_history.append(
                        ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                    )
                    tool_messages.append(
                        ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                    )
            try:
                if self.provider == "gemini":
                    ai_msg = self.llm.invoke(self.message_history)
                else:
                    stateless_memory.append(ai_msg)
                    stateless_memory.extend(tool_messages)
                    ai_msg = self.llm.invoke(stateless_memory)
                self.message_history.append(ai_msg)
                print(ai_msg)
            except Exception as e:
                st.error(f"API Error in loop: {e}")
                return "Some error occurred in LLM side! Please change model or try again later."
        msg = helpers.get_clean_message(ai_msg)
        if not msg:
            msg = "Action completed successfully."
            self.message_history.append(AIMessage(content=msg))
        return msg

    def get_model_options(self):
        return self.MODEL_OPTIONS
