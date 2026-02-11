from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool
from pydantic import EmailStr

from utils.schemas import CustomerBase


@tool(name_or_callable="get_all_customers")
def get_all_customers():
    """
    Retrieves a comprehensive list of all registered customers.

    **Triggers:**
    - Use this when the user asks to 'show all', 'list', 'fetch', or 'get data' for **customers** or **clients**.
    - Also use this if the user asks for a 'roster', 'directory', or 'names' of the entire customer base.

    **Scope:**
    - This tool returns the full dataset, including names, IDs, emails, and phone numbers for every customer in the system.
    """
    res = requests.get(
        "http://127.0.0.1:8000/customers/",
        headers=st.session_state.headers
    )
    data = res.json()
    return f"This is the data for all customers - {data}. Display this in a tabular format and do not miss any " \
           f"columns."


@tool(name_or_callable="search_customers")
def search_customers(
        customer_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        email: Optional[EmailStr] = None,
        phone: Optional[str] = None,
        created_by: Optional[int] = None
):
    """
    Search for specific customers by filtering on attributes such as `name`, `email`, `phone`, or `id`.

    **Triggers:** - **Strictly use this tool** when the user provides specific search criteria (e.g., 'Find customer
    John', 'Who is client 101?', 'Search for the guy with email x@y.com'). - Do NOT use this for generic 'list all
    customers' requests (use `get_all_customers` instead).

    **Supported Filters:**
    - Look for `first_name`, `last_name`, `email`, `phone_number`,`created_by` or `customer_id` in the user's request.
    """
    payload = {}
    if first_name:
        payload["first_name"] = first_name
    if last_name:
        payload["last_name"] = last_name
    if company:
        payload["company"] = company
    if email:
        payload["email"] = email
    if phone:
        payload["phone"] = phone
    if created_by:
        payload["created_by"] = created_by

    if customer_id:
        res = requests.get(
            f"http://127.0.0.1:8000/customers/{customer_id}",
            headers=st.session_state.headers
        )
        data = res.json()
        return f"The data for customer with id = {customer_id} is {data}. Display this customer in a nice format " \
               f"with all details visible  and assign color and emojis for any field you feel " \
               f"appropriate. Do not display this in tabular format "

    res = requests.get(
        "http://127.0.0.1:8000/customers/",
        headers=st.session_state.headers
    )
    data = res.json()

    return f"The data for all customers is {data}. Fetch entries that match the requirements given by user - " \
           f"{payload} and display it in tabular format without missing any columns."


@tool(name_or_callable="create_new_customer", args_schema=CustomerBase)  # type: ignore
def create_new_customer(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        email: Optional[EmailStr] = None,
        phone: Optional[str] = None
):
    """
    Creates a new customer account in the system.

    **Triggers:**
    - Call this when the user asks to 'add', 'create', 'register', or 'onboard' a new customer.

    **Critical Requirements:**
    - You **MUST** extract ALL of the following fields from the user's request:
      1. `first_name`
      2. `last_name`
      3. `email`
      4. `phone`
      5. `password` (passed to password_hash)
    - If ANY of these values are missing, **DO NOT** call this function. Instead, ask the user to provide the missing details.
    """
    missing = []
    if not first_name:
        missing.append("first_name")
    if not last_name:
        missing.append("last_name")
    if not company:
        missing.append("company")
    if not email:
        missing.append("email")

    if missing:
        return "Error! Missing required fields. Ask the user to fill them"

    customer = CustomerBase(
        first_name=first_name,
        last_name=last_name,
        company=company,
        email=email,
        phone=phone
    )
    res = requests.post(
        "http://127.0.0.1:8000/customers/",
        json=customer.model_dump(),
        headers=st.session_state.headers
    )
    return f"Successfully created a customer with id {res.json()['customer_id']}"


@tool(name_or_callable="update_customer_data")
def update_customer_data(
        customer_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        email: Optional[EmailStr] = None,
        phone: Optional[str] = None
):
    """
    Updates the profile details of an existing customer.

    **Triggers:**
    - Call this when the user asks to 'update', 'modify', 'edit', 'change', or 'correct' a customer's information.

    **Critical Requirements:** - You **MUST** extract and provide the `customer_id` to identify which record to
    update. - **Partial Updates:** Only include the specific fields the user wants to change (e.g., if they only say
    "change email to x", just provide `email` and `customer_id`). Leave other fields as `None`.
    """
    payload = {}
    if not customer_id:
        return "Cannot Edit a customer without an customer id. Please ask the user for customer_id"

    if first_name:
        payload["first_name"] = first_name
    if last_name:
        payload["last_name"] = last_name
    if company:
        payload["company"] = company
    if email:
        payload["email"] = email
    if phone:
        payload["phone"] = phone

    if not payload:
        return "You did not mention any fields to be updated. Need at least 1 field"

    try:
        res = requests.put(
            f"http://127.0.0.1:8000/customers/{customer_id}",
            json=payload,
            headers=st.session_state.headers
        )
        res.raise_for_status()
        if res.status_code == 200:
            return f"Successfully updated customer with id {res.json()['customer_id']}"
    except Exception as e:
        return f"The update process has failed and gave this error - {e} Explain the user what went wrong and how to " \
               f"correct it "
