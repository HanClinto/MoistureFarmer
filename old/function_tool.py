# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Modified from CAMEL source code.
#  Original: https://github.com/camel-ai/camel/blob/master/camel/toolkits/function_tool.py
# --- Modifications Copyright 2025 @ HanClinto Games. All Rights Reserved. ---
import warnings
from inspect import Parameter, signature
from typing import Any, Callable, Dict, Mapping, Tuple

from docstring_parser import parse
from jsonschema.exceptions import SchemaError
from jsonschema.validators import Draft202012Validator as JSONValidator
from pydantic import create_model
from pydantic.fields import FieldInfo

def _to_pascal(name: str) -> str:
    r"""Convert a string to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))

def _remove_a_key(d: Dict, remove_key: Any) -> None:
    r"""Remove a key from a dictionary recursively."""
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == remove_key:
                del d[key]
            else:
                _remove_a_key(d[key], remove_key)

def _remove_title_recursively(data, parent_key=None):
    r"""Recursively removes the 'title' key from all levels of a nested
    dictionary, except when 'title' is an argument name in the schema.
    """
    if isinstance(data, dict):
        # Only remove 'title' if it's not an argument name
        if parent_key not in [
            "properties",
            "$defs",
            "items",
            "allOf",
            "oneOf",
            "anyOf",
        ]:
            data.pop("title", None)

        # Recursively process each key-value pair
        for key, value in data.items():
            _remove_title_recursively(value, parent_key=key)
    elif isinstance(data, list):
        # Recursively process each element in the list
        for item in data:
            _remove_title_recursively(item, parent_key=parent_key)


def get_openai_tool_schema(func: Callable) -> Dict[str, Any]:
    r"""Generates an OpenAI JSON schema from a given Python function.

    This function creates a schema compatible with OpenAI's API specifications,
    based on the provided Python function. It processes the function's
    parameters, types, and docstrings, and constructs a schema accordingly.

    Note:
        - Each parameter in `func` must have a type annotation; otherwise, it's
          treated as 'Any'.
        - Variable arguments (*args) and keyword arguments (**kwargs) are not
          supported and will be ignored.
        - A functional description including a brief and detailed explanation
          should be provided in the docstring of `func`.
        - All parameters of `func` must be described in its docstring.
        - Supported docstring styles: ReST, Google, Numpydoc, and Epydoc.

    Args:
        func (Callable): The Python function to be converted into an OpenAI
                         JSON schema.

    Returns:
        Dict[str, Any]: A dictionary representing the OpenAI JSON schema of
                        the provided function.

    See Also:
        `OpenAI API Reference
            <https://platform.openai.com/docs/api-reference/assistants/object>`_
    """
    params: Mapping[str, Parameter] = signature(func).parameters
    fields: Dict[str, Tuple[type, FieldInfo]] = {}
    for param_name, p in params.items():
        param_type = p.annotation
        param_default = p.default
        param_kind = p.kind
        param_annotation = p.annotation
        # Variable parameters are not supported
        if (
            param_kind == Parameter.VAR_POSITIONAL
            or param_kind == Parameter.VAR_KEYWORD
        ):
            continue
        # If the parameter type is not specified, it defaults to typing.Any
        if param_annotation is Parameter.empty:
            param_type = Any
        # Check if the parameter has a default value
        if param_default is Parameter.empty:
            fields[param_name] = (param_type, FieldInfo())
        else:
            fields[param_name] = (param_type, FieldInfo(default=param_default))

    # Applying `create_model()` directly will result in a mypy error,
    # create an alias to avoid this.
    def _create_mol(name, field):
        return create_model(name, **field)

    model = _create_mol(_to_pascal(func.__name__), fields)
    parameters_dict = model.model_json_schema()

    # The `"title"` is generated by `model.model_json_schema()`
    # but is useless for openai json schema, remove generated 'title' from
    # parameters_dict
    _remove_title_recursively(parameters_dict)

    docstring = parse(func.__doc__ or "")
    for param in docstring.params:
        if (name := param.arg_name) in parameters_dict["properties"] and (
            description := param.description
        ):
            parameters_dict["properties"][name]["description"] = description

    short_description = docstring.short_description or ""
    long_description = docstring.long_description or ""
    if long_description:
        func_description = f"{short_description}\n{long_description}"
    else:
        func_description = short_description

    # OpenAI client.beta.chat.completions.parse for structured output has
    # additional requirements for the schema, refer:
    # https://platform.openai.com/docs/guides/structured-outputs/some-type-specific-keywords-are-not-yet-supported#supported-schemas
    parameters_dict["additionalProperties"] = False

    openai_function_schema = {
        "name": func.__name__,
        "description": func_description,
        "strict": True,
        "parameters": parameters_dict,
    }

    openai_tool_schema = {
        "type": "function",
        "function": openai_function_schema,
    }

    openai_tool_schema = sanitize_and_enforce_required(openai_tool_schema)
    return openai_tool_schema


def sanitize_and_enforce_required(parameters_dict: Dict[str, Any]) -> Dict[str, Any]:
    r"""Cleans and updates the function schema to conform with OpenAI's
    requirements:
    - Removes invalid 'default' fields from the parameters schema.
    - Ensures all fields are marked as required or have null type for optional
    fields.
    - Recursively adds additionalProperties: false to all nested objects.

    Args:
        parameters_dict (dict): The dictionary representing the function
            schema.

    Returns:
        dict: The updated dictionary with invalid defaults removed and all
            fields properly configured for strict mode.
    """

    def _add_additional_properties_false(obj):
        r"""Recursively add additionalProperties: false to all objects."""
        if isinstance(obj, dict):
            if (
                obj.get("type") == "object"
                and "additionalProperties" not in obj
            ):
                obj["additionalProperties"] = False

            # Process nested structures
            for key, value in obj.items():
                if key == "properties" and isinstance(value, dict):
                    for prop_value in value.values():
                        _add_additional_properties_false(prop_value)
                elif key in [
                    "items",
                    "allOf",
                    "oneOf",
                    "anyOf",
                ] and isinstance(value, (dict, list)):
                    if isinstance(value, dict):
                        _add_additional_properties_false(value)
                    elif isinstance(value, list):
                        for item in value:
                            _add_additional_properties_false(item)
                elif key == "$defs" and isinstance(value, dict):
                    for def_value in value.values():
                        _add_additional_properties_false(def_value)

    # Check if 'function' and 'parameters' exist
    if (
        'function' in parameters_dict
        and 'parameters' in parameters_dict['function']
    ):
        # Access the 'parameters' section
        parameters = parameters_dict['function']['parameters']
        properties = parameters.get('properties', {})

        # Track which fields should be required vs optional
        required_fields = []

        # Process each property
        for field_name, field_schema in properties.items():
            # Check if this field had a default value (making it optional)
            had_default = 'default' in field_schema

            # Remove 'default' key from field schema as required by OpenAI
            field_schema.pop('default', None)

            if had_default:
                # This field is optional - add null to its type
                current_type = field_schema.get('type')
                has_ref = '$ref' in field_schema
                has_any_of = 'anyOf' in field_schema

                if has_ref:
                    # Fields with $ref shouldn't have additional type field
                    # The $ref itself defines the type structure
                    pass
                elif has_any_of:
                    # Field already has anyOf
                    any_of_types = field_schema['anyOf']
                    has_null_type = any(
                        item.get('type') == 'null' for item in any_of_types
                    )
                    if not has_null_type:
                        # Add null type to anyOf
                        field_schema['anyOf'].append({'type': 'null'})
                    # Remove conflicting type field if it exists
                    if 'type' in field_schema:
                        del field_schema['type']
                elif current_type:
                    if isinstance(current_type, str):
                        # Single type - convert to array with null
                        field_schema['type'] = [current_type, 'null']
                    elif (
                        isinstance(current_type, list)
                        and 'null' not in current_type
                    ):
                        # Array of types - add null if not present
                        field_schema['type'] = [*current_type, 'null']
                else:
                    # No type specified, add null type
                    field_schema['type'] = ['null']

                # Optional fields are still marked as required in strict mode
                # but with null type to indicate they can be omitted
                required_fields.append(field_name)
            else:
                # This field is required
                required_fields.append(field_name)

        # Set all fields as required (strict mode requirement)
        parameters['required'] = required_fields

        # Recursively add additionalProperties: false to all objects
        _add_additional_properties_false(parameters)

    return parameters_dict


def validate_openai_tool_schema(
    openai_tool_schema: Dict[str, Any],
) -> None:
    r"""Validates the OpenAI tool schema against
    :obj:`ToolAssistantToolsFunction`.
    This function checks if the provided :obj:`openai_tool_schema` adheres
    to the specifications required by OpenAI's
    :obj:`ToolAssistantToolsFunction`. It ensures that the function
    description and parameters are correctly formatted according to JSON
    Schema specifications.
    Args:
        openai_tool_schema (Dict[str, Any]): The OpenAI tool schema to
            validate.
    Raises:
        ValidationError: If the schema does not comply with the
            specifications.
        SchemaError: If the parameters do not meet JSON Schema reference
            specifications.
    """
    # Check the type
    if not openai_tool_schema["type"]:
        raise ValueError("miss `type` in tool schema.")

    # Check the function description, if no description then raise warming
    if not openai_tool_schema["function"].get("description"):
        warnings.warn(f"""Function description is missing for 
                        {openai_tool_schema['function']['name']}. This may 
                        affect the quality of tool calling.""")

    # Validate whether parameters
    # meet the JSON Schema reference specifications.
    # See https://platform.openai.com/docs/guides/gpt/function-calling
    # for examples, and the
    # https://json-schema.org/understanding-json-schema/ for
    # documentation about the format.
    parameters = openai_tool_schema["function"]["parameters"]
    try:
        JSONValidator.check_schema(parameters)
    except SchemaError as e:
        raise e

    # Check the parameter description, if no description then raise warming
    properties: Dict[str, Any] = parameters["properties"]
    for param_name in properties.keys():
        param_dict = properties[param_name]
        if "description" not in param_dict:
            warnings.warn(
                f"Parameter description is missing for the "
                f"function '{openai_tool_schema['function']['name']}'. "
                f"The parameter definition is {param_dict}. "
                f"This may affect the quality of tool calling."
            )

