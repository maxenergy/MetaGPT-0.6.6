#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/4/29 16:07
@Author  : alexanderwu
@File    : common.py
@Modified By: mashenquan, 2023-11-1. According to Chapter 2.2.2 of RFC 116:
        Add generic class-to-string and object-to-string conversion functionality.
@Modified By: mashenquan, 2023/11/27. Bug fix: `parse_recipient` failed to parse the recipient in certain GPT-3.5
        responses.
"""
from __future__ import annotations

import ast
import contextlib
import importlib
import inspect
import json
import os
import platform
import re
import sys
import traceback
import typing
from pathlib import Path
from typing import Any, List, Tuple, Union

import aiofiles
import loguru
from pydantic_core import to_jsonable_python
from tenacity import RetryCallState, RetryError, _utils

from metagpt.const import MESSAGE_ROUTE_TO_ALL
from metagpt.logs import logger
from metagpt.utils.exceptions import handle_exception


def check_cmd_exists(command) -> int:
    """检查命令是否存在
    :param command: 待检查的命令
    :return: 如果命令存在，返回0，如果不存在，返回非0
    """
    if platform.system().lower() == "windows":
        check_command = "where " + command
    else:
        check_command = "command -v " + command + ' >/dev/null 2>&1 || { echo >&2 "no mermaid"; exit 1; }'
    result = os.system(check_command)
    return result


def require_python_version(req_version: Tuple) -> bool:
    if not (2 <= len(req_version) <= 3):
        raise ValueError("req_version should be (3, 9) or (3, 10, 13)")
    return bool(sys.version_info > req_version)


class OutputParser:
    @classmethod
    def parse_blocks(cls, text: str):
        # 首先根据"##"将文本分割成不同的block
        blocks = text.split("##")

        # 创建一个字典，用于存储每个block的标题和内容
        block_dict = {}

        # 遍历所有的block
        for block in blocks:
            # 如果block不为空，则继续处理
            if block.strip() != "":
                # 将block的标题和内容分开，并分别去掉前后的空白字符
                block_title, block_content = block.split("\n", 1)
                # LLM可能出错，在这里做一下修正
                if block_title[-1] == ":":
                    block_title = block_title[:-1]
                block_dict[block_title.strip()] = block_content.strip()

        return block_dict

    @classmethod
    def parse_code(cls, text: str, lang: str = "") -> str:
        # 修改正则表达式以动态匹配不同的编程语言
        pattern = rf"```{lang}\s+(.*?)```" if lang else r"```.*?\s+(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            # 记录错误日志
            logger.error(f"No code block found for language: {lang}")
            return ""  # 返回空字符串以避免抛出异常

    @classmethod
    def parse_str(cls, text: str):
        text = text.split("=")[-1]
        text = text.strip().strip("'").strip('"')
        return text

    @classmethod
    def parse_file_list(cls, text: str) -> list[str]:
        # Regular expression pattern to find the tasks list.
        pattern = r"\s*(.*=.*)?(\[.*\])"

        # Extract tasks list string using regex.
        match = re.search(pattern, text, re.DOTALL)
        if match:
            tasks_list_str = match.group(2)

            # Convert string representation of list to a Python list using ast.literal_eval.
            tasks = ast.literal_eval(tasks_list_str)
        else:
            tasks = text.split("\n")
        return tasks

    @staticmethod
    def parse_python_code(text: str) -> str:
        for pattern in (r"(.*?```python.*?\s+)?(?P<code>.*)(```.*?)", r"(.*?```python.*?\s+)?(?P<code>.*)"):
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                continue
            code = match.group("code")
            if not code:
                continue
            with contextlib.suppress(Exception):
                ast.parse(code)
                return code
        raise ValueError("Invalid python code")

    @classmethod
    def parse_data(cls, data):
        block_dict = cls.parse_blocks(data)
        parsed_data = {}
        for block, content in block_dict.items():
            # 尝试去除code标记
            try:
                content = cls.parse_code(text=content)
            except Exception:
                # 尝试解析list
                try:
                    content = cls.parse_file_list(text=content)
                except Exception:
                    pass
            parsed_data[block] = content
        return parsed_data

    @staticmethod
    def extract_content(text, tag="CONTENT"):
        # Use regular expression to extract content between [CONTENT] and [/CONTENT]
        extracted_content = re.search(rf"\[{tag}\](.*?)\[/{tag}\]", text, re.DOTALL)

        if extracted_content:
            return extracted_content.group(1).strip()
        else:
            raise ValueError(f"Could not find content between [{tag}] and [/{tag}]")

    @classmethod
    def parse_data_with_mapping(cls, data, mapping):
        if "[CONTENT]" in data:
            data = cls.extract_content(text=data)
        block_dict = cls.parse_blocks(data)
        parsed_data = {}
        for block, content in block_dict.items():
            # 尝试去除code标记
            try:
                content = cls.parse_code(text=content)
            except Exception:
                pass
            typing_define = mapping.get(block, None)
            if isinstance(typing_define, tuple):
                typing = typing_define[0]
            else:
                typing = typing_define
            if typing == List[str] or typing == List[Tuple[str, str]] or typing == List[List[str]]:
                # 尝试解析list
                try:
                    content = cls.parse_file_list(text=content)
                except Exception:
                    pass
            # TODO: 多余的引号去除有风险，后期再解决
            # elif typing == str:
            #     # 尝试去除多余的引号
            #     try:
            #         content = cls.parse_str(text=content)
            #     except Exception:
            #         pass
            parsed_data[block] = content
        return parsed_data

    @classmethod
    def extract_struct(cls, text: str, data_type: Union[type(list), type(dict)]) -> Union[list, dict]:
        """Extracts and parses a specified type of structure (dictionary or list) from the given text.
        The text only contains a list or dictionary, which may have nested structures.

        Args:
            text: The text containing the structure (dictionary or list).
            data_type: The data type to extract, can be "list" or "dict".

        Returns:
            - If extraction and parsing are successful, it returns the corresponding data structure (list or dictionary).
            - If extraction fails or parsing encounters an error, it throw an exception.

        Examples:
            >>> text = 'xxx [1, 2, ["a", "b", [3, 4]], {"x": 5, "y": [6, 7]}] xxx'
            >>> result_list = OutputParser.extract_struct(text, "list")
            >>> print(result_list)
            >>> # Output: [1, 2, ["a", "b", [3, 4]], {"x": 5, "y": [6, 7]}]

            >>> text = 'xxx {"x": 1, "y": {"a": 2, "b": {"c": 3}}} xxx'
            >>> result_dict = OutputParser.extract_struct(text, "dict")
            >>> print(result_dict)
            >>> # Output: {"x": 1, "y": {"a": 2, "b": {"c": 3}}}
        """
        # Find the first "[" or "{" and the last "]" or "}"
        start_index = text.find("[" if data_type is list else "{")
        end_index = text.rfind("]" if data_type is list else "}")

        if start_index != -1 and end_index != -1:
            # Extract the structure part
            structure_text = text[start_index : end_index + 1]

            # 修改异常处理
            try:
                # 尝试解析结构
                result = ast.literal_eval(structure_text)
                if isinstance(result, data_type):
                    return result
                else:
                    logger.error(f"Extracted structure is not a {data_type.__name__}.")
            except (ValueError, SyntaxError) as e:
                logger.error(f"Error parsing text as {data_type.__name__}: {e}")
        else:
            logger.error(f"No {data_type} found in the text.")
            return [] if data_type is list else {}


class CodeParser:
    @classmethod
    def parse_block(cls, block: str, text: str) -> str:
        blocks = cls.parse_blocks(text)
        for k, v in blocks.items():
            if block in k:
                return v
        return ""

    @classmethod
    def parse_blocks(cls, text: str):
        blocks = text.split("##")
        block_dict = {}
        for block in blocks:
            if block.strip() == "":
                continue
            if "\n" not in block:
                block_title = block
                block_content = ""
            else:
                block_title, block_content = block.split("\n", 1)
            block_dict[block_title.strip()] = block_content.strip()

        return block_dict

    @classmethod
    def parse_code(cls, block: str, text: str, lang: str = "cpp") -> str:
        if block:
            text = cls.parse_block(block, text)
        pattern = rf"```{lang}\s+(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            logger.error(f"{pattern} not match following text:")
            logger.error(text)
            return text  # just assume original text is code
        return code

    @classmethod
    def parse_str(cls, block: str, text: str, lang: str = "cpp"):
        code = cls.parse_code(block, text, lang)
        code = code.split("=")[-1]
        code = code.strip().strip("'").strip('"')
        return code

    @classmethod
    def parse_file_list(cls, block: str, text: str, lang: str = "cpp") -> list[str]:
        code = cls.parse_code(block, text, lang)
        pattern = r"\s*(.*=.*)?(\[.*\])"
        match = re.search(pattern, code, re.DOTALL)
        if match:
            tasks_list_str = match.group(2)
            tasks = ast.literal_eval(tasks_list_str)
        else:
            logger.error(f"Unable to parse file list from the code block: {code}")
            return []
        return tasks


import logging

class NoMoneyException(Exception):
    """Raised when the operation cannot be completed due to insufficient funds"""

    def __init__(self, amount, current_balance=None, message="Insufficient funds"):
        self.amount = amount
        self.current_balance = current_balance
        self.message = message
        logging.error(f"NoMoneyException: Required amount: {amount}, Current balance: {current_balance}")
        super().__init__(self.message)

    def __str__(self):
        balance_info = f", Current balance: {self.current_balance}" if self.current_balance is not None else ""
        return f"{self.message} -> Amount required: {self.amount}{balance_info}"


def print_members(module, indent=0, logger=logging.getLogger()):
    """
    Prints members of a module with indentation for better readability.
    """
    prefix = " " * indent
    members_info = []
    for name, obj in inspect.getmembers(module):
        member_type = "Unknown"
        if inspect.isclass(obj):
            member_type = "Class"
        elif inspect.isfunction(obj):
            member_type = "Function"
        elif inspect.ismethod(obj):
            member_type = "Method"
        
        member_info = f"{prefix}{member_type}: {name}"
        members_info.append(member_info)

    formatted_output = "\n".join(members_info)
    logger.info(formatted_output)


def parse_recipient(text, logger=logging.getLogger()):
    pattern = r"## Send To:\s*([A-Za-z]+)\s*|Send To:\s*([A-Za-z]+)\s*"
    match = re.search(pattern, text)

    if match:
        recipient = match.group(1) or match.group(2)
        return recipient

    logger.warning("Recipient not found in the text.")
    return ""


def get_class_name(class_string: str) -> str:
    """
    Extracts the class name from a string that includes module and class name.

    Args:
        class_string (str): The string containing the full class name, 
                            e.g., 'module.submodule.ClassName'.

    Returns:
        str: Extracted class name, e.g., 'ClassName'.
    """
    if not isinstance(class_string, str):
        raise ValueError("Input must be a string.")

    # Split the string by dots and get the last element
    parts = class_string.split('.')
    class_name = parts[-1] if parts else class_string

    return class_name


def any_to_str(val: Any) -> str:
    """
    Converts any value to a string. If the value is a class or an instance of a class,
    returns the class name. If the value is a string, returns it as is.
    
    Args:
        val (Any): The value to convert to a string.

    Returns:
        str: The string representation of the input value.
    """
    if isinstance(val, str):
        # If the value is a string, return it directly
        return val
    elif isinstance(val, type):
        # If the value is a class type, return its name
        return get_class_name(val)
    elif hasattr(val, '__class__'):
        # If the value is an instance of a class, return the class name
        return get_class_name(val.__class__)
    else:
        # Otherwise, return the string representation of the value
        return str(val)


def any_to_str_set(val) -> set:
    """Convert any type to string set."""
    res = set()

    # Check if the value is iterable, but not a string (since strings are technically iterable)
    if isinstance(val, (dict, list, set, tuple)):
        # Special handling for dictionaries to iterate over values
        if isinstance(val, dict):
            val = val.values()

        for i in val:
            res.add(any_to_str(i))
    else:
        res.add(any_to_str(val))

    return res


def is_subscribed(message: "Message", tags: set):
    """Return whether it's consumer"""
    if MESSAGE_ROUTE_TO_ALL in message.send_to:
        return True

    for i in tags:
        if i in message.send_to:
            return True
    return False


def any_to_name(val):
    """
    Convert a value to its name by extracting the last part of the dotted path.
    This function now also handles C++ style names with '::' separators.

    :param val: The value to convert. Can be a string representing a C++ class or method name.

    :return: The name of the value.
    """
    name = any_to_str(val)
    # Handle both Python and C++ style names
    if "::" in name:
        return name.split("::")[-1]
    else:
        return name.split(".")[-1]



def concat_namespace(*args) -> str:
    """
    Concatenates multiple namespace or class name components into a C++ style
    fully qualified name.

    Args:
        args: A variable number of strings representing namespace or class name components.

    Returns:
        A string representing the fully qualified name in C++ style.
    """
    return "::".join(str(value) for value in args)



def general_after_log(logger, sec_format: str = "%0.3f"):
    """
    Generates a logging function to be used after a call is made, suitable for both Python and C++.

    This generated function logs an error message with the outcome of the function call. It includes
    the name of the function, the time taken for the call in seconds (formatted according to `sec_format`),
    and the error message if any.

    :param logger: A Logger instance used to log the error message.
    :param sec_format: A string format specifier for how to format the number of seconds. Defaults to three decimal places.
    :return: A callable that accepts the function name, duration, attempt number, and error message.
    """

    def log_it(fn_name: str, duration: float, attempt_number: int, error_message: str = ""):
        # Log an error message with the function name, time since start, attempt number, and the error message
        formatted_duration = sec_format % duration
        formatted_attempt = f"{attempt_number}{'st' if attempt_number == 1 else 'nd' if attempt_number == 2 else 'rd' if attempt_number == 3 else 'th'}"
        log_message = f"Finished call to '{fn_name}' after {formatted_duration}(s), this was the {formatted_attempt} time calling it."
        if error_message:
            log_message += f" Error: {error_message}"
        logger.error(log_message)

    return log_it


def read_json_file(json_file: str, encoding="utf-8") -> list[Any]:
    if not Path(json_file).exists():
        raise FileNotFoundError(f"json_file: {json_file} not exist, return []")

    with open(json_file, "r", encoding=encoding) as fin:
        try:
            data = json.load(fin)
        except Exception:
            raise ValueError(f"read json file: {json_file} failed")
    return data


def write_json_file(json_file: str, data: list, encoding=None):
    folder_path = Path(json_file).parent
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)

    with open(json_file, "w", encoding=encoding) as fout:
        json.dump(data, fout, ensure_ascii=False, indent=4, default=to_jsonable_python)


def import_class(class_name: str, module_name: str) -> type:
    module = importlib.import_module(module_name)
    a_class = getattr(module, class_name)
    return a_class


def import_class_inst(class_name: str, module_name: str, *args, **kwargs) -> object:
    a_class = import_class(class_name, module_name)
    class_inst = a_class(*args, **kwargs)
    return class_inst


def format_trackback_info(limit: int = 2):
    return traceback.format_exc(limit=limit)


def serialize_decorator(func):
    async def wrapper(self, *args, **kwargs):
        try:
            result = await func(self, *args, **kwargs)
            return result
        except KeyboardInterrupt:
            logger.error(f"KeyboardInterrupt occurs, start to serialize the project, exp:\n{format_trackback_info()}")

            # C++ code snippet for illustration
            cpp_code = """
            // C++ Equivalent
            try {
                // C++ function call
            } catch (const std::exception& e) {
                std::cerr << "Exception caught: " << e.what() << std::endl;
                // Serialization logic
            }
            """
            print(cpp_code)

        except Exception:
            logger.error(f"Exception occurs, start to serialize the project, exp:\n{format_trackback_info()}")
            # Including C++ code snippet
            cpp_code = """
            // C++ Equivalent
            try {
                // C++ function call
            } catch (const std::exception& e) {
                std::cerr << "Exception caught: " << e.what() << std::endl;
                // Serialization logic
            }
            """
            print(cpp_code)

        self.serialize()  # Team.serialize

    return wrapper



def serialize_decorator(func):
    async def wrapper(self, *args, **kwargs):
        try:
            result = await func(self, *args, **kwargs)
            return result
        except KeyboardInterrupt:
            logger.error(f"键盘中断发生，开始序列化项目，异常信息：\n{format_trackback_info()}")

            # 用于演示的 C++ 代码片段
            cpp_code = """
            // C++ 等效代码
            try {
                // C++ 函数调用
            } catch (const std::exception& e) {
                std::cerr << "捕获到异常: " << e.what() << std::endl;
                // 序列化逻辑
            }
            """
            print(cpp_code)

        except Exception:
            logger.error(f"异常发生，开始序列化项目，异常信息：\n{format_trackback_info()}")
            # 包含 C++ 代码片段
            cpp_code = """
            // C++ 等效代码
            try {
                // C++ 函数调用
            } catch (const std::exception& e) {
                std::cerr << "捕获到异常: " << e.what() << std::endl;
                // 序列化逻辑
            }
            """
            print(cpp_code)

        self.serialize()  # Team.serialize

    return wrapper

def role_raise_decorator(func):
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except KeyboardInterrupt as kbi:
            logger.error(f"KeyboardInterrupt: {kbi} occurs, start to serialize the project")
            if self.latest_observed_msg:
                self.rc.memory.delete(self.latest_observed_msg)
            # raise again to make it captured outside
            raise Exception(format_trackback_info(limit=None))
        except Exception as e:
            if self.latest_observed_msg:
                logger.warning(
                    "There is a exception in role's execution, in order to resume, "
                    "we delete the newest role communication message in the role's memory."
                )
                self.rc.memory.delete(self.latest_observed_msg)
            # raise again to make it captured outside
            if isinstance(e, RetryError):
                last_error = e.last_attempt._exception
                name = any_to_str(last_error)
                if re.match(r"^openai\.", name) or re.match(r"^httpx\.", name):
                    raise last_error

            raise Exception(format_trackback_info(limit=None))

        # 示范 C++ 异常处理和日志记录代码
        cpp_code = """
        // C++ 异常处理和日志记录示例
        #include <iostream>
        #include <exception>

        void functionWithExceptionHandling() {
            try {
                // 假设的功能实现
                // ...
            } catch (const std::exception& e) {
                std::cerr << "Exception occurred: " << e.what() << std::endl;
                // 处理异常
            }
        }

        int main() {
            try {
                functionWithExceptionHandling();
            } catch (...) {
                std::cerr << "Unhandled exception occurred." << std::endl;
                // 序列化或其他清理操作
            }
            return 0;
        }
        """
        print("C++ 异常处理和日志记录示例：")
        print(cpp_code)

    return wrapper


@handle_exception
async def aread(filename: str | Path, encoding=None) -> str:
    """Read file asynchronously."""
    async with aiofiles.open(str(filename), mode="r", encoding=encoding) as reader:
        content = await reader.read()



async def awrite(filename: str | Path, data: str, encoding=None):
    """Write file asynchronously."""
    pathname = Path(filename)
    pathname.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(str(pathname), mode="w", encoding=encoding) as writer:
        await writer.write(data)



async def read_file_block(filename: str | Path, lineno: int, end_lineno: int):
    if not Path(filename).exists():
        return ""
    lines = []
    async with aiofiles.open(str(filename), mode="r") as reader:
        ix = 0
        while ix < end_lineno:
            ix += 1
            line = await reader.readline()
            if ix < lineno:
                continue
            if ix > end_lineno:
                break
            lines.append(line)

    # 示范 C++ 读取文件特定行区间的代码片段
    cpp_code = """
    // C++ 读取文件特定行区间示例
    #include <fstream>
    #include <string>
    #include <vector>

    std::vector<std::string> read_file_block(const std::string& filename, int lineno, int end_lineno) {
        std::vector<std::string> lines;
        std::ifstream file(filename);
        std::string line;
        int current_line = 0;
        while (std::getline(file, line)) {
            ++current_line;
            if (current_line >= lineno && current_line <= end_lineno) {
                lines.push_back(line);
            }
            if (current_line > end_lineno) {
                break;
            }
        }
        return lines;
    }

    // 使用方法
    // std::vector<std::string> file_lines = read_file_block("path/to/file", 1, 10);
    // for (const auto& line : file_lines) {
    //     std::cout << line << std::endl;
    // }
    """
    print("C++ 读取文件特定行区间示例：")
    print(cpp_code)

    return "".join(lines)

