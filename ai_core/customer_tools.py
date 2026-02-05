from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool
from pydantic import EmailStr

from utils.schemas import CustomerBase


@tool
def get_all_customers():
    """ Fetch / Show all customers. If user ask to see customer data or all names of customers fetch this"""
    res = requests.get(
        "http://127.0.0.1:8000/customers/",
        headers=st.session_state.headers
    )
    data = res.json()
    return f"This is the data for all customers - {data}. Display this in a tabular format and do not miss any " \
           f"columns."


@tool
def search_customers(
        customer_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        email: Optional[EmailStr] = None,
        phone: Optional[str] = None
):
    """
        If the user asks to fetch or search for any customers data based on any of the above mentioned fields called this.
        Remember, call this only if user asks for a specific filter on customers.
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

    res = requests.get(
        "http://127.0.0.1:8000/customers/",
        headers=st.session_state.headers
    )
    data = res.json()

    return f"The data for all customers is {data}. Fetch entries that match the requirements given by user - " \
           f"{payload} and display it in tabular format without missing any columns."


@tool(args_schema=CustomerBase)  # type: ignore
def create_new_customer(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        email: Optional[EmailStr] = None,
        phone: Optional[str] = None
):
    """When the user asks to create or add a new customer , call this functions and check all the values are given to
    it """
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


@tool
def update_customer_data(
        customer_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        email: Optional[EmailStr] = None,
        phone: Optional[str] = None
):
    """ Invoke this function if user wants to update or set value to an existing customer. user must
        provide an customer_id to do so.
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
