#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/14 11:40
@Author  : alexanderwu
@File    : write_prd_an.py
"""
from typing import List

from metagpt.actions.action_node import ActionNode
from metagpt.logs import logger

LANGUAGE = ActionNode(
    key="Language",
    expected_type=str,
    instruction="Provide the language used in the project, typically matching the user's requirement language.",
    example="en_us",
)

PROGRAMMING_LANGUAGE = ActionNode(
    key="Programming Language",
    expected_type=str,
    instruction="Specify the main programming language used in the project, such as C++, Python, JavaScript, etc.",
    example="C++",  
)

CMAKE_CONFIGURATION = ActionNode(
    key="CMake Configuration",
    expected_type=str,
    instruction="Provide a basic CMake configuration for the C++ project.",
    example="cmake_minimum_required(VERSION 3.10)\n"
            "project(ProjectName)\n"
            "set(CMAKE_CXX_STANDARD 17)\n"
            "add_executable(ProjectName main.cpp)\n"
            "# Add other CMake configuration as needed."
)

ORIGINAL_REQUIREMENTS = ActionNode(
    key="Original Requirements",
    expected_type=str,
    instruction="Place the original user's requirements here. This should reflect the core objectives and features expected in the project.",
    example="Develop a high-performance data processing module using C++",  # ʾ�����Ը��ݾ����C++��Ŀ����������
)

PROJECT_NAME = ActionNode(
    key="Project Name",
    expected_type=str,
    instruction="According to the content of \"Original Requirements,\" name the project using snake case style , like 'video_analysis' or 'simple_crm.",
    example="smartnvr",
)

PRODUCT_GOALS = ActionNode(
    key="Product Goals",
    expected_type=List[str],
    instruction="Provide up to three clear, orthogonal product goals.",
    example=["Create an engaging user experience", "Improve accessibility, be responsive", "More beautiful UI"],
)

USER_STORIES = ActionNode(
    key="User Stories",
    expected_type=List[str],
    instruction="Provide up to 3 to 5 scenario-based user stories. Focus on scenarios that are relevant to the backend, performance, or system-level aspects in C++ projects.",
    example=[
        "As a data analyst, I want the application to process large datasets efficiently so that I can get results quickly.",
        "As a system administrator, I want the software to use system resources optimally to ensure smooth operation of other applications.",
        "As a developer, I want the application to have a well-documented API so that it can be easily integrated with other systems.",
        "As an end-user, I want the software to ensure data security and integrity during processing.",
        "As a network engineer, I want the system to handle multiple concurrent connections efficiently."
    ],
)


COMPETITIVE_ANALYSIS = ActionNode(
    key="Competitive Analysis",
    expected_type=List[str],
    instruction="Provide an analysis of 5 to 7 products or services that are competitive or similar to your C++ project. Focus on aspects like performance, scalability, usability, and feature set.",
    example=[
        "FastDataProcessingTool: Offers high-speed data processing, but lacks easy customization options",
        "EfficientResourceManager: Known for optimal resource usage, but has a steep learning curve",
        "SecureDataHandler: Highly secure and reliable, yet has performance limitations under heavy load",
        "StreamlinedAPIIntegrator: Offers seamless API integration but lacks comprehensive documentation",
        "AdvancedSystemOptimizer: Provides extensive system optimization features but lacks user-friendly interface",
        "RobustNetworkManager: Efficient in handling network operations, but not optimized for low-latency scenarios"
    ],
)


COMPETITIVE_QUADRANT_CHART = ActionNode(
    key="Competitive Quadrant Chart",
    expected_type=str,
    instruction="Use mermaid quadrantChart syntax to analyze and compare competitive C++ products or solutions. Evaluate them based on critical factors such as performance, scalability, security, and ease of integration.",
    example="""quadrantChart
    title "Comparison of C++ Data Processing Tools"
    x-axis "Low Performance" --> "High Performance"
    y-axis "Low Scalability" --> "High Scalability"
    quadrant-1 "High Potential"
    quadrant-2 "Needs Improvement"
    quadrant-3 "Niche Players"
    quadrant-4 "Market Leaders"
    "Tool A": [0.7, 0.8]  # High performance and scalability
    "Tool B": [0.4, 0.6]  # Moderate performance, good scalability
    "Tool C": [0.3, 0.2]  # Low performance and scalability
    "Tool D": [0.6, 0.3]  # Good performance, low scalability
    "Our Solution": [0.8, 0.9]  # Targeting high performance and scalability
    """
)


REQUIREMENT_ANALYSIS = ActionNode(
    key="Requirement Analysis",
    expected_type=str,
    instruction="Provide a detailed analysis of the requirements, focusing on aspects critical to C++ projects such as performance optimization, memory management, concurrency, and system integration.",
    example="The project requires a high-performance data processing module capable of handling large datasets efficiently. Key requirements include optimizing memory usage to handle large data loads, implementing multithreading to leverage multi-core processors, and ensuring compatibility with existing database systems. Additionally, the module should be designed with extensibility in mind to easily integrate future enhancements and new data sources."
)

REQUIREMENT_POOL = ActionNode(
    key="Requirement Pool",
    expected_type=List[List[str]],
    instruction="List the top-5 requirements with their priority (P0, P1, P2), focusing on critical aspects for a C++ project such as performance, scalability, and integration.",
    example=[
        ["P0", "Implement a high-performance data processing algorithm that can efficiently handle large datasets."],
        ["P0", "Design the system to support multithreading and parallel processing to maximize CPU utilization."],
        ["P1", "Ensure the module integrates seamlessly with existing database systems and software infrastructure."],
        ["P1", "Develop a robust memory management strategy to optimize resource usage and prevent memory leaks."],
        ["P2", "Create a modular architecture that allows for easy expansion and integration of new features and data sources."]
    ],
)


UI_DESIGN_DRAFT = ActionNode(
    key="UI Design draft",
    expected_type=str,
    instruction="Provide a simple description of UI elements, functions, style, and layout.",
    example="Basic function description with a simple style and layout.",
)

ANYTHING_UNCLEAR = ActionNode(
    key="Anything UNCLEAR",
    expected_type=str,
    instruction="Identify and clarify any unclear aspects of the C++ project, such as technical challenges, performance expectations, integration with other systems, or specific project requirements.",
    example="Need clarification on the expected performance benchmarks for the data processing module and the specific metrics to measure them. Also, details about how the module will integrate with the existing Python-based system are unclear."
)


ISSUE_TYPE = ActionNode(
    key="issue_type",
    expected_type=str,
    instruction="Answer BUG/REQUIREMENT. If it is a bugfix, answer BUG, otherwise answer Requirement",
    example="BUG",
)

IS_RELATIVE = ActionNode(
    key="is_relative",
    expected_type=str,
    instruction="Answer YES/NO. If the requirement is related to the old PRD, answer YES, otherwise NO",
    example="YES",
)

REASON = ActionNode(
    key="reason", expected_type=str, instruction="Explain the reasoning process from question to answer", example="..."
)


NODES = [
    LANGUAGE,
    PROGRAMMING_LANGUAGE,
    ORIGINAL_REQUIREMENTS,
    PROJECT_NAME,
    PRODUCT_GOALS,
    USER_STORIES,
    COMPETITIVE_ANALYSIS,
    COMPETITIVE_QUADRANT_CHART,
    REQUIREMENT_ANALYSIS,
    REQUIREMENT_POOL,
    UI_DESIGN_DRAFT,
    ANYTHING_UNCLEAR,
    CMAKE_CONFIGURATION, 
]

WRITE_PRD_NODE = ActionNode.from_children("WritePRD", NODES)
WP_ISSUE_TYPE_NODE = ActionNode.from_children("WP_ISSUE_TYPE", [ISSUE_TYPE, REASON])
WP_IS_RELATIVE_NODE = ActionNode.from_children("WP_IS_RELATIVE", [IS_RELATIVE, REASON])


def main():
    prompt = WRITE_PRD_NODE.compile(context="")
    logger.info(prompt)


if __name__ == "__main__":
    main()
