from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool

from utils import schemas as sch
from utils.schemas import TicketBase


@tool(args_schema=TicketBase)  # type: ignore
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
    pass
