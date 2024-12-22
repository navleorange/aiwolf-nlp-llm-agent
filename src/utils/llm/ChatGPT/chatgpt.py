from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

from .message_role import MessageRole

if TYPE_CHECKING:
    import configparser

    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionDeveloperMessageParam,
        ChatCompletionFunctionMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionToolMessageParam,
        ChatCompletionUserMessageParam,
    )


class ChatGPT:
    # init file key
    __inifile_key = "ChatGPT"

    def __init__(self, inifile: configparser.ConfigParser) -> None:
        # ChatGPT settings
        self.model: str = inifile.get(self.__inifile_key, "model")
        self.frequency_penalty: float = inifile.getfloat(self.__inifile_key, "frequency_penalty")
        self.max_completion_tokens: int = inifile.getint(
            self.__inifile_key,
            "max_completion_tokens",
        )
        self.n: int = inifile.getint(self.__inifile_key, "n")
        self.presence_penalty: float = inifile.getfloat(self.__inifile_key, "presence_penalty")
        self.seed: int = inifile.getint(self.__inifile_key, "seed")
        self.temperature: float = inifile.getfloat(self.__inifile_key, "temperature")
        self.top_p: float = inifile.getfloat(self.__inifile_key, "top_p")

        self.messages: list[
            ChatCompletionDeveloperMessageParam
            | ChatCompletionSystemMessageParam
            | ChatCompletionUserMessageParam
            | ChatCompletionToolMessageParam
            | ChatCompletionFunctionMessageParam
        ] = []
        self.token_model = tiktoken.encoding_for_model(model_name=self.model)

        self.load_api_key(inifile=inifile)
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    @classmethod
    def load_api_key(cls, inifile: configparser.ConfigParser) -> None:
        api_key_path: str = inifile.get("ChatGPT", "api_key_path")

        if Path(api_key_path).exists():
            raise FileNotFoundError(api_key_path, "APIの設定ファイルが見つかりません")

        load_dotenv(api_key_path)

    def get_tokens(self, text: str) -> int:
        tokens: list[int] = self.token_model.encode(text)
        return len(tokens)

    @classmethod
    def make_developer_message_param(cls, content: str) -> ChatCompletionDeveloperMessageParam:
        new_message: ChatCompletionDeveloperMessageParam = {
            "content": content,
            "role": MessageRole.DEVELOPER.value,
        }
        return new_message

    @classmethod
    def make_system_message_param(cls, content: str) -> ChatCompletionSystemMessageParam:
        new_message: ChatCompletionSystemMessageParam = {
            "content": content,
            "role": MessageRole.SYSTEM.value,
        }
        return new_message

    @classmethod
    def make_user_message_param(cls, content: str) -> ChatCompletionUserMessageParam:
        new_message: ChatCompletionUserMessageParam = {
            "content": content,
            "role": MessageRole.USER.value,
        }
        return new_message

    @classmethod
    def make_tool_message_param(cls, content: str) -> ChatCompletionToolMessageParam:
        new_message: ChatCompletionToolMessageParam = {
            "content": content,
            "role": MessageRole.TOOL.value,
        }
        return new_message

    @classmethod
    def make_function_message_param(cls, content: str) -> ChatCompletionFunctionMessageParam:
        new_message: ChatCompletionFunctionMessageParam = {
            "content": content,
            "role": MessageRole.FUNCTION.value,
        }
        return new_message

    def add_message(
        self,
        message: ChatCompletionDeveloperMessageParam
        | ChatCompletionSystemMessageParam
        | ChatCompletionUserMessageParam
        | ChatCompletionToolMessageParam
        | ChatCompletionFunctionMessageParam,
    ) -> None:
        self.messages.append(message)

    def add_developer_message(self, content: str) -> None:
        self.add_message(message=self.make_developer_message_param(content=content))

    def add_system_message(self, content: str) -> None:
        self.add_message(message=self.make_system_message_param(content=content))

    def add_user_message(self, content: str) -> None:
        self.add_message(message=self.make_user_message_param(content=content))

    def add_tool_message(self, content: str) -> None:
        self.add_message(message=self.make_tool_message_param(content=content))

    def add_function_message(self, content: str) -> None:
        self.add_message(message=self.make_function_message_param(content=content))

    def create_comment(self) -> ChatCompletion:
        chatgpt_args = {
            "model": self.model,
            "messages": self.messages,
        }

        optional_args = {
            "frequency_penalty": self.frequency_penalty,
            "max_completion_tokens": self.max_completion_tokens,
            "n": self.n,
            "presence_penalty": self.presence_penalty,
            "seed": self.seed,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }
        chatgpt_args.update(
            {key: value for key, value in optional_args.items() if value is not None},
        )

        return self.client.chat.completions.create(**chatgpt_args)