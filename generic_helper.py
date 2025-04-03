import uuid
from IPython.display import display, HTML
import json
import logging
import pandas as pd
import datetime
from sqlite_helper import (
    list_tables,
    describe_table_schema,
    run_sql_query,
    get_sample_rows,
)
from file_helper import read_file, write_file, list_files

# Set up logging with a simple format
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


def create_collapsible(header, content, open_by_default=False):
    """Create a collapsible HTML section for Jupyter"""
    unique_id = f"collapse_{uuid.uuid4().hex[:8]}"
    open_state = "checked" if open_by_default else ""
    html = f"""
    <div style="margin: 10px 0;">
        <input type="checkbox" id="{unique_id}" {open_state} class="collapsible-checkbox" style="display:none;">
        <label for="{unique_id}" style="background-color: #f0f0f0; padding: 8px; border-radius: 4px; cursor: pointer; display: block; border: 1px solid #ccc;">r
            <span style="font-weight: bold;">▶ {header}</span>
        </label>
        <div class="collapsible-content" style="padding: 10px; border: 1px solid #ddd; border-top: none; display: none; overflow: auto; max-height: 500px;">
            <pre style="white-space: pre-wrap; margin: 0;">{content}</pre>
        </div>
    </div>
    <script>
    (function() {{
        var checkBox = document.getElementById("{unique_id}");
        var content = checkBox.nextElementSibling.nextElementSibling;
        var arrow = checkBox.nextElementSibling.firstElementChild;
        
        // Initial state
        if (checkBox.checked) {{{{
            content.style.display = "block";
            arrow.textContent = "▼ {header}";
        }}}}
        
        // Toggle state when clicked
        checkBox.addEventListener('change', function() {{{{
            if (this.checked) {{{{
                content.style.display = "block";
                arrow.textContent = "▼ {header}";
            }}}} else {{{{
                content.style.display = "none";
                arrow.textContent = "▶ {header}";
            }}}}
        }}}});
    }})();
    </script>
    """
    return HTML(html)


def invoke_agent(
    bedrock_agent_runtime_client, agent_id, prompt, session_id=None, enable_trace=False
):
    """
    Invokes a Bedrock agent with support for return of control (function calling)
    and collapsible trace output in Jupyter notebooks.
    Handles recursive function calls that may be needed by the agent.
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    def process_agent_response(agent_response):
        """
        Helper function to process agent responses recursively
        """
        # if enable_trace and 'ResponseMetadata' in agent_response:
        #     # Display response metadata in a collapsible section
        #     metadata_str = json.dumps(agent_response['ResponseMetadata'], indent=2)
        #     display(create_collapsible("RESPONSE METADATA", metadata_str))

        event_stream = agent_response["completion"]
        trace_count = 0
        response_text = None

        try:
            for event in event_stream:
                if "chunk" in event:
                    data = event["chunk"]["bytes"]
                    response_text = data.decode("utf8")
                    if enable_trace:
                        # Always show the final response not collapsed
                        print("\n=== AGENT RESPONSE ===")
                        print(response_text)
                    else:
                        print(f"\nAGENT RESPONSE: {response_text}")

                elif "returnControl" in event:
                    # Handle return of control
                    function_call = event["returnControl"]

                    # Extract function and parameters
                    function_name = function_call["invocationInputs"][0][
                        "functionInvocationInput"
                    ]["function"]
                    action_group = function_call["invocationInputs"][0][
                        "functionInvocationInput"
                    ]["actionGroup"]

                    # Parameters may be in different formats depending on function
                    try:
                        parameters = {}
                        params_data = function_call["invocationInputs"][0][
                            "functionInvocationInput"
                        ]["parameters"]

                        # Handle parameters according to their structure
                        if isinstance(params_data, list):
                            for param in params_data:
                                if "name" in param and "value" in param:
                                    parameters[param["name"]] = param["value"]
                        else:
                            # Handle any other parameter format if needed
                            print(
                                f"WARNING: Unexpected parameters format: {params_data}"
                            )
                    except Exception as param_error:
                        print(f"Error extracting parameters: {param_error}")
                        parameters = {}

                    # Display function call details in a collapsible section
                    function_call_info = {
                        "invocationId": function_call["invocationId"],
                        "actionGroup": action_group,
                        "function": function_name,
                        "parameters": parameters,
                    }
                    function_call_str = json.dumps(
                        function_call_info, indent=2, cls=DateTimeEncoder
                    )
                    display(
                        create_collapsible(
                            "TOOL CALL", function_call_str, open_by_default=True
                        )
                    )

                    # Execute the appropriate SQLite helper or file helper function
                    if function_name == "list_tables":
                        result = list_tables()
                    elif function_name == "describe_table_schema":
                        table_name = parameters.get("table_name")
                        result = describe_table_schema(table_name=table_name)
                    elif function_name == "get_sample_rows":
                        table_name = parameters.get("table_name")
                        result = get_sample_rows(table_name=table_name)
                        # Convert DataFrame to JSON for proper serialization
                        if isinstance(result, pd.DataFrame):
                            result = result.to_dict(orient="records")
                    elif function_name == "run_sql_query":
                        query = parameters.get("query")
                        result = run_sql_query(query=query)
                        # Convert DataFrame to JSON for proper serialization
                        if isinstance(result, pd.DataFrame):
                            result = result.to_dict(orient="records")
                    # File operations
                    elif function_name == "read_file":
                        file_path = parameters.get("file_path")
                        result = read_file(file_path=file_path)
                    elif function_name == "write_file":
                        file_path = parameters.get("file_path")
                        content = parameters.get("content")
                        result = write_file(file_path=file_path, content=content)
                    elif function_name == "list_files":
                        directory_path = parameters.get(
                            "directory_path", ""
                        )  # Default to root if not provided
                        result = list_files(directory_path=directory_path)
                    else:
                        result = {"error": f"Unknown function: {function_name}"}
                        logging.warning(result)

                    # Convert result to string for the agent
                    if isinstance(result, (dict, list)):
                        result_str = json.dumps(result, indent=2, cls=DateTimeEncoder)
                    else:
                        result_str = str(result)

                    # Display function result in a collapsible section
                    result_type = type(result).__name__
                    display(
                        create_collapsible(
                            f"TOOL RESULT ({result_type})",
                            result_str,
                            open_by_default=True,
                        )
                    )

                    # Continue the conversation with the function result
                    continue_response = bedrock_agent_runtime_client.invoke_agent(
                        agentId=agent_id,
                        agentAliasId="TSTALIASID",
                        sessionId=session_id,
                        sessionState={
                            "invocationId": function_call["invocationId"],
                            "returnControlInvocationResults": [
                                {
                                    "functionResult": {
                                        "actionGroup": action_group,
                                        "function": function_name,
                                        "responseBody": {"TEXT": {"body": result_str}},
                                    }
                                }
                            ],
                        },
                        enableTrace=enable_trace,
                    )

                    # Recursively process the continuation response
                    return process_agent_response(continue_response)

                elif "trace" in event and enable_trace:
                    trace_count += 1
                    trace_str = json.dumps(
                        event["trace"], indent=2, cls=DateTimeEncoder
                    )

                    # Extract trace type for a more descriptive header
                    trace_type = "GENERIC"

                    # Inspect the trace structure
                    if "trace" in event["trace"]:
                        orch_trace = event["trace"]["trace"]["orchestrationTrace"]

                        # Look for specific keys that indicate the trace type
                        if "modelInvocationInput" in orch_trace:
                            trace_type = "MODEL INPUT"
                        elif "modelInvocationOutput" in orch_trace:
                            trace_type = "MODEL OUTPUT"
                            # # Add more detailed info from tokens if available
                            # if 'metadata' in orch_trace['modelInvocationOutput'] and 'usage' in orch_trace['modelInvocationOutput']['metadata']:
                            #     usage = orch_trace['modelInvocationOutput']['metadata']['usage']
                            #     if 'inputTokens' in usage and 'outputTokens' in usage:
                            #         trace_type = f"MODEL OUTPUT (In: {usage['inputTokens']}, Out: {usage['outputTokens']} tokens)"
                            #         trace_type = "MODEL OUTPUT"
                        elif "rationale" in orch_trace:
                            trace_type = "AGENT THOUGHT"
                        elif "observation" in orch_trace:
                            trace_type = "FINAL RESPONSE"

                    if trace_type not in ["GENERIC", "MODEL INPUT", "MODEL OUTPUT"]:
                        # Create collapsible section for this trace event
                        display(
                            create_collapsible(
                                f"TRACE {trace_count}: {trace_type}", trace_str
                            )
                        )

            return response_text

        except Exception as e:
            print(f"\nERROR in process_agent_response: {e}")
            return f"Error processing agent response: {str(e)}"

    # Start the initial invocation
    try:
        initial_response = bedrock_agent_runtime_client.invoke_agent(
            inputText=prompt,
            agentId=agent_id,
            agentAliasId="TSTALIASID",
            sessionId=session_id,
            enableTrace=enable_trace,
        )

        # Process the response recursively
        return process_agent_response(initial_response)

    except Exception as e:
        print(f"\nERROR in invoke_agent_with_tools: {e}")
        return f"Error invoking agent: {str(e)}"
