#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/14 15:28
@Author  : alexanderwu
@File    : project_management_an.py
"""
from typing import List

from metagpt.actions.action_node import ActionNode
from metagpt.logs import logger

REQUIRED_CPP_PACKAGES = ActionNode(
    key="Required C++/header packages",
    expected_type=List[str],
    instruction="List down the required C++ packages, possibly using vcpkg or another package manager. "
                "Format the list as it would appear in a vcpkg configuration file or equivalent."
                "generate CMakeLists.txt and header files for C++ project ",
    example=["fmt", "nlohmann-json", "vcpkg"],
)

REQUIRED_PYTHON_PACKAGES = ActionNode(
    key="Required Python packages",
    expected_type=List[str],
    instruction="Provide required Python packages in requirements.txt format.",
    example=["flask==1.1.2", "bcrypt==3.2.0"],
)

REQUIRED_OTHER_LANGUAGE_PACKAGES = ActionNode(
    key="Required Other language third-party packages",
    expected_type=List[str],
    instruction="List down the required packages for languages other than Python.",
    example=["No third-party dependencies required"],
)

LOGIC_ANALYSIS = ActionNode(
    key="Logic Analysis",
    expected_type=List[List[str]],
    instruction="Provide a list of files with the classes/methods/functions to be implemented for a C++ project, "
                "including dependency analysis and header/source file relationships.",
    example=[
        ["Game.h", "Contains Game class declaration and its member function prototypes"],
        ["Game.cpp", "Contains implementation of Game class methods defined in Game.h"],
        ["Main.cpp", "Contains the main function, includes Game.h"],
    ],
)


TASK_LIST = ActionNode(
    key="Task list",
    expected_type=List[str],
    instruction="Break down the tasks into a list of C++ filenames, prioritized by dependency order. "
                "Include both header files and source files.",
    example=["Game.h", "Game.cpp", "Main.cpp"],
)


FULL_API_SPEC = ActionNode(
    key="Full API spec",
    expected_type=str,
    instruction="Describe all APIs for the C++ project in a detailed and clear manner, similar to OpenCV's documentation style. "
                "Include classes, methods, parameters, return values, and any additional relevant information. "
                "Use a documentation generator like Doxygen for detailed and formatted API documentation if needed.",
    example="Class: VideoCapture\n"
            "Methods:\n"
            "  - open(filename: String): bool\n"
            "  - read(): (bool, Mat)\n"
            "  - release(): void\n"
            "Description: The VideoCapture class allows for video file capture.\n"
            "...\n\n"
            "Function: findContours\n"
            "Parameters:\n"
            "  - image: Mat\n"
            "  - mode: RetrievalModes\n"
            "  - method: ContourApproximationModes\n"
            "Return: List of Contours\n"
            "Description: This function retrieves contours from a binary image.\n"
            "..."
)


SHARED_KNOWLEDGE = ActionNode(
    key="Shared Knowledge",
    expected_type=str,
    instruction="Detail any shared knowledge specific to the C++ project, such as common utility functions, "
                "configuration variables, or references to local code libraries. Include guidelines on how these "
                "should be used within the project.",
    example="'Utils.h/cpp' contains common utility functions like logging and data parsing, which are used across "
            "the project. Include 'Utils.h' in files where these functions are needed."
)



ANYTHING_UNCLEAR_PM = ActionNode(
    key="Anything UNCLEAR",
    expected_type=str,
    instruction="Mention any unclear aspects in the project management context and try to clarify them. "
                "This includes technical uncertainties, project scope, dependencies, or any other issues that need clarification.",
    example="Clarification needed on how to start and initialize third-party libraries.\n"
            "Need details on the expected performance metrics for the C++ data processing module.\n"
            "Uncertain about the integration process of our C++ module with existing Python codebase.\n"
            "Seeking more information on the deployment strategy for the application."
)

NODES = [
    REQUIRED_CPP_PACKAGES,
    REQUIRED_PYTHON_PACKAGES,
    REQUIRED_OTHER_LANGUAGE_PACKAGES,
    LOGIC_ANALYSIS,
    TASK_LIST,
    FULL_API_SPEC,
    SHARED_KNOWLEDGE,
    ANYTHING_UNCLEAR_PM,
]


PM_NODE = ActionNode.from_children("PM_NODE", NODES)


def main():
    shared_knowledge_info = [
        "The project uses GStreamer for media processing. Documentation is available in the /docs directory.",
        "We have a set of common utility functions in Utils.h that are used across various modules.",
        "Global configuration settings are defined in Config.h."
    ]
    shared_knowledge_str = "\n".join(shared_knowledge_info)

    # 直接在生成提示时使用 shared_knowledge_str
    context = {"Shared Knowledge": shared_knowledge_str}

    # 编译并输出提示
    prompt = PM_NODE.compile(context="")
    logger.info(prompt)


if __name__ == "__main__":
    main()
