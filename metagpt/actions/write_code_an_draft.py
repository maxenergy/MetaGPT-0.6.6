#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : alexanderwu
@File    : write_review.py
"""
import asyncio
from typing import List

from metagpt.actions import Action
from metagpt.actions.action_node import ActionNode

REVIEW = ActionNode(
    key="Review",
    expected_type=List[str],
    instruction="Act as an experienced reviewer and critically assess the given output. Provide specific and"
    " constructive feedback, highlighting areas for improvement and suggesting changes.",
    example=[
        "The logic in the function `calculate_total` seems flawed. Shouldn't it consider the discount rate as well?",
        "The TODO function is not implemented yet? Should we implement it before commit?",
    ],
)

LGTM = ActionNode(
    key="LGTM",
    expected_type=str,
    instruction="LGTM/LBTM. If the code is fully implemented, "
    "give a LGTM (Looks Good To Me), otherwise provide a LBTM (Looks Bad To Me).",
    example="LBTM",
)

ACTIONS = ActionNode(
    key="Actions",
    expected_type=str,
    instruction="Based on the code review outcome, suggest actionable steps. This can include code changes, "
    "refactoring suggestions, or any follow-up tasks.",
    example=[
    """1. Refactor the `process_data` method to improve readability and efficiency.
       ...
    """,
    """2. Cover edge cases in the `validate_user` function.
       ...
    """,
    """3. Implement the TODO in the `calculate_total` function.
       ...
    """,
    """4. Fix the `handle_events` method to update the game state only if a move is successful.
       ```cpp
       void handle_events() {
           SDL_Event event;
           while (SDL_PollEvent(&event)) {
               if (event.type == SDL_QUIT) {
                   return false;
               }
               bool moved = false;
               if (event.type == SDL_KEYDOWN) {
                   // C++ specific logic for handling keyboard events
                   ...
               }
               if (moved) {
                   // Update the game state only if a move was successful
                   render();
               }
           }
           return true;
       }
       ```
    """,
],
)

WRITE_DRAFT = ActionNode(
    key="WriteDraft",
    expected_type=str,
    instruction="Could you write draft code for move function in order to implement it?",
    example="Draft: ...",
)


WRITE_MOVE_FUNCTION = ActionNode(
    key="WriteFunction",
    expected_type=str,
    instruction="write code for the function not implemented.",
    example="""
```Code
...
```
""",
)


REWRITE_CODE = ActionNode(
    key="RewriteCode",
    expected_type=str,
    instruction="""rewrite code based on the Review and Actions""",
    example=[
        """
        ```python
        ## example.py
        def calculate_total(price, quantity):
            total = price * quantity
            # Add logic to consider discount or other factors
            return total
        ```
        """,
        """
        ```cpp
        ## example.cpp
        double calculate_total(double price, int quantity) {
            double total = price * quantity;
            // Add logic to consider discount or other factors
            return total;
        }
        ```
        """
    ],
)


CODE_REVIEW_CONTEXT = """
# System
Role: You are a professional software engineer, and your main task is to review and revise the code. You need to ensure that the code conforms to the industry standards, is elegantly designed and modularized, easy to read and maintain.
Language: Please use the same language as the user requirement, but the title and code should be still in English. For example, if the user speaks Chinese, the specific text of your answer should also be in Chinese.

# Context
## System Design
{"Implementation approach": "We will use C++ to develop a high-performance data processing system. The system will focus on efficiency and stability. We will leverage C++'s multithreading and object-oriented features to build this system", "File list": ["main.cpp", "DataProcessor.h", "DataProcessor.cpp", "Utils.h", "Utils.cpp"], "Data structures and interfaces": "classDiagram\
    class DataProcessor {\
        -data Array\
        +processData()\
        +loadData(filePath: String)\
        +saveData(filePath: String)\
    }\
    class Utils {\
        +static parseData(rawData: String)\
        +static formatData(data: Array)\
    }\
    DataProcessor --> Utils : uses", "Program call flow": "sequenceDiagram\
    participant M as Main\
    participant DP as DataProcessor\
    participant U as Utils\
    M->>DP: loadData(filePath)\
    DP->>U: parseData(rawData)\
    U-->>DP: return parsedData\
    loop Data Processing Loop\
        DP->>DP: processData()\
    end\
    M->>DP: saveData(filePath)", "Anything UNCLEAR": "目前项目要求明确，没有不清楚的地方。"}

## Tasks
{"Required C++ libraries": ["标准库", "其他第三方库"], "Logic Analysis": [["main.cpp", "程序入口，负责初始化DataProcessor对象和处理用户输入"], ["DataProcessor.h/cpp", "包含DataProcessor类，负责数据的加载、处理和保存"], ["Utils.h/cpp", "包含工具函数，用于数据的解析和格式化"]], "Task list": ["main.cpp", "DataProcessor.h", "DataProcessor.cpp", "Utils.h", "Utils.cpp"], "Full API spec": "", "Shared Knowledge": "\'DataProcessor.cpp\' 包含数据处理逻辑，被 \'main.cpp\' 调用。", "Anything UNCLEAR": "目前项目要求明确，没有不清楚的地方。"}

## Code Files
```cpp
// main.cpp
#include "DataProcessor.h"

int main() {
    DataProcessor processor;
    processor.loadData("data/input.txt");
    processor.processData();
    processor.saveData("data/output.txt");
    return 0;
}

cpp
// DataProcessor.h
#ifndef DATAPROCESSOR_H
#define DATAPROCESSOR_H

#include <string>
#include <vector>

class DataProcessor {
public:
    void loadData(const std::string& filePath);
    void processData();
    void saveData(const std::string& filePath);

private:
    std::vector<int> data;
};

#endif // DATAPROCESSOR_H
//DataProcessor.cpp

cpp
// DataProcessor.cpp
#include "DataProcessor.h"
#include "Utils.h"
#include <fstream>

void DataProcessor::loadData(const std::string& filePath) {
    // Logic to load data from file
}

void DataProcessor::processData() {
    // Data processing logic
}

void DataProcessor::saveData(const std::string& filePath) {
    // Logic to save data to file
}
cpp
// Utils.h
#ifndef UTILS_H
#define UTILS_H

#include <string>
#include <vector>

class Utils {
public:
    static std::vector<int> parseData(const std::string& rawData);
    static std::string formatData(const std::vector<int>& data);
};

#endif // UTILS_H
cpp
// Utils.cpp
#include "Utils.h"

std::vector<int> Utils::parseData(const std::string& rawData) {
    // Logic to parse data
}

std::string Utils::formatData(const std::vector<int>& data) {
    // Logic to format data
}
"""


CODE_REVIEW_SMALLEST_CONTEXT = """
## Code to be Reviewed: Game.cpp
```cpp
// Game.cpp
#include "Game.h"

Game::Game() {
    this->board = createEmptyBoard();
    this->score = 0;
    this->bestScore = 0;
}

std::vector<std::vector<int>> Game::createEmptyBoard() {
    std::vector<std::vector<int>> board(4, std::vector<int>(4, 0));
    return board;
}

void Game::startGame() {
    this->board = createEmptyBoard();
    this->score = 0;
    addRandomTile();
    addRandomTile();
}

void Game::addRandomTile() {
    std::vector<std::pair<int, int>> emptyCells;
    for (int r = 0; r < 4; ++r) {
        for (int c = 0; c < 4; ++c) {
            if (this->board[r][c] == 0) {
                emptyCells.emplace_back(r, c);
            }
        }
    }
    if (!emptyCells.empty()) {
        auto randomCell = emptyCells[rand() % emptyCells.size()];
        this->board[randomCell.first][randomCell.second] = (rand() % 10 < 9) ? 2 : 4;
    }
}

// Additional methods for move, getBoard, getScore, getBestScore, setBestScore...
"""


CODE_REVIEW_SAMPLE = """
## Code Review: Game.cpp
1. The code partially implements the requirements. The `Game` class is missing the full implementation of the `move` method, which is crucial for the game's functionality.
2. The code logic is not completely correct. The `move` method is not implemented, which means the game cannot process player moves.
3. The existing code follows the "Data structures and interfaces" in terms of class structure but lacks full method implementations.
4. Not all functions are implemented. The `move` method is incomplete and does not handle the logic for moving and merging tiles.
5. All necessary pre-dependencies seem to be imported since the code does not indicate the need for additional imports.
6. The methods from other files (such as `Storage`) are not being used in the provided code snippet, but the class structure suggests that they will be used correctly.

## Actions
1. Implement the `move` method to handle tile movements and merging. This is a complex task that requires careful consideration of the game's rules and logic. Here is a simplified version of how one might begin to implement the `move` method:
   ```cpp
   void Game::move(Direction direction) {
       // Simplified logic for moving tiles up
       if (direction == Direction::UP) {
           for (int col = 0; col < 4; col++) {
               std::vector<int> tiles;
               for (int row = 0; row < 4; row++) {
                   if (this->board[row][col] != 0) {
                       tiles.push_back(this->board[row][col]);
                   }
               }
               // Logic for merging tiles
               // ...
               // Update the board with the new values
               for (int row = 0; row < 4; row++) {
                   this->board[row][col] = (row < tiles.size()) ? tiles[row] : 0;
               }
           }
       }
       // Additional logic needed for DOWN, LEFT, RIGHT
       // ...
       addRandomTile();
   }
Integrate the Storage class methods to handle the best score. This means updating the startGame and setBestScore methods to use Storage for retrieving and setting the best score:
cpp
void Game::startGame() {
    this->board = createEmptyBoard();
    this->score = 0;
    this->bestScore = Storage::getBestScore(); // Retrieve the best score from storage
    addRandomTile();
    addRandomTile();
}

void Game::setBestScore(int score) {
    if (score > this->bestScore) {
        this->bestScore = score;
        Storage::setBestScore(score); // Set the new best score in storage
    }
}
Code Review Result
LBTM
"""


WRITE_CODE_NODE = ActionNode.from_children("WRITE_REVIEW_NODE", [REVIEW, LGTM, ACTIONS])
WRITE_MOVE_NODE = ActionNode.from_children("WRITE_MOVE_NODE", [WRITE_DRAFT, WRITE_MOVE_FUNCTION])


CR_FOR_MOVE_FUNCTION_BY_3 = """
The implementation of the `move` function in C++ seems to be well-structured and follows a clear logic for moving and merging tiles in the specified direction. However, there are several areas where the code could be improved:

1. Encapsulation: The logic for moving and merging tiles could be encapsulated into smaller, reusable member functions of the `Game` class to improve readability and maintainability. This will also make the code more aligned with object-oriented principles.

2. Use of Magic Numbers: The function contains some magic numbers (e.g., 4, representing the dimensions of the board). These numbers should be replaced with named constants or class members to make the code more robust and easier to maintain.

3. Documentation: The function lacks comments explaining the logic and purpose of each section. Adding detailed comments would improve the readability and maintainability of the code, making it more accessible to future developers.

4. Error Handling: It is important to consider robust error handling in the function, especially to address edge cases or unexpected inputs. This might include checking for invalid directions or ensuring the integrity of the board state after each move.

Overall, the `move` function could greatly benefit from a refactoring that focuses on these aspects to enhance its readability, maintainability, and adherence to best practices in C++ programming.
"""



class WriteCodeAN(Action):
    """Write a code review for the context."""

    async def run(self, context):
        self.llm.system_prompt = "You are an outstanding engineer and can implement any code"
        return await WRITE_MOVE_FUNCTION.fill(context=context, llm=self.llm, schema="json")
        # return await WRITE_CODE_NODE.fill(context=context, llm=self.llm, schema="markdown")


async def main():
    await WriteCodeAN().run(CODE_REVIEW_SMALLEST_CONTEXT)


if __name__ == "__main__":
    asyncio.run(main())
