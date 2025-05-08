#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# JotForm API - MCP Server
#

import asyncio
import json
import os
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

# Assuming jotform.py is in the same directory or Python path
from jotform import JotformAPIClient

load_dotenv()

@dataclass
class JotformContext:
    """Context for the Jotform MCP server."""
    jotform_client: JotformAPIClient

@asynccontextmanager
async def jotform_lifespan(server: FastMCP) -> AsyncIterator[JotformContext]:
    """
    Manages the JotformAPIClient lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        JotformContext: The context containing the JotformAPIClient
    """
    api_key = os.getenv("JOTFORM_API_KEY")
    if not api_key or api_key == "YOUR_JOTFORM_API_KEY_HERE":
        logging.error("JOTFORM_API_KEY not found or not set in environment variables. Please set it in the .env file.")
        raise ValueError("JOTFORM_API_KEY not found or not set in environment variables.")

    base_url = os.getenv("JOTFORM_BASE_URL", JotformAPIClient.DEFAULT_BASE_URL)
    output_type = os.getenv("JOTFORM_OUTPUT_TYPE", "json")
    debug_mode_str = os.getenv("JOTFORM_DEBUG_MODE", "False")
    debug_mode = debug_mode_str.lower() in ['true', '1', 't', 'y', 'yes']

    client = JotformAPIClient(
        apiKey=api_key,
        baseUrl=base_url,
        outputType=output_type,
        debug=debug_mode
    )
    logging.info(f"JotformAPIClient initialized with base URL: {base_url}, output type: {output_type}, debug: {debug_mode}")
    
    try:
        yield JotformContext(jotform_client=client)
    finally:
        # No explicit cleanup needed for JotformAPIClient based on its current implementation
        logging.info("JotformAPIClient lifespan ended.")
        pass

# Initialize FastMCP server
mcp = FastMCP(
    "jotform-mcp-server",
    description="MCP server for interacting with the Jotform API.",
    lifespan=jotform_lifespan,
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8067"))
)

# Helper to process results and errors
async def _execute_jotform_request(client_method, *args, **kwargs) -> str:
    try:
        # client_method is already bound to the client instance if passed as client.method_name
        # If it's a string, we'd need client: client.method_name(args)
        raw_result = await asyncio.to_thread(client_method, *args, **kwargs)

        if isinstance(raw_result, (dict, list)):
            return json.dumps(raw_result, indent=2)
        elif isinstance(raw_result, str):
            try:
                parsed_json = json.loads(raw_result)
                return json.dumps(parsed_json, indent=2)
            except json.JSONDecodeError:
                # If not JSON (e.g. XML or plain text), wrap it
                return json.dumps({"data": raw_result}, indent=2)
        elif raw_result is None:
             return json.dumps({"data": None}, indent=2)
        else:
            return json.dumps({"data": str(raw_result)}, indent=2)
    except Exception as e:
        logging.error(f"Error during Jotform API request for method {client_method.__name__ if hasattr(client_method, '__name__') else 'unknown_method'}: {e}", exc_info=True)
        return json.dumps({"error": f"Jotform API Error: {str(e)}"}, indent=2)

# --- User Related Tools ---
@mcp.tool()
async def get_user(ctx: Context) -> str:
    """Get user account details for a JotForm user.

    Returns:
        User account type, avatar URL, name, email, website URL and account limits as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_user)

@mcp.tool()
async def get_usage(ctx: Context) -> str:
    """Get number of form submissions received this month.

    Returns:
        Number of submissions, SSL submissions, payment submissions, and upload space used as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_usage)

@mcp.tool()
async def get_forms(ctx: Context, offset: Optional[int] = None, limit: Optional[int] = None, filter_array: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None) -> str:
    """Get a list of forms for this account.

    Args:
        ctx: The MCP server context.
        offset (Optional[int]): Start of each result set for form list.
        limit (Optional[int]): Number of results in each result set for form list.
        filter_array (Optional[Dict[str, Any]]): Filters the query results. Example: {"status:eq": "ENABLED"}
        order_by (Optional[str]): Order results by a form field name.

    Returns:
        Basic details of forms as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_forms, offset=offset, limit=limit, filterArray=filter_array, order_by=order_by)

@mcp.tool()
async def get_submissions(ctx: Context, offset: Optional[int] = None, limit: Optional[int] = None, filter_array: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None) -> str:
    """Get a list of submissions for this account.

    Args:
        ctx: The MCP server context.
        offset (Optional[int]): Start of each result set.
        limit (Optional[int]): Number of results in each result set.
        filter_array (Optional[Dict[str, Any]]): Filters the query results.
        order_by (Optional[str]): Order results by a field name.

    Returns:
        Basic details of submissions as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_submissions, offset=offset, limit=limit, filterArray=filter_array, order_by=order_by)

@mcp.tool()
async def get_subusers(ctx: Context) -> str:
    """Get a list of sub users for this account.

    Returns:
        List of forms and form folders with access privileges as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_subusers)

@mcp.tool()
async def get_folders(ctx: Context) -> str:
    """Get a list of form folders for this account.

    Returns:
        Name of the folder and owner of the folder for shared folders as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_folders)

@mcp.tool()
async def get_reports(ctx: Context) -> str:
    """List of URLs for reports in this account.

    Returns:
        Reports for all of the forms (Excel, CSV, etc.) as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_reports)

@mcp.tool()
async def get_settings(ctx: Context) -> str:
    """Get user's settings for this account.

    Returns:
        User's time zone and language as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_settings)

@mcp.tool()
async def update_settings(ctx: Context, settings: Dict[str, Any]) -> str:
    """Update user's settings.

    Args:
        ctx: The MCP server context.
        settings (Dict[str, Any]): New user setting values with setting keys.

    Returns:
        Changes on user settings as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.update_settings, settings)

@mcp.tool()
async def get_history(ctx: Context, action: Optional[str] = None, date: Optional[str] = None, sort_by: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """Get user activity log.

    Args:
        ctx: The MCP server context.
        action (Optional[str]): Filter results by activity performed. Default is 'all'.
        date (Optional[str]): Limit results by a date range.
        sort_by (Optional[str]): Lists results by ascending and descending order.
        start_date (Optional[str]): Limit results to only after a specific date. Format: MM/DD/YYYY.
        end_date (Optional[str]): Limit results to only before a specific date. Format: MM/DD/YYYY.

    Returns:
        Activity log as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_history, action=action, date=date, sortBy=sort_by, startDate=start_date, endDate=end_date)

# --- Form Related Tools ---
@mcp.tool()
async def get_form(ctx: Context, form_id: str) -> str:
    """Get basic information about a form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.

    Returns:
        Form details as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form, form_id)

@mcp.tool()
async def get_form_questions(ctx: Context, form_id: str) -> str:
    """Get a list of all questions on a form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.

    Returns:
        Question properties of a form as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form_questions, form_id)

@mcp.tool()
async def get_form_question(ctx: Context, form_id: str, qid: str) -> str:
    """Get details about a question.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        qid (str): Question ID.

    Returns:
        Question properties as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form_question, form_id, qid)

@mcp.tool()
async def get_form_submissions(ctx: Context, form_id: str, offset: Optional[int] = None, limit: Optional[int] = None, filter_array: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None) -> str:
    """List of a form submissions.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        offset (Optional[int]): Start of each result set.
        limit (Optional[int]): Number of results in each result set.
        filter_array (Optional[Dict[str, Any]]): Filters the query results.
        order_by (Optional[str]): Order results by a field name.

    Returns:
        Submissions of a specific form as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form_submissions, form_id, offset=offset, limit=limit, filterArray=filter_array, order_by=order_by)

@mcp.tool()
async def create_form_submission(ctx: Context, form_id: str, submission: Dict[str, Any]) -> str:
    """Submit data to this form using the API.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        submission (Dict[str, Any]): Submission data with question IDs.
            Example: {"1_first": "John", "1_last": "Doe", "2": "test@example.com"}
            For complex fields like name (qid_first, qid_last) or address (qid_addr_line1), use the underscore notation.

    Returns:
        Posted submission ID and URL as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    # The client method handles formatting `submission` internally.
    return await _execute_jotform_request(client.create_form_submission, form_id, submission)

@mcp.tool()
async def create_form_submissions(ctx: Context, form_id: str, submissions: Union[List[Dict[str, Any]], str]) -> str:
    """Submit multiple data entries to a form using the API (via PUT request).

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        submissions (Union[List[Dict[str, Any]], str]): A list of submission objects or a JSON string representing the list.
            Each submission object is a dictionary of submission data with question IDs.
            Example: [{"1_first": "Jane", "2": "jane@example.com"}, {"1_first": "Mike", "2": "mike@example.com"}]

    Returns:
        Response from the API, typically indicating success or failure, as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    # The client method expects a JSON string for the PUT body.
    submissions_json_str = submissions
    if isinstance(submissions, list):
        submissions_json_str = json.dumps(submissions)
    
    return await _execute_jotform_request(client.create_form_submissions, form_id, submissions_json_str)


@mcp.tool()
async def get_form_files(ctx: Context, form_id: str) -> str:
    """List of files uploaded on a form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.

    Returns:
        Uploaded file information and URLs as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form_files, form_id)

@mcp.tool()
async def get_form_webhooks(ctx: Context, form_id: str) -> str:
    """Get list of webhooks for a form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.

    Returns:
        List of webhooks as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form_webhooks, form_id)

@mcp.tool()
async def create_form_webhook(ctx: Context, form_id: str, webhook_url: str) -> str:
    """Add a new webhook.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        webhook_url (str): Webhook URL.

    Returns:
        List of webhooks for the form as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.create_form_webhook, form_id, webhook_url)

@mcp.tool()
async def delete_form_webhook(ctx: Context, form_id: str, webhook_id: str) -> str:
    """Delete a specific webhook of a form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        webhook_id (str): Webhook ID.

    Returns:
        Remaining webhook URLs of form as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.delete_form_webhook, form_id, webhook_id)

# --- Submission Related Tools ---
@mcp.tool()
async def get_submission(ctx: Context, sid: str) -> str:
    """Get submission data.

    Args:
        ctx: The MCP server context.
        sid (str): Submission ID.

    Returns:
        Information and answers of a specific submission as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_submission, sid)

@mcp.tool()
async def delete_submission(ctx: Context, sid: str) -> str:
    """Delete a single submission.

    Args:
        ctx: The MCP server context.
        sid (str): Submission ID.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.delete_submission, sid)

@mcp.tool()
async def edit_submission(ctx: Context, sid: str, submission: Dict[str, Any]) -> str:
    """Edit a single submission.

    Args:
        ctx: The MCP server context.
        sid (str): Submission ID.
        submission (Dict[str, Any]): New submission data with question IDs.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.edit_submission, sid, submission)

# --- Report Related Tools ---
@mcp.tool()
async def get_report(ctx: Context, report_id: str) -> str:
    """Get report details.

    Args:
        ctx: The MCP server context.
        report_id (str): Report ID.

    Returns:
        Properties of a specific report as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_report, report_id)

@mcp.tool()
async def create_report(ctx: Context, form_id: str, report: Dict[str, Any]) -> str:
    """Create new report of a form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        report (Dict[str, Any]): Report details (list_type, title, etc.).

    Returns:
        Report details and URL as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.create_report, form_id, report)

@mcp.tool()
async def delete_report(ctx: Context, report_id: str) -> str:
    """Delete a specific report.

    Args:
        ctx: The MCP server context.
        report_id (str): Report ID.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.delete_report, report_id)

# --- Folder Related Tools ---
@mcp.tool()
async def get_folder(ctx: Context, folder_id: str) -> str:
    """Get folder details.

    Args:
        ctx: The MCP server context.
        folder_id (str): Folder ID.

    Returns:
        A list of forms in a folder and other details as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_folder, folder_id)

@mcp.tool()
async def create_folder(ctx: Context, folder_properties: Dict[str, Any]) -> str:
    """Create a new folder.

    Args:
        ctx: The MCP server context.
        folder_properties (Dict[str, Any]): Properties of the new folder.

    Returns:
        New folder details as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.create_folder, folder_properties)

@mcp.tool()
async def delete_folder(ctx: Context, folder_id: str) -> str:
    """Delete a specific folder and its subfolders.

    Args:
        ctx: The MCP server context.
        folder_id (str): Folder ID.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.delete_folder, folder_id)

@mcp.tool()
async def update_folder(ctx: Context, folder_id: str, folder_properties: Union[Dict[str, Any], str]) -> str:
    """Update a specific folder.

    Args:
        ctx: The MCP server context.
        folder_id (str): Folder ID.
        folder_properties (Union[Dict[str, Any], str]): New properties of the folder (dict or JSON string).
            The client method expects a JSON string for the PUT body.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    properties_json_str = folder_properties
    if isinstance(folder_properties, dict):
        properties_json_str = json.dumps(folder_properties)
    return await _execute_jotform_request(client.update_folder, folder_id, properties_json_str)

@mcp.tool()
async def add_forms_to_folder(ctx: Context, folder_id: str, form_ids: List[str]) -> str:
    """Add forms to a folder.

    Args:
        ctx: The MCP server context.
        folder_id (str): Folder ID.
        form_ids (List[str]): List of Form IDs.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    # The client.add_forms_to_folder method internally calls update_folder with a JSON string.
    return await _execute_jotform_request(client.add_forms_to_folder, folder_id, form_ids)

@mcp.tool()
async def add_form_to_folder(ctx: Context, folder_id: str, form_id: str) -> str:
    """Add a specific form to a folder.

    Args:
        ctx: The MCP server context.
        folder_id (str): Folder ID.
        form_id (str): Form ID.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    # The client.add_form_to_folder method internally calls update_folder with a JSON string.
    return await _execute_jotform_request(client.add_form_to_folder, folder_id, form_id)


# --- Form Properties ---
@mcp.tool()
async def get_form_properties(ctx: Context, form_id: str) -> str:
    """Get a list of all properties on a form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.

    Returns:
        Form properties as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form_properties, form_id)

@mcp.tool()
async def get_form_property(ctx: Context, form_id: str, property_key: str) -> str:
    """Get a specific property of the form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        property_key (str): Property key.

    Returns:
        Given property key value as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form_property, form_id, property_key)

@mcp.tool()
async def set_form_properties(ctx: Context, form_id: str, form_properties: Dict[str, Any]) -> str:
    """Add or edit properties of a specific form (POST).

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        form_properties (Dict[str, Any]): New properties.

    Returns:
        Edited properties as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.set_form_properties, form_id, form_properties)

@mcp.tool()
async def set_multiple_form_properties(ctx: Context, form_id: str, form_properties: Union[Dict[str, Any], str]) -> str:
    """Add or edit properties of a specific form (PUT).

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        form_properties (Union[Dict[str, Any], str]): New properties (dict or JSON string).
            The client method expects a JSON string for the PUT body.

    Returns:
        Edited properties as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    properties_json_str = form_properties
    if isinstance(form_properties, dict):
        properties_json_str = json.dumps(form_properties)
    return await _execute_jotform_request(client.set_multiple_form_properties, form_id, properties_json_str)


# --- Form Reports ---
@mcp.tool()
async def get_form_reports(ctx: Context, form_id: str) -> str:
    """Get all the reports of a form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.

    Returns:
        List of all reports in a form as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_form_reports, form_id)


# --- Form Cloning, Deletion, Creation ---
@mcp.tool()
async def clone_form(ctx: Context, form_id: str) -> str:
    """Clone a single form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.

    Returns:
        Status of request (details of the new cloned form) as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.clone_form, form_id)

@mcp.tool()
async def delete_form_question(ctx: Context, form_id: str, qid: str) -> str:
    """Delete a single form question.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        qid (str): Question ID.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.delete_form_question, form_id, qid)

@mcp.tool()
async def create_form_question(ctx: Context, form_id: str, question: Dict[str, Any]) -> str:
    """Add new question to specified form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        question (Dict[str, Any]): New question properties.

    Returns:
        Properties of new question as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.create_form_question, form_id, question)

@mcp.tool()
async def create_form_questions(ctx: Context, form_id: str, questions: Union[List[Dict[str, Any]], str]) -> str:
    """Add new questions to specified form (PUT).

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        questions (Union[List[Dict[str, Any]], str]): New questions (list of dicts or JSON string).
            The client method expects a JSON string for the PUT body.

    Returns:
        Properties of new questions as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    questions_json_str = questions
    if isinstance(questions, list):
        questions_json_str = json.dumps(questions)
    return await _execute_jotform_request(client.create_form_questions, form_id, questions_json_str)

@mcp.tool()
async def edit_form_question(ctx: Context, form_id: str, qid: str, question_properties: Dict[str, Any]) -> str:
    """Add or edit a single question properties.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.
        qid (str): Question ID.
        question_properties (Dict[str, Any]): New question properties.

    Returns:
        Edited property and type of question as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.edit_form_question, form_id, qid, question_properties)

@mcp.tool()
async def create_form(ctx: Context, form_definition: Dict[str, Any]) -> str:
    """Create a new form.

    Args:
        ctx: The MCP server context.
        form_definition (Dict[str, Any]): Questions, properties, and emails of the new form.
            Example: {"questions": [{"type": "control_textbox", "text": "Name", "order": "1"}],
                      "properties": {"title": "My New Form"}}

    Returns:
        New form details as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    # The client method handles formatting `form_definition` internally.
    return await _execute_jotform_request(client.create_form, form_definition)

@mcp.tool()
async def create_forms(ctx: Context, forms_definition: Union[List[Dict[str, Any]], str]) -> str:
    """Create new forms (PUT).

    Args:
        ctx: The MCP server context.
        forms_definition (Union[List[Dict[str, Any]], str]): List of form definitions or a JSON string.
            The client method expects a JSON string for the PUT body.

    Returns:
        New forms details as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    forms_json_str = forms_definition
    if isinstance(forms_definition, list):
        forms_json_str = json.dumps(forms_definition)
    return await _execute_jotform_request(client.create_forms, forms_json_str)

@mcp.tool()
async def delete_form(ctx: Context, form_id: str) -> str:
    """Delete a specific form.

    Args:
        ctx: The MCP server context.
        form_id (str): Form ID.

    Returns:
        Properties of deleted form as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.delete_form, form_id)

# --- User Account Management (Potentially sensitive, use with caution) ---
@mcp.tool()
async def register_user(ctx: Context, user_details: Dict[str, str]) -> str:
    """Register with username, password and email.

    Args:
        ctx: The MCP server context.
        user_details (Dict[str, str]): Username, password, and email.

    Returns:
        New user's details as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.register_user, user_details)

@mcp.tool()
async def login_user(ctx: Context, credentials: Dict[str, str]) -> str:
    """Login user with given credentials.

    Args:
        ctx: The MCP server context.
        credentials (Dict[str, str]): Username, password, application name, and access type.

    Returns:
        Logged in user's settings and app key as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.login_user, credentials)

@mcp.tool()
async def logout_user(ctx: Context) -> str:
    """Logout user.

    Returns:
        Status of request as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.logout_user)

# --- System ---
@mcp.tool()
async def get_plan(ctx: Context, plan_name: str) -> str:
    """Get details of a plan.

    Args:
        ctx: The MCP server context.
        plan_name (str): Name of the requested plan (e.g., FREE, PREMIUM).

    Returns:
        Details of a plan as a JSON string.
    """
    client = ctx.request_context.lifespan_context.jotform_client
    return await _execute_jotform_request(client.get_plan, plan_name)


async def main():
    """Runs the MCP server."""
    transport = os.getenv("MCP_TRANSPORT", "sse").lower()
    logging.info(f"Starting Jotform MCP server with {transport} transport...")
    if transport == 'sse':
        await mcp.run_sse_async()
    elif transport == 'stdio':
        await mcp.run_stdio_async()
    else:
        logging.warning(f"Unsupported MCP_TRANSPORT type: {transport}. Defaulting to SSE.")
        await mcp.run_sse_async()

if __name__ == "__main__":
    # Setup basic logging for the script itself
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())
