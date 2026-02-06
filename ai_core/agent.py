from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage
from ai_core import customer_tools,ticket_tools,employee_tools
from utils import helpers


class GeminiAssistant:
    model = "gemini-3-flash"

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

    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            api_key=self.api_key
        ).bind_tools(self.llm_tools)
        self.message_history = []

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
