from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
import streamlit as st
from ai_core import customer_tools, ticket_tools, employee_tools
from utils import helpers


class GeminiAssistant:
    llm_tools = [
        customer_tools.update_customer_data, ticket_tools.update_ticket, employee_tools.update_employee,
        customer_tools.get_all_customers, ticket_tools.get_all_tickets, employee_tools.get_all_employees,
        customer_tools.search_customers, ticket_tools.search_ticket, employee_tools.search_employee,
        customer_tools.create_new_customer, ticket_tools.create_new_ticket, employee_tools.create_new_employee
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
        "update_employee": employee_tools.update_employee
    }

    system_prompt = """
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
    """

    def __init__(self, model="gemini"):
        if model == "groq":
            self.llm = ChatGroq(
                model_name="qwen/qwen3-32b",
                # model_name="meta-llama/llama-prompt-guard-2-86m",
                temperature=0.7,
                api_key=st.secrets["groq_secret"]
            ).bind_tools(self.llm_tools)
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-exp",
                api_key=st.secrets["gemini_secret_1"]
            ).bind_tools(self.llm_tools)
        self.message_history = [
            SystemMessage(content=self.system_prompt)
        ]

    def send_message(self, prompt: str) -> str:

        self.message_history.append(HumanMessage(content=prompt))
        ai_msg = self.llm.invoke(self.message_history)
        self.message_history.append(ai_msg)
        if ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                name = tool_call["name"]
                args = tool_call["args"]

                if name in self.tools_map:
                    print(f"Executing Tool {name}")
                    result = self.tools_map[name].invoke(args)
                    self.message_history.append(
                        ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                    )
            final_response = self.llm.invoke(self.message_history)
            self.message_history.append(final_response)
            msg = helpers.get_clean_message(final_response)
            return msg
        else:
            msg = helpers.get_clean_message(ai_msg)
            return msg
