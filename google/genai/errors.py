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

"""Error classes for the GenAI SDK."""

from typing import Any, Optional, TYPE_CHECKING, Union
import httpx
import json
from . import _common


if TYPE_CHECKING:
  from .replay_api_client import ReplayResponse
  import aiohttp


class APIError(Exception):
  """General errors raised by the GenAI API."""
  code: int
  response: Union['ReplayResponse', httpx.Response]

  status: Optional[str] = None
  message: Optional[str] = None

  def __init__(
      self,
      code: int,
      response_json: Any,
      response: Optional[
          Union['ReplayResponse', httpx.Response, 'aiohttp.ClientResponse']
      ] = None,
  ):
    self.response = response
    self.details = response_json
    self.message = self._get_message(response_json)
    self.status = self._get_status(response_json)
    self.code = code if code else self._get_code(response_json)

    super().__init__(f'{self.code} {self.status}. {self.details}')

  def _get_status(self, response_json: Any) -> Any:
    return response_json.get(
        'status', response_json.get('error', {}).get('status', None)
    )

  def _get_message(self, response_json: Any) -> Any:
    return response_json.get(
        'message', response_json.get('error', {}).get('message', None)
    )

  def _get_code(self, response_json: Any) -> Any:
    return response_json.get(
        'code', response_json.get('error', {}).get('code', None)
    )

  def _to_replay_record(self) -> _common.StringDict:
    """Returns a dictionary representation of the error for replay recording.

    details is not included since it may expose internal information in the
    replay file.
    """
    return {
        'error': {
            'code': self.code,
            'message': self.message,
            'status': self.status,
        }
    }

  @classmethod
  def raise_for_response(
      cls, response: Union['ReplayResponse', httpx.Response]
  ) -> None:
    """Raises an error with detailed error message if the response has an error status."""
    if response.status_code == 200:
      return

    if isinstance(response, httpx.Response):
      try:
        response.read()
        response_json = response.json()
      except json.decoder.JSONDecodeError:
        message = response.text
        response_json = {
            'message': message,
            'status': response.reason_phrase,
        }
    else:
      response_json = response.body_segments[0].get('error', {})

    status_code = response.status_code
    if 400 <= status_code < 500:
      raise ClientError(status_code, response_json, response)
    elif 500 <= status_code < 600:
      raise ServerError(status_code, response_json, response)
    else:
      raise cls(status_code, response_json, response)

  @classmethod
  async def raise_for_async_response(
      cls,
      response: Union[
          'ReplayResponse', httpx.Response, 'aiohttp.ClientResponse'
      ],
  ) -> None:
    """Raises an error with detailed error message if the response has an error status."""
    status_code = 0
    response_json = None
    if isinstance(response, httpx.Response):
      if response.status_code == 200:
        return
      try:
        await response.aread()
        response_json = response.json()
      except json.decoder.JSONDecodeError:
        message = response.text
        response_json = {
            'message': message,
            'status': response.reason_phrase,
        }
      status_code = response.status_code
    else:
      try:
        import aiohttp  # pylint: disable=g-import-not-at-top

        if isinstance(response, aiohttp.ClientResponse):
          if response.status == 200:
            return
          try:
            response_json = await response.json()
          except aiohttp.client_exceptions.ContentTypeError:
            message = await response.text()
            response_json = {
                'message': message,
                'status': response.reason,
            }
          status_code = response.status
        else:
          response_json = response.body_segments[0].get('error', {})
      except ImportError:
        response_json = response.body_segments[0].get('error', {})

    if 400 <= status_code < 500:
      raise ClientError(status_code, response_json, response)
    elif 500 <= status_code < 600:
      raise ServerError(status_code, response_json, response)
    else:
      raise cls(status_code, response_json, response)


class ClientError(APIError):
  """Client error raised by the GenAI API."""
  pass


class ServerError(APIError):
  """Server error raised by the GenAI API."""
  pass


class UnknownFunctionCallArgumentError(ValueError):
  """Raised when the function call argument cannot be converted to the parameter annotation."""

  pass


class UnsupportedFunctionError(ValueError):
  """Raised when the function is not supported."""


class FunctionInvocationError(ValueError):
  """Raised when the function cannot be invoked with the given arguments."""

  pass


ExperimentalWarning = _common.ExperimentalWarning
