import re
import json
from functools import wraps
from typing import Type

from pydantic import BaseModel, create_model, ValidationError

PYDANTIC_FORMAT_INSTRUCTIONS = """The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output schema:
```
{schema}
```"""


class Instructor(BaseModel):
    @classmethod
    def from_response(cls, response: str) -> "Instructor":
        try:
            # Greedy search for 1st json candidate.
            match = re.search(
                r"\{.*\}", response.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
            )
            json_str = ""
            if match:
                json_str = match.group()
            # json_object = json.loads(json_str, strict=False)
            return cls.model_validate_json(json_str)  # type: ignore

        except (json.JSONDecodeError, ValidationError) as e:
            name = cls.__name__
            msg = f"Failed to parse {name} from completion {response}. Got: {e}"
            raise Exception(msg)

    @classmethod
    def get_format_instructions(cls) -> str:
        schema = cls.model_json_schema()  # type: ignore

        # Remove extraneous fields.
        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]
        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema)

        return PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=schema_str)

    @classmethod
    def from_BaseModel(cls, cls1) -> Type["Instructor"]:
        if not issubclass(cls1, BaseModel):
            raise TypeError("Class must be a subclass of pydantic.BaseModel")

        return wraps(cls1, updated=())(
            create_model(
                cls1.__name__,
                __base__=(cls1, Instructor),  # type: ignore
            )
        )
