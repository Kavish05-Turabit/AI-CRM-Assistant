from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool

from utils import schemas as sch
from utils.schemas import TicketBase


@tool(name_or_callable="get_all_tickets")
def get_all_tickets():
    """ Fetch / Show all tickets. If user ask to see ticket data or all names of tickets fetch this"""
    res = requests.get(
        "http://127.0.0.1:8000/tickets/",
        headers=st.session_state.headers
    )
    data = res.json()
    return f"This is the data for all tickets - {data}. Display this in a tabular format and do not miss any " \
           f"columns."


@tool(name_or_callable="search_ticket")
def search_ticket(
        title: Optional[str] = None,
        description: Optional[str] = None,
        customer_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        ticket_type: Optional[sch.TicketType] = None,
        priority: Optional[sch.TicketPriority] = None,
        status: Optional[sch.TicketStatus] = None
):
    """
        If the user asks to fetch or search for any tickets data based on any of the above mentioned fields called this.
        Remember, call this only if user asks for a specific filter on tickets.
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


@tool(name_or_callable="create_new_ticket",args_schema=TicketBase)  # type: ignore
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
    When the user asks to create or add a new ticket , call this functions. If no description is provided then add
    one yourself in string format
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

        payload = t.model_dump(mode='json',exclude_none=True)
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
