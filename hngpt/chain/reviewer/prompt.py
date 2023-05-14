import datetime
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from pydantic import BaseModel, Field
from typing import List

ITEMS_I_AM_INTERESTED_IN = [
    "Python",
    "Lisp",
    "Deep learning",
    "Machine learning",
    "Large language models",
    "Prompt",
    "Natural language processing",
    "Productivity",
    "Zettelkasten",
    "Writing and thinking",
    "Paul Graham",
    "Martin Fowler",
    "Computer science",
    "Math, especially linear algebra, statistics and information geometry",
    "Web application frameworks",
    "Software architecture",
]

ITEMS_I_AM_NOT_INTERESTED_IN = [
    "Visual Basic",
]


def format_items_in_bullet(items: List[str]) -> str:
    return "\n".join([f"- {item}" for item in items])


class Review(BaseModel):

    score: int = Field(description="degree of interest")
    reason: str = Field(description="reason for the score")


output_parser = PydanticOutputParser(pydantic_object=Review)

system_prompt = SystemMessagePromptTemplate.from_template("You are a helpful assistant.")

human_template = """Read a story in Hacker news and decide if this interests me. I am interested in the latest technical articles. In particular, I am interested in the following technical areas:

My technical areas of interest:
{items_i_am_interested_in}

Technical areas that do not interest me:
{items_i_am_not_interested_in}

Score my interest in the following story from Hacker News on a scale of 1 to 5. Please score my interest based on the following criteria

- The story is about a technical area that interests me
- The story is not about a technical area that does not interest me
- Hacker news score, if the story is about a technical area that interests me, the higher the Hacker news score, the higher the level of interest.
- Date of the story, if the story is about a technical area that interests me, the more recent it is (closer to today ({date})), the higher the level of interest

The story:

```
{story}
```
{format_instructions}"""
human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template=human_template,
        input_variables=["story"],
        partial_variables={
            "items_i_am_interested_in": format_items_in_bullet(ITEMS_I_AM_INTERESTED_IN),
            "items_i_am_not_interested_in": format_items_in_bullet(ITEMS_I_AM_NOT_INTERESTED_IN),
            "format_instructions": output_parser.get_format_instructions(),
            "date": datetime.datetime.now().strftime("%Y/%m/%d")
        }
    )
)

PROMPT = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
