# Google Gen AI SDK

[![PyPI version](https://img.shields.io/pypi/v/google-genai.svg)](https://pypi.org/project/google-genai/)
![Python support](https://img.shields.io/pypi/pyversions/google-genai)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/google-genai)](https://pypistats.org/packages/google-genai)

--------
**Documentation:** https://googleapis.github.io/python-genai/

-----

Google Gen AI Python SDK provides an interface for developers to integrate
Google's generative models into their Python applications. It supports the
[Gemini Developer API](https://ai.google.dev/gemini-api/docs) and
[Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/overview)
APIs.

## Installation

```sh
pip install google-genai
```

## Imports

```python
from google import genai
from google.genai import types
```

## Create a client

Please run one of the following code blocks to create a client for
different services ([Gemini Developer API](https://ai.google.dev/gemini-api/docs) or [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/overview)).

```python
from google import genai

# Only run this block for Gemini Developer API
client = genai.Client(api_key='GEMINI_API_KEY')
```

```python
from google import genai

# Only run this block for Vertex AI API
client = genai.Client(
    vertexai=True, project='your-project-id', location='us-central1'
)
```

**(Optional) Using environment variables:**

You can create a client by configuring the necessary environment variables.
Configuration setup instructions depends on whether you're using the Gemini
Developer API or the Gemini API in Vertex AI.

**Gemini Developer API:** Set the `GEMINI_API_KEY` or `GOOGLE_API_KEY`.
It will automatically be picked up by the client. It's recommended that you
set only one of those variables, but if both are set, `GOOGLE_API_KEY` takes
precedence.

```bash
export GEMINI_API_KEY='your-api-key'
```

**Gemini API on Vertex AI:** Set `GOOGLE_GENAI_USE_VERTEXAI`,
`GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`, as shown below:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='us-central1'
```

```python
from google import genai

client = genai.Client()
```

### API Selection

By default, the SDK uses the beta API endpoints provided by Google to support
preview features in the APIs. The stable API endpoints can be selected by
setting the API version to `v1`.

To set the API version use `http_options`. For example, to set the API version
to `v1` for Vertex AI:

```python
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1',
    http_options=types.HttpOptions(api_version='v1')
)
```

To set the API version to `v1alpha` for the Gemini Developer API:

```python
from google import genai
from google.genai import types

client = genai.Client(
    api_key='GEMINI_API_KEY',
    http_options=types.HttpOptions(api_version='v1alpha')
)
```

### Faster async client option: Aiohttp

By default we use httpx for both sync and async client implementations. In order
to have faster performance, you may install `google-genai[aiohttp]`. In Gen AI
SDK we configure `trust_env=True` to match with the default behavior of httpx.
Additional args of `aiohttp.ClientSession.request()` ([see _RequestOptions args](https://github.com/aio-libs/aiohttp/blob/v3.12.13/aiohttp/client.py#L170)) can be passed
through the following way:

```python

http_options = types.HttpOptions(
    async_client_args={'cookies': ..., 'ssl': ...},
)

client=Client(..., http_options=http_options)
```

### Proxy

Both httpx and aiohttp libraries use `urllib.request.getproxies` from
environment variables. Before client initialization, you may set proxy (and
optional SSL_CERT_FILE) by setting the environment variables:


```bash
export HTTPS_PROXY='http://username:password@proxy_uri:port'
export SSL_CERT_FILE='client.pem'
```

If you need `socks5` proxy, httpx [supports](https://www.python-httpx.org/advanced/proxies/#socks) `socks5` proxy if you pass it via
args to `httpx.Client()`. You may install `httpx[socks]` to use it.
Then, you can pass it through the following way:

```python

http_options = types.HttpOptions(
    client_args={'proxy': 'socks5://user:pass@host:port'},
    async_client_args={'proxy': 'socks5://user:pass@host:port'},,
)

client=Client(..., http_options=http_options)
```

## Types

Parameter types can be specified as either dictionaries(`TypedDict`) or
[Pydantic Models](https://pydantic.readthedocs.io/en/stable/model.html).
Pydantic model types are available in the `types` module.

## Models

The `client.models` module exposes model inferencing and model getters.
See the 'Create a client' section above to initialize a client.

### Generate Content

#### with text content

```python
response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents='Why is the sky blue?'
)
print(response.text)
```

#### with uploaded file (Gemini Developer API only)
download the file in console.

```sh
!wget -q https://storage.googleapis.com/generativeai-downloads/data/a11.txt
```

python code.

```python
file = client.files.upload(file='a11.txt')
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=['Could you summarize this file?', file]
)
print(response.text)
```

#### How to structure `contents` argument for `generate_content`
The SDK always converts the inputs to the `contents` argument into
`list[types.Content]`.
The following shows some common ways to provide your inputs.

##### Provide a `list[types.Content]`
This is the canonical way to provide contents, SDK will not do any conversion.

##### Provide a `types.Content` instance

```python
from google.genai import types

contents = types.Content(
  role='user',
  parts=[types.Part.from_text(text='Why is the sky blue?')]
)
```

SDK converts this to

```python
[
  types.Content(
    role='user',
    parts=[types.Part.from_text(text='Why is the sky blue?')]
  )
]
```

##### Provide a string

```python
contents='Why is the sky blue?'
```

The SDK will assume this is a text part, and it converts this into the following:

```python
[
  types.UserContent(
    parts=[
      types.Part.from_text(text='Why is the sky blue?')
    ]
  )
]
```

Where a `types.UserContent` is a subclass of `types.Content`, it sets the
`role` field to be `user`.

##### Provide a list of string

```python
contents=['Why is the sky blue?', 'Why is the cloud white?']
```

The SDK assumes these are 2 text parts, it converts this into a single content,
like the following:

```python
[
  types.UserContent(
    parts=[
      types.Part.from_text(text='Why is the sky blue?'),
      types.Part.from_text(text='Why is the cloud white?'),
    ]
  )
]
```

Where a `types.UserContent` is a subclass of `types.Content`, the
`role` field in `types.UserContent` is fixed to be `user`.

##### Provide a function call part

```python
from google.genai import types

contents = types.Part.from_function_call(
  name='get_weather_by_location',
  args={'location': 'Boston'}
)
```

The SDK converts a function call part to a content with a `model` role:

```python
[
  types.ModelContent(
    parts=[
      types.Part.from_function_call(
        name='get_weather_by_location',
        args={'location': 'Boston'}
      )
    ]
  )
]
```

Where a `types.ModelContent` is a subclass of `types.Content`, the
`role` field in `types.ModelContent` is fixed to be `model`.

##### Provide a list of function call parts

```python
from google.genai import types

contents = [
  types.Part.from_function_call(
    name='get_weather_by_location',
    args={'location': 'Boston'}
  ),
  types.Part.from_function_call(
    name='get_weather_by_location',
    args={'location': 'New York'}
  ),
]
```

The SDK converts a list of function call parts to the a content with a `model` role:

```python
[
  types.ModelContent(
    parts=[
      types.Part.from_function_call(
        name='get_weather_by_location',
        args={'location': 'Boston'}
      ),
      types.Part.from_function_call(
        name='get_weather_by_location',
        args={'location': 'New York'}
      )
    ]
  )
]
```

Where a `types.ModelContent` is a subclass of `types.Content`, the
`role` field in `types.ModelContent` is fixed to be `model`.

##### Provide a non function call part

```python
from google.genai import types

contents = types.Part.from_uri(
  file_uri: 'gs://generativeai-downloads/images/scones.jpg',
  mime_type: 'image/jpeg',
)
```

The SDK converts all non function call parts into a content with a `user` role.

```python
[
  types.UserContent(parts=[
    types.Part.from_uri(
     file_uri: 'gs://generativeai-downloads/images/scones.jpg',
      mime_type: 'image/jpeg',
    )
  ])
]
```

##### Provide a list of non function call parts

```python
from google.genai import types

contents = [
  types.Part.from_text('What is this image about?'),
  types.Part.from_uri(
    file_uri: 'gs://generativeai-downloads/images/scones.jpg',
    mime_type: 'image/jpeg',
  )
]
```

The SDK will convert the list of parts into a content with a `user` role

```python
[
  types.UserContent(
    parts=[
      types.Part.from_text('What is this image about?'),
      types.Part.from_uri(
        file_uri: 'gs://generativeai-downloads/images/scones.jpg',
        mime_type: 'image/jpeg',
      )
    ]
  )
]
```

##### Mix types in contents

You can also provide a list of `types.ContentUnion`. The SDK leaves items of
`types.Content` as is, it groups consecutive non function call parts into a
single `types.UserContent`, and it groups consecutive function call parts into
a single `types.ModelContent`.

If you put a list within a list, the inner list can only contain
`types.PartUnion` items. The SDK will convert the inner list into a single
`types.UserContent`.

### System Instructions and Other Configs

The output of the model can be influenced by several optional settings
available in generate_content's config parameter. For example, increasing
`max_output_tokens` is essential for longer model responses. To make a model more
deterministic, lowering the `temperature` parameter reduces randomness, with
values near 0 minimizing variability. Capabilities and parameter defaults for
each model is shown in the
[Vertex AI docs](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash)
and [Gemini API docs](https://ai.google.dev/gemini-api/docs/models) respectively.

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        max_output_tokens=3,
        temperature=0.3,
    ),
)
print(response.text)
```

### Typed Config

All API methods support Pydantic types for parameters as well as
dictionaries. You can get the type from `google.genai.types`.

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=types.Part.from_text(text='Why is the sky blue?'),
    config=types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        top_k=20,
        candidate_count=1,
        seed=5,
        max_output_tokens=100,
        stop_sequences=['STOP!'],
        presence_penalty=0.0,
        frequency_penalty=0.0,
    ),
)

print(response.text)
```

### List Base Models

To retrieve tuned models, see [list tuned models](#list-tuned-models).

```python
for model in client.models.list():
    print(model)
```

```python
pager = client.models.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### List Base Models (Asynchronous)

```python
async for job in await client.aio.models.list():
    print(job)
```

```python
async_pager = await client.aio.models.list(config={'page_size': 10})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

### Safety Settings

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Say something bad.',
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category='HARM_CATEGORY_HATE_SPEECH',
                threshold='BLOCK_ONLY_HIGH',
            )
        ]
    ),
)
print(response.text)
```

### Function Calling

#### Automatic Python function Support

You can pass a Python function directly and it will be automatically
called and responded by default.

```python
from google.genai import types

def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
      location: The city and state, e.g. San Francisco, CA
    """
    return 'sunny'


response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)

print(response.text)
```
#### Disabling automatic function calling
If you pass in a python function as a tool directly, and do not want
automatic function calling, you can disable automatic function calling
as follows:

```python
from google.genai import types

response = client.models.generate_content(
  model='gemini-2.0-flash-001',
  contents='What is the weather like in Boston?',
  config=types.GenerateContentConfig(
    tools=[get_current_weather],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
      disable=True
    ),
  ),
)
```

With automatic function calling disabled, you will get a list of function call
parts in the response:

```python
function_calls: Optional[List[types.FunctionCall]] = response.function_calls
```

#### Manually declare and invoke a function for function calling

If you don't want to use the automatic function support, you can manually
declare the function and invoke it.

The following example shows how to declare a function and pass it as a tool.
Then you will receive a function call part in the response.

```python
from google.genai import types

function = types.FunctionDeclaration(
    name='get_current_weather',
    description='Get the current weather in a given location',
    parameters_json_schema={
        'type': 'object',
        'properties': {
            'location': {
                'type': 'string',
                'description': 'The city and state, e.g. San Francisco, CA',
            }
        },
        'required': ['location'],
    },
)

tool = types.Tool(function_declarations=[function])

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[tool]),
)

print(response.function_calls[0])
```

After you receive the function call part from the model, you can invoke the function
and get the function response. And then you can pass the function response to
the model.
The following example shows how to do it for a simple function invocation.

```python
from google.genai import types

user_prompt_content = types.Content(
    role='user',
    parts=[types.Part.from_text(text='What is the weather like in Boston?')],
)
function_call_part = response.function_calls[0]
function_call_content = response.candidates[0].content


try:
    function_result = get_current_weather(
        **function_call_part.function_call.args
    )
    function_response = {'result': function_result}
except (
    Exception
) as e:  # instead of raising the exception, you can let the model handle it
    function_response = {'error': str(e)}


function_response_part = types.Part.from_function_response(
    name=function_call_part.name,
    response=function_response,
)
function_response_content = types.Content(
    role='tool', parts=[function_response_part]
)

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=[
        user_prompt_content,
        function_call_content,
        function_response_content,
    ],
    config=types.GenerateContentConfig(
        tools=[tool],
    ),
)

print(response.text)
```

#### Function calling with `ANY` tools config mode

If you configure function calling mode to be `ANY`, then the model will always
return function call parts. If you also pass a python function as a tool, by
default the SDK will perform automatic function calling until the remote calls exceed the
maximum remote call for automatic function calling (default to 10 times).

If you'd like to disable automatic function calling in `ANY` mode:

```python
from google.genai import types

def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
      location: The city and state, e.g. San Francisco, CA
    """
    return "sunny"

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

If you'd like to set `x` number of automatic function call turns, you can
configure the maximum remote calls to be `x + 1`.
Assuming you prefer `1` turn for automatic function calling.

```python
from google.genai import types

def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
      location: The city and state, e.g. San Francisco, CA
    """
    return "sunny"

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=2
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

#### Model Context Protocol (MCP) support (experimental)

Built-in [MCP](https://modelcontextprotocol.io/introduction) support is an
experimental feature. You can pass a local MCP server as a tool directly.

```python
import os
import asyncio
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

client = genai.Client()

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="npx",  # Executable
    args=["-y", "@philschmid/weather-mcp"],  # MCP Server
    env=None,  # Optional environment variables
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Prompt to get the weather for the current day in London.
            prompt = f"What is the weather in London in {datetime.now().strftime('%Y-%m-%d')}?"

            # Initialize the connection between client and server
            await session.initialize()

            # Send request to the model with MCP function declarations
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[session],  # uses the session, will automatically call the tool using automatic function calling
                ),
            )
            print(response.text)

# Start the asyncio event loop and run the main function
asyncio.run(run())
```

### JSON Response Schema

However you define your schema, don't duplicate it in your input prompt,
including by giving examples of expected JSON output. If you do, the generated
output might be lower in quality.

#### JSON Schema support
Schemas can be provided as standard JSON schema.
```python
user_profile = {
    'properties': {
        'age': {
            'anyOf': [
                {'maximum': 20, 'minimum': 0, 'type': 'integer'},
                {'type': 'null'},
            ],
            'title': 'Age',
        },
        'username': {
            'description': "User's unique name",
            'title': 'Username',
            'type': 'string',
        },
    },
    'required': ['username', 'age'],
    'title': 'User Schema',
    'type': 'object',
}

response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Give me information of the United States.',
    config={
        'response_mime_type': 'application/json',
        'response_json_schema': userProfile
    },
)
print(response.parsed)
```

#### Pydantic Model Schema support

Schemas can be provided as Pydantic Models.

```python
from pydantic import BaseModel
from google.genai import types


class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int


response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=CountryInfo,
    ),
)
print(response.text)
```

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema={
            'required': [
                'name',
                'population',
                'capital',
                'continent',
                'gdp',
                'official_language',
                'total_area_sq_mi',
            ],
            'properties': {
                'name': {'type': 'STRING'},
                'population': {'type': 'INTEGER'},
                'capital': {'type': 'STRING'},
                'continent': {'type': 'STRING'},
                'gdp': {'type': 'INTEGER'},
                'official_language': {'type': 'STRING'},
                'total_area_sq_mi': {'type': 'INTEGER'},
            },
            'type': 'OBJECT',
        },
    ),
)
print(response.text)
```

### Enum Response Schema

#### Text Response

You can set response_mime_type to 'text/x.enum' to return one of those enum
values as the response.

```python
class InstrumentEnum(Enum):
  PERCUSSION = 'Percussion'
  STRING = 'String'
  WOODWIND = 'Woodwind'
  BRASS = 'Brass'
  KEYBOARD = 'Keyboard'

response = client.models.generate_content(
      model='gemini-2.0-flash-001',
      contents='What instrument plays multiple notes at once?',
      config={
          'response_mime_type': 'text/x.enum',
          'response_schema': InstrumentEnum,
      },
  )
print(response.text)
```

#### JSON Response

You can also set response_mime_type to 'application/json', the response will be
identical but in quotes.

```python
from enum import Enum

class InstrumentEnum(Enum):
  PERCUSSION = 'Percussion'
  STRING = 'String'
  WOODWIND = 'Woodwind'
  BRASS = 'Brass'
  KEYBOARD = 'Keyboard'

response = client.models.generate_content(
      model='gemini-2.0-flash-001',
      contents='What instrument plays multiple notes at once?',
      config={
          'response_mime_type': 'application/json',
          'response_schema': InstrumentEnum,
      },
  )
print(response.text)
```

### Generate Content (Synchronous Streaming)

Generate content in a streaming format so that the model outputs streams back
to you, rather than being returned as one chunk.

#### Streaming for text content

```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

#### Streaming for image content

If your image is stored in [Google Cloud Storage](https://cloud.google.com/storage),
you can use the `from_uri` class method to create a `Part` object.

```python
from google.genai import types

for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001',
    contents=[
        'What is this image about?',
        types.Part.from_uri(
            file_uri='gs://generativeai-downloads/images/scones.jpg',
            mime_type='image/jpeg',
        ),
    ],
):
    print(chunk.text, end='')
```

If your image is stored in your local file system, you can read it in as bytes
data and use the `from_bytes` class method to create a `Part` object.

```python
from google.genai import types

YOUR_IMAGE_PATH = 'your_image_path'
YOUR_IMAGE_MIME_TYPE = 'your_image_mime_type'
with open(YOUR_IMAGE_PATH, 'rb') as f:
    image_bytes = f.read()

for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001',
    contents=[
        'What is this image about?',
        types.Part.from_bytes(data=image_bytes, mime_type=YOUR_IMAGE_MIME_TYPE),
    ],
):
    print(chunk.text, end='')
```

### Generate Content (Asynchronous Non Streaming)

`client.aio` exposes all the analogous [`async` methods](https://docs.python.org/3/library/asyncio.html)
that are available on `client`. Note that it applies to all the modules.

For example, `client.aio.models.generate_content` is the `async` version
of `client.models.generate_content`

```python
response = await client.aio.models.generate_content(
    model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
)

print(response.text)
```

### Generate Content (Asynchronous Streaming)


```python
async for chunk in await client.aio.models.generate_content_stream(
    model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### Count Tokens and Compute Tokens

```python
response = client.models.count_tokens(
    model='gemini-2.0-flash-001',
    contents='why is the sky blue?',
)
print(response)
```

#### Compute Tokens

Compute tokens is only supported in Vertex AI.

```python
response = client.models.compute_tokens(
    model='gemini-2.0-flash-001',
    contents='why is the sky blue?',
)
print(response)
```

##### Async

```python
response = await client.aio.models.count_tokens(
    model='gemini-2.0-flash-001',
    contents='why is the sky blue?',
)
print(response)
```

### Embed Content

```python
response = client.models.embed_content(
    model='text-embedding-004',
    contents='why is the sky blue?',
)
print(response)
```

```python
from google.genai import types

# multiple contents with config
response = client.models.embed_content(
    model='text-embedding-004',
    contents=['why is the sky blue?', 'What is your age?'],
    config=types.EmbedContentConfig(output_dimensionality=10),
)

print(response)
```

### Imagen

#### Generate Images

Support for generate images in Gemini Developer API is behind an allowlist

```python
from google.genai import types

# Generate Image
response1 = client.models.generate_images(
    model='imagen-3.0-generate-002',
    prompt='An umbrella in the foreground, and a rainy night sky in the background',
    config=types.GenerateImagesConfig(
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response1.generated_images[0].image.show()
```

#### Upscale Image

Upscale image is only supported in Vertex AI.

```python
from google.genai import types

# Upscale the generated image from above
response2 = client.models.upscale_image(
    model='imagen-3.0-generate-001',
    image=response1.generated_images[0].image,
    upscale_factor='x2',
    config=types.UpscaleImageConfig(
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response2.generated_images[0].image.show()
```

#### Edit Image

Edit image uses a separate model from generate and upscale.

Edit image is only supported in Vertex AI.

```python
# Edit the generated image from above
from google.genai import types
from google.genai.types import RawReferenceImage, MaskReferenceImage

raw_ref_image = RawReferenceImage(
    reference_id=1,
    reference_image=response1.generated_images[0].image,
)

# Model computes a mask of the background
mask_ref_image = MaskReferenceImage(
    reference_id=2,
    config=types.MaskReferenceConfig(
        mask_mode='MASK_MODE_BACKGROUND',
        mask_dilation=0,
    ),
)

response3 = client.models.edit_image(
    model='imagen-3.0-capability-001',
    prompt='Sunlight and clear sky',
    reference_images=[raw_ref_image, mask_ref_image],
    config=types.EditImageConfig(
        edit_mode='EDIT_MODE_INPAINT_INSERTION',
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response3.generated_images[0].image.show()
```

### Veo

Support for generating videos is considered public preview

#### Generate Videos (Text to Video)

```python
from google.genai import types

# Create operation
operation = client.models.generate_videos(
    model='veo-2.0-generate-001',
    prompt='A neon hologram of a cat driving at top speed',
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

# Poll operation
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

#### Generate Videos (Image to Video)

```python
from google.genai import types

# Read local image (uses mimetypes.guess_type to infer mime type)
image = types.Image.from_file("local/path/file.png")

# Create operation
operation = client.models.generate_videos(
    model='veo-2.0-generate-001',
    # Prompt is optional if image is provided
    prompt='Night sky',
    image=image,
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
        # Can also pass an Image into last_frame for frame interpolation
    ),
)

# Poll operation
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

#### Generate Videos (Video to Video)

Currently, only Vertex supports Video to Video generation (Video extension).

```python
from google.genai import types

# Read local video (uses mimetypes.guess_type to infer mime type)
video = types.Video.from_file("local/path/video.mp4")

# Create operation
operation = client.models.generate_videos(
    model='veo-2.0-generate-001',
    # Prompt is optional if Video is provided
    prompt='Night sky',
    # Input video must be in GCS
    video=types.Video(
        uri="gs://bucket-name/inputs/videos/cat_driving.mp4",
    ),
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

# Poll operation
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

## Chats

Create a chat session to start a multi-turn conversations with the model. Then,
use `chat.send_message` function multiple times within the same chat session so
that it can reflect on its previous responses (i.e., engage in an ongoing
 conversation). See the 'Create a client' section above to initialize a client.

### Send Message (Synchronous Non-Streaming)

```python
chat = client.chats.create(model='gemini-2.0-flash-001')
response = chat.send_message('tell me a story')
print(response.text)
response = chat.send_message('summarize the story you told me in 1 sentence')
print(response.text)
```

### Send Message (Synchronous Streaming)

```python
chat = client.chats.create(model='gemini-2.0-flash-001')
for chunk in chat.send_message_stream('tell me a story'):
    print(chunk.text)
```

### Send Message (Asynchronous Non-Streaming)

```python
chat = client.aio.chats.create(model='gemini-2.0-flash-001')
response = await chat.send_message('tell me a story')
print(response.text)
```

### Send Message (Asynchronous Streaming)

```python
chat = client.aio.chats.create(model='gemini-2.0-flash-001')
async for chunk in await chat.send_message_stream('tell me a story'):
    print(chunk.text)
```

## Files

Files are only supported in Gemini Developer API. See the 'Create a client'
section above to initialize a client.

```cmd
!gsutil cp gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf .
!gsutil cp gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf .
```

### Upload

```python
file1 = client.files.upload(file='2312.11805v3.pdf')
file2 = client.files.upload(file='2403.05530.pdf')

print(file1)
print(file2)
```

### Get

```python
file1 = client.files.upload(file='2312.11805v3.pdf')
file_info = client.files.get(name=file1.name)
```

### Delete

```python
file3 = client.files.upload(file='2312.11805v3.pdf')

client.files.delete(name=file3.name)
```

## Caches

`client.caches` contains the control plane APIs for cached content. See the
'Create a client' section above to initialize a client.

### Create

```python
from google.genai import types

if client.vertexai:
    file_uris = [
        'gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf',
        'gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf',
    ]
else:
    file_uris = [file1.uri, file2.uri]

cached_content = client.caches.create(
    model='gemini-2.0-flash-001',
    config=types.CreateCachedContentConfig(
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_uri(
                        file_uri=file_uris[0], mime_type='application/pdf'
                    ),
                    types.Part.from_uri(
                        file_uri=file_uris[1],
                        mime_type='application/pdf',
                    ),
                ],
            )
        ],
        system_instruction='What is the sum of the two pdfs?',
        display_name='test cache',
        ttl='3600s',
    ),
)
```

### Get

```python
cached_content = client.caches.get(name=cached_content.name)
```

### Generate Content with Caches

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Summarize the pdfs',
    config=types.GenerateContentConfig(
        cached_content=cached_content.name,
    ),
)
print(response.text)
```

## Tunings

`client.tunings` contains tuning job APIs and supports supervised fine
tuning through `tune`. Only supported in Vertex AI. See the 'Create a client'
section above to initialize a client.

### Tune

-   Vertex AI supports tuning from GCS source or from a Vertex Multimodal Dataset

```python
from google.genai import types

model = 'gemini-2.0-flash-001'
training_dataset = types.TuningDataset(
  # or gcs_uri=my_vertex_multimodal_dataset
    gcs_uri='gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl',
)
```

```python
from google.genai import types

tuning_job = client.tunings.tune(
    base_model=model,
    training_dataset=training_dataset,
    config=types.CreateTuningJobConfig(
        epoch_count=1, tuned_model_display_name='test_dataset_examples model'
    ),
)
print(tuning_job)
```

### Get Tuning Job

```python
tuning_job = client.tunings.get(name=tuning_job.name)
print(tuning_job)
```

```python
import time

completed_states = set(
    [
        'JOB_STATE_SUCCEEDED',
        'JOB_STATE_FAILED',
        'JOB_STATE_CANCELLED',
    ]
)

while tuning_job.state not in completed_states:
    print(tuning_job.state)
    tuning_job = client.tunings.get(name=tuning_job.name)
    time.sleep(10)
```

#### Use Tuned Model

```python
response = client.models.generate_content(
    model=tuning_job.tuned_model.endpoint,
    contents='why is the sky blue?',
)

print(response.text)
```

### Get Tuned Model

```python
tuned_model = client.models.get(model=tuning_job.tuned_model.model)
print(tuned_model)
```

### List Tuned Models

To retrieve base models, see [list base models](#list-base-models).

```python
for model in client.models.list(config={'page_size': 10, 'query_base': False}):
    print(model)
```

```python
pager = client.models.list(config={'page_size': 10, 'query_base': False})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### Async

```python
async for job in await client.aio.models.list(config={'page_size': 10, 'query_base': False}):
    print(job)
```

```python
async_pager = await client.aio.models.list(config={'page_size': 10, 'query_base': False})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

### Update Tuned Model

```python
from google.genai import types

model = pager[0]

model = client.models.update(
    model=model.name,
    config=types.UpdateModelConfig(
        display_name='my tuned model', description='my tuned model description'
    ),
)

print(model)
```


### List Tuning Jobs

```python
for job in client.tunings.list(config={'page_size': 10}):
    print(job)
```

```python
pager = client.tunings.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### Async

```python
async for job in await client.aio.tunings.list(config={'page_size': 10}):
    print(job)
```

```python
async_pager = await client.aio.tunings.list(config={'page_size': 10})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

## Batch Prediction

Only supported in Vertex AI. See the 'Create a client' section above to
initialize a client.

### Create

Vertex AI:

```python
# Specify model and source file only, destination and job display name will be auto-populated
job = client.batches.create(
    model='gemini-2.0-flash-001',
    src='bq://my-project.my-dataset.my-table',  # or "gs://path/to/input/data"
)

job
```

Gemini Developer API:

```python
# Create a batch job with inlined requests
batch_job = client.batches.create(
    model="gemini-2.0-flash",
    src=[{
      "contents": [{
        "parts": [{
          "text": "Hello!",
        }],
       "role": "user",
     }],
     "config:": {"response_modalities": ["text"]},
    }],
)

job
```

In order to create a batch job with file name. Need to upload a jsonl file.
For example myrequests.json:

```
{"key":"request_1", "request": {"contents": [{"parts": [{"text":
 "Explain how AI works in a few words"}]}], "generation_config": {"response_modalities": ["TEXT"]}}}
{"key":"request_2", "request": {"contents": [{"parts": [{"text": "Explain how Crypto works in a few words"}]}]}}
```
Then upload the file.

```python
# Upload the file
file = client.files.upload(
    file='myrequest.json',
    config=types.UploadFileConfig(display_name='test_json')
)

# Create a batch job with file name
batch_job = client.batches.create(
    model="gemini-2.0-flash",
    src="files/file_name",
)
```


```python
# Get a job by name
job = client.batches.get(name=job.name)

job.state
```

```python
completed_states = set(
    [
        'JOB_STATE_SUCCEEDED',
        'JOB_STATE_FAILED',
        'JOB_STATE_CANCELLED',
        'JOB_STATE_PAUSED',
    ]
)

while job.state not in completed_states:
    print(job.state)
    job = client.batches.get(name=job.name)
    time.sleep(30)

job
```

### List

```python
for job in client.batches.list(config=types.ListBatchJobsConfig(page_size=10)):
    print(job)
```

```python
pager = client.batches.list(config=types.ListBatchJobsConfig(page_size=10))
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### Async

```python
async for job in await client.aio.batches.list(
    config=types.ListBatchJobsConfig(page_size=10)
):
    print(job)
```

```python
async_pager = await client.aio.batches.list(
    config=types.ListBatchJobsConfig(page_size=10)
)
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

### Delete

```python
# Delete the job resource
delete_job = client.batches.delete(name=job.name)

delete_job
```

## Error Handling

To handle errors raised by the model service, the SDK provides this [APIError](https://github.com/googleapis/python-genai/blob/main/google/genai/errors.py) class.

```python
from google.genai import errors

try:
  client.models.generate_content(
      model="invalid-model-name",
      contents="What is your name?",
  )
except errors.APIError as e:
  print(e.code) # 404
  print(e.message)
```

## Extra Request Body

The `extra_body` field in `HttpOptions` accepts a dictionary of additional JSON
properties to include in the request body. This can be used to access new or
experimental backend features that are not yet formally supported in the SDK.
The structure of the dictionary must match the backend API's request structure.

- VertexAI backend API docs: https://cloud.google.com/vertex-ai/docs/reference/rest
- GeminiAPI backend API docs: https://ai.google.dev/api/rest

```python
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="What is the weather in Boston? and how about Sunnyvale?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        http_options=types.HttpOptions(extra_body={'tool_config': {'function_calling_config': {'mode': 'COMPOSITIONAL'}}}),
    ),
)
```
