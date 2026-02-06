from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool

from utils import schemas as sch
from utils.schemas import EmployeeBase


@tool
def get_all_employees():
    """ Fetch / Show all employees. If user ask to see employee data or all names of employees fetch this"""
    res = requests.get(
        "http://127.0.0.1:8000/employees/",
        headers=st.session_state.headers
    )
    data = res.json()
    return f"This is the data for all employees - {data}. Display this in a tabular format and do not miss any " \
           f"columns."


@tool
def search_employee(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        access_level: Optional[sch.AccessLevel] = None
):
    """
        If the user asks to fetch or search for any employees data based on any of the above mentioned fields called this.
        Remember, call this only if user asks for a specific filter on employees.
    """
    try:
        payload = {}

        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if email:
            payload["email"] = email
        if phone:
            payload["phone"] = phone
        if access_level:
            payload["access_level"] = access_level

        res = requests.get(
            "http://127.0.0.1:8000/employees/",
            headers=st.session_state.headers
        )
        data = res.json()
        return f"The data for all employees is {data}. Fetch entries that match the requirements given by user - " \
               f"{payload} and display it in tabular format without missing any columns. Remember, STRICTLY " \
               f"TABULAR FORMAT"
    except Exception as e:
        return f"During Searching of employee, this following error has occurred - {e}." \
               "Explain the user what went wrong and give them correction in really short summary"
    pass


@tool(args_schema=EmployeeBase)  # type: ignore
def create_new_employee(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        access_level: Optional[sch.AccessLevel] = None,
        password_hash: Optional[str] = None
):
    """
    When the user asks to create or add a new employee , call this functions. If no access_level is provided then add
    one yourself as AGENT
    """
    try:
        missing = []
        if not first_name: missing.append("first_name")
        if not last_name: missing.append("last_name")
        if not email: missing.append("email")
        if not password_hash: missing.append("password_hash")

        if missing:
            return "Error! Missing required fields. Ask the user to fill them"

        e = EmployeeBase(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            access_level=access_level,
            phone=phone
        )

        payload = e.model_dump(mode='json',exclude_none=True)
        res = requests.post(
            "http://127.0.0.1:8000/employees/",
            json=payload,
            headers=st.session_state.headers
        )
        print(res.json())
        return f"Successfully created an employee with id {res.json().get('employee_id')}"
    except Exception as e:
        return f"During Creation of employee, this following error has occurred - {e}." \
               "Explain the user what went wrong and give them correction in really short summary"


@tool
def update_employee(
        employee_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        access_level: Optional[sch.AccessLevel] = None
):
    """
    Invoke this function if user wants to update or set value to an existing employee. user must
    provide an employee_id to do so. Also call this function when user asks to promote an employee.
    """
    payload = {}

    if first_name: payload["first_name"] = first_name
    if last_name: payload["last_name"] = last_name
    if email: payload["email"] = email
    if phone: payload["phone"] = phone
    if access_level: payload["access_level"] = access_level

    if not payload:
        return "You did not mention any fields to be updated. Need at least 1 field"

    try:
        res = requests.put(
            f"http://127.0.0.1:8000/employees/{employee_id}",
            json=payload,
            headers=st.session_state.headers
        )
        res.raise_for_status()
        if res.status_code == 200:
            return f"Successfully updated employee with id {res.json().get('employee_id')}"
    except Exception as e:
        return f"The update process has failed and gave this error - {e} Explain the user what went wrong and how to " \
               f"correct it "
