import logging
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.output_parsers import RetryWithErrorOutputParser
from langchain.output_parsers.pydantic import OutputParserException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Any, Dict, List, Optional

from ...hnclient import HackerNewsStory
from .prompt import PROMPT, output_parser

logger = logging.getLogger(__name__)


class ReviewerChain(LLMChain):

    STORY_CHUNK_SIZE = 2_000
    SPLITTER_MODEL_NAME = "gpt-3.5-turbo"

    prompt = PROMPT

    @property
    def input_keys(self) -> List[str]:
        return ["story"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        story = get_story_string(
            inputs["story"],
            self.SPLITTER_MODEL_NAME,
            self.STORY_CHUNK_SIZE
        )
        retry_parser = RetryWithErrorOutputParser.from_llm(parser=output_parser, llm=self.llm)
        output = super()._call({"story": story}, run_manager=run_manager)

        try:
            output = output_parser.parse(output[self.output_key])
        except OutputParserException:
            try:
                output = retry_parser.parse_with_prompt(
                    output[self.output_key],
                    self.prompt.format_prompt(story=story)
                )
            except OutputParserException as e:
                logger.warning(f"Abort {story.title}, {e}.")
                output = ""

        return {self.output_key: output}

    def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        raise NotImplementedError()


def get_story_string(
        story: HackerNewsStory,
        splitter_model_name: str,
        story_chunk_size: int,
) -> str:
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name=splitter_model_name,
        chunk_size=story_chunk_size,
        chunk_overlap=0,
    )

    story_string = f"""Title: {story.title}

Submitted at: {story.posted_at}

Hacker News score: {story.score}

Text: """

    text = (
        text_splitter.split_text(story.soup.get_text().replace("\n", " "))[0]
        if story.soup else ""
    )

    return story_string + text
