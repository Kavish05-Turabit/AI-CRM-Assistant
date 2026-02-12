from typing import Optional

import requests
import streamlit as st
from langchain_core.tools import tool

from utils import schemas as sch
from utils.schemas import EmployeeBase


@tool(name_or_callable="get_all_employees")
def get_all_employees():
    """
    Retrieves a comprehensive list of all employees from the organization's database. Use this tool when the user
    asks to 'show all employees', 'list everyone', 'get employee data', or specifically requests names, roles, IDs,
    or contact details of the staff. It provides a full roster of current personnel.

    Return:
    - DO not return all the employees at once. Give only 10 employees in tabular format and ask user if he wants
    more (next 10). If you already have all employees in context fetch the next employees from there and do not
    call this function again.
    - Only return this fields in this same order in tabular format :- emp_id, firstname, lastname, access_level
    - Use emojis wherever you see fit for displaying data inside table
    """
    res = requests.get(
        "http://127.0.0.1:8000/employees/",
        headers=st.session_state.headers
    )
    data = res.json()
    return f"This is the data for all employees - {data}. Display this in a tabular format and do not miss any " \
           f"columns."


@tool(name_or_callable="search_employee")
def search_employee(
        employee_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        access_level: Optional[sch.AccessLevel] = None
):
    """
    Search for specific employees by filtering on attributes such as first_name, last_name, role, department, email,
    or employee_id. Strictly use this tool when the user provides specific criteria (e.g., 'Find John', 'Who is the
    manager?', 'Get details for employee 101'). Do NOT use this for generic 'list all employees' requests.
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

        if employee_id:
            res = requests.get(
                f"http://127.0.0.1:8000/employees/{employee_id}",
                headers=st.session_state.headers
            )
            data = res.json()
            return f"The data for employee with id = {employee_id} is {data}. Display this employee in a nice format with " \
                   f"all details visible  and assign color and emojis for any field you feel " \
                   f"appropriate. Do not display this in tabular format "

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


@tool(name_or_callable="create_new_employee",args_schema=EmployeeBase)  # type: ignore
def create_new_employee(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        access_level: Optional[sch.AccessLevel] = None,
        password_hash: Optional[str] = None
):
    """
    Creates a new employee account in the system.

    Use this tool when the user asks to 'add', 'create', 'register', or 'onboard' a new staff member.

    **Parameters to Extract:**
    - `first_name`, `last_name`, `email`, `phone`, and `password` (passed to password_hash).

    **Critical Logic:**
    - If the user provides a specific role/permission (e.g., 'Make them an Admin'), map it to `access_level`.
    - **If NO access level is specified, you MUST default `access_level` to 'AGENT'.**
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


@tool(name_or_callable="update_employee")
def update_employee(
        employee_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        access_level: Optional[sch.AccessLevel] = None
):
    """
    Updates the details of an existing employee.

    Triggers:
    - Call this when the user asks to 'update', 'modify', 'edit', or 'change' an employee's information.
    - ALSO call this when the user asks to **'promote'** or **'demote'** an employee (by changing their `access_level` or `role`).
    - If promote then access level is admin and if demote then access level is agent
    Critical Requirements:
    - You MUST extract and provide the `employee_id` to identify which record to update.
    - Only include the fields that need changing; leave others as None.
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
