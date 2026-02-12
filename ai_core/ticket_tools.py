from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool

from utils import schemas as sch
from utils.schemas import TicketBase


@tool(name_or_callable="get_all_tickets")
def get_all_tickets():
    """
    Retrieves a comprehensive list of all support tickets in the system.

    Triggers:
    - Use this when the user asks to 'show all', 'list', 'fetch', or 'get data' for **tickets**, **issues**, **cases**, or **requests**.
    - Also use this if the user asks for a 'log', 'queue', or 'history' of all support items.

    Return:
    - DO not return all the ticket at once. Give only 10 tickets in tabular format and ask user if he wants
    more (next 10). If you already have all ticekts in context fetch the next tickets from there and do not
    call this function again.
    - Only return this fields in this same order in tabular format :- ticket_id , ticket_title, status, priority, type
    - Use emojis wherever you see fit for displaying data inside table
    """
    res = requests.get(
        "http://127.0.0.1:8000/tickets/",
        headers=st.session_state.headers
    )
    data = res.json()
    return f"This is the data for all tickets - {data}."


@tool(name_or_callable="search_ticket")
def search_ticket(
        ticket_id: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        customer_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        ticket_type: Optional[sch.TicketType] = None,
        priority: Optional[sch.TicketPriority] = None,
        status: Optional[sch.TicketStatus] = None,
        created_by_id: Optional[int] = None,
        quantity: Optional[int] = None
):
    """
    Search for and retrieve support tickets based on specific criteria. If user asks for a specific
    number of tickets and not all, use this.

    **Triggers:** - Call this when the user asks to 'find', 'search', 'get', or 'show' tickets matching specific
    attributes. - Examples: "Find ticket #105", "Show me high priority tickets", "List tickets for customer 12",
    "What is the status of the 'Login Error' ticket?".

    **Behavior & Parameters:** - **Single Ticket:** If the user provides a specific ID (e.g., "Ticket 10"),
    pass strictly `ticket_id`. - **Filtering:** Use other parameters (`status`, `priority`, `customer_id`,
    etc.) to filter the list. - **Status/Priority/Type:** Map adjectives like "urgent" -> `priority='Critical'`,
    "open" -> `status='Open'`, "bug" -> `ticket_type='Bug'`.

    **Exclusion:** - Do NOT use this if the user asks for "all tickets" or a "full list" without any conditions (use
    `get_all_tickets` instead).
    """
    try:

        payload = {}

        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if customer_id:
            payload["customer_id"] = customer_id
        if assignee_id:
            payload["assignee_id"] = assignee_id
        if ticket_type:
            payload["ticket_type"] = ticket_type
        if priority:
            payload["priority"] = priority
        if status:
            payload["status"] = status
        if created_by_id:
            payload["created_by_id"] = created_by_id
        if quantity:
            payload["quantity"] = quantity

        if ticket_id:
            res = requests.get(
                f"http://127.0.0.1:8000/tickets/{ticket_id}",
                headers=st.session_state.headers
            )
            data = res.json()
            return f"The data for ticket with id = {ticket_id} is {data}. Display this ticket in a nice format with " \
                   f"all details visible  and assign color and emojis for type or status pr any other field you feel " \
                   f"appropriate. Do not display this in tabular format "

        res = requests.get(
            "http://127.0.0.1:8000/tickets/",
            headers=st.session_state.headers
        )
        data = res.json()
        return f"The data for all tickets is {data}. Fetch entries that match the requirements given by user - " \
               f"{payload} and display it in tabular format without missing any columns. Remember, STRICTLY " \
               f"TABULAR FORMAT"
    except Exception as e:
        return f"During Searching of ticket, this following error has occurred - {e}." \
               "Explain the user what went wrong and give them correction in really short summary"
    pass


@tool(name_or_callable="create_new_ticket", args_schema=TicketBase)  # type: ignore
def create_new_ticket(
        title: Optional[str] = None,
        description: Optional[str] = None,
        customer_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        ticket_type: Optional[sch.TicketType] = None,
        priority: Optional[sch.TicketPriority] = None,
        status: Optional[sch.TicketStatus] = None
):
    """
    Creates a new support ticket in the system.

    **Triggers:**
    - Call this when the user asks to 'open', 'create', 'log', 'raise', or 'add' a new ticket or issue.

    **Critical Requirements:** - **Description:** If the user does not provide a description, **YOU MUST** generate a
    concise, professional description based on the title or context

    **Critical Prerequisite (Chaining):** - This function **REQUIRES** a numeric `customer_id`. - If the user
    provided a **name** (e.g., "Create a ticket for John"), you **MUST** first call `search_customers` to find John's
    `customer_id`. - **DO NOT** hallucinate or guess the ID. If you don't have it, find it first.
    """
    try:
        missing = []
        if not title: missing.append("title")
        if not customer_id: missing.append("customer_id")

        if missing:
            return "Error! Missing required fields. Ask the user to fill them"

        t = TicketBase(
            title=title,
            description=description,
            customer_id=customer_id,
            assignee_id=assignee_id,
            ticket_type=ticket_type,
            priority=priority,
            status=status
        )

        payload = t.model_dump(mode='json', exclude_none=True)
        res = requests.post(
            "http://127.0.0.1:8000/tickets/",
            json=payload,
            headers=st.session_state.headers
        )
        print(res.json())
        return f"Successfully created a ticket with id {res.json()['ticket_id']}"
    except Exception as e:
        return f"During Creation of ticket, this following error has occurred - {e}." \
               "Explain the user what went wrong and give them correction in really short summary"


@tool(name_or_callable="update_ticket")
def update_ticket(
        ticket_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        customer_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        ticket_type: Optional[sch.TicketType] = None,
        priority: Optional[sch.TicketPriority] = None,
        status: Optional[sch.TicketStatus] = None
):
    """
    Invoke this function if user wants to update or set value to an existing ticket. user must
    provide an ticket_id to do so. Also call this function when user asks to assign a ticket to someone or change the
    status of the ticket. user saying mark the ticket as done means to set its status to close.
    """
    payload = {}

    if title: payload["title"] = title
    if description: payload["description"] = description
    if customer_id: payload["customer_id"] = customer_id
    if assignee_id: payload["assignee_id"] = assignee_id
    if ticket_type: payload["ticket_type"] = ticket_type
    if priority: payload["priority"] = priority
    if status: payload["status"] = status

    if not payload:
        return "You did not mention any fields to be updated. Need at least 1 field"

    try:
        res = requests.put(
            f"http://127.0.0.1:8000/tickets/{ticket_id}",
            json=payload,
            headers=st.session_state.headers
        )
        res.raise_for_status()
        if res.status_code == 200:
            return f"Successfully updated ticket with id {res.json()['ticket_id']}"
    except Exception as e:
        return f"The update process has failed and gave this error - {e} Explain the user what went wrong and how to " \
               f"correct it "
