from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool

from utils import schemas as sch


@tool(name_or_callable="show_individual_analysis")
def show_individual_analysis(
        employee_id: Optional[int] = None,
        customer_id: Optional[int] = None,
):
    """
    Fetches raw ticket data to generate a detailed performance or activity analysis for a specific Employee OR Customer.

    **WHEN TO USE:**
    - Use this when the user asks to "analyze", "review performance", "check stats", or "show history" for a person.
    - REQUIRED: You must have either an `employee_id` OR a `customer_id`.

    **CRITICAL INSTRUCTION FOR THE AI (HOW TO DISPLAY DATA):**
    Do NOT output the raw JSON. You must calculate and present a "Statistical Dashboard" using the returned data.
    If the api says that no employee/customer can be found with the key they provided, inform the user that no
    employee/customer with that id exist.

    **Layout & Visuals to Generate:**
    1.  **📊 Executive Summary**:
        - Total Tickets Found.
        - Active vs. Resolved Count.

    2.  **🚨 Priority Breakdown** (Use emojis):
        - 🔴 Critical/High: [Count]
        - 🟡 Medium: [Count]
        - 🔵 Low: [Count]

    3.  **🥧 Status Distribution**:
        - Create a text-based bar chart (e.g., "Open: ■■■■■ (5)", "Closed: ■■ (2)").

    4.  **🏷️ Ticket Type Analysis**:
        - Count of Bugs vs. Features vs. Inquiries.

    5.  **📋 Recent Activity Log**:
        - List the last 3-5 tickets with their ID, Title, and current Status formatted as a clean table.

    **Example Output Style:**
    "### 👤 Analysis for Employee #42
    **Performance Score:** 95% Resolution Rate 🚀
    ...
    """
    q_params = {
        "customer_id": customer_id,
        "employee_id": employee_id
    }
    res = requests.get(
        "http://127.0.0.1:8000/tickets/search",
        headers=st.session_state.headers,
        params=q_params
    )
    data = res.json()
    return f"This is the data for the requested query - {data}"


@tool()
def show_overall_analysis():
    """
    When the user asks to fetch overall, complete, current or just analysis without mentioning emp id or cust id, call this function.
    Evaluate the data sent by the api ask Display it in visually compelling manner.
    :return:
    """
    res = requests.get(
        "http://127.0.0.1:8000/dashboard/",
        headers=st.session_state.headers,
    )
    data = res.json()
    return f"This is the data for the requested query - {data}"
