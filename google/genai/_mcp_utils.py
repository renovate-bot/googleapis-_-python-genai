# Copyright 2025 Google LLC
#
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
#

"""Utils for working with MCP tools."""

from importlib.metadata import PackageNotFoundError, version
import typing
from typing import Any

from . import _common
from . import types

if typing.TYPE_CHECKING:
  from mcp.types import Tool as McpTool
  from mcp import ClientSession as McpClientSession
else:
  McpClientSession: typing.Type = Any
  McpTool: typing.Type = Any
  try:
    from mcp.types import Tool as McpTool
    from mcp import ClientSession as McpClientSession
  except ImportError:
    McpTool = None
    McpClientSession = None


def mcp_to_gemini_tool(tool: McpTool) -> types.Tool:
  """Translates an MCP tool to a Google GenAI tool."""
  return types.Tool(
      function_declarations=[{
          "name": tool.name,
          "description": tool.description,
          "parameters": types.Schema.from_json_schema(
              json_schema=types.JSONSchema(
                  **_filter_to_supported_schema(tool.inputSchema)
              )
          ),
      }]
  )


def mcp_to_gemini_tools(tools: list[McpTool]) -> list[types.Tool]:
  """Translates a list of MCP tools to a list of Google GenAI tools."""
  return [mcp_to_gemini_tool(tool) for tool in tools]


def has_mcp_tool_usage(tools: types.ToolListUnion) -> bool:
  """Checks whether the list of tools contains any MCP tools or sessions."""
  if McpClientSession is None:
    return False
  for tool in tools:
    if isinstance(tool, McpTool) or isinstance(tool, McpClientSession):
      return True
  return False


def has_mcp_session_usage(tools: types.ToolListUnion) -> bool:
  """Checks whether the list of tools contains any MCP sessions."""
  if McpClientSession is None:
    return False
  for tool in tools:
    if isinstance(tool, McpClientSession):
      return True
  return False


def set_mcp_usage_header(headers: dict[str, str]) -> None:
  """Sets the MCP version label in the Google API client header."""
  if McpClientSession is None:
    return
  try:
    version_label = version("mcp")
  except PackageNotFoundError:
    version_label = "0.0.0"
  existing_header = headers.get("x-goog-api-client", "")
  headers["x-goog-api-client"] = (
      existing_header + f" mcp_used/{version_label}"
  ).lstrip()


def _filter_to_supported_schema(
    schema: _common.StringDict,
) -> _common.StringDict:
  """Filters the schema to only include fields that are supported by JSONSchema."""
  supported_fields: set[str] = set(types.JSONSchema.model_fields.keys())
  schema_field_names: tuple[str] = ("items",)  # 'additional_properties' to come
  list_schema_field_names: tuple[str] = (
      "any_of",  # 'one_of', 'all_of', 'not' to come
  )
  dict_schema_field_names: tuple[str] = ("properties",)  # 'defs' to come
  for field_name, field_value in schema.items():
    if field_name in schema_field_names:
      schema[field_name] = _filter_to_supported_schema(field_value)
    elif field_name in list_schema_field_names:
      schema[field_name] = [
          _filter_to_supported_schema(value) for value in field_value
      ]
    elif field_name in dict_schema_field_names:
      schema[field_name] = {
          key: _filter_to_supported_schema(value)
          for key, value in field_value.items()
      }
  return {
      key: value for key, value in schema.items() if key in supported_fields
  }
