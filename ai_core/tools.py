from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool
from pydantic import EmailStr


@tool
def update_customer_data(
        customer_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        email: Optional[str] = None,
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

    res = requests.put(
        f"http://127.0.0.1:8000/customers/{customer_id}",
        json=payload,
        headers=st.session_state.headers
    )
    return f"Successfully updated customer with id {res.json()['customer_id']}"
