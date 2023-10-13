# 🤖LangBridge
A package to call LLM Services / APIs without having to worry about rate limits. It also seamlessly integrates with Langfuse, 
providing an interface for analytics and to track / log API calls and their costs.</br>
</br>
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) ![Python](https://img.shields.io/badge/python-v3.9+-blue.svg) [![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

---

## 🚀Getting Started
### 📋Prerequisites
* Python 3.9+ 🐍
* [Poetry](https://python-poetry.org/) <img src="https://python-poetry.org/images/logo-origami.svg" width="10" height="10">
* [Langfuse Server](https://langfuse.com/) [Optional] 🪢

### 💾Installation
Clone the repository
```bash
git clone https://github.com/vignesh-nswamy/langbridge.git
cd langbridge
```

Install package and dependencies
```bash
poetry install --without dev
```
---
## 🛠 Usage
The framework can be used both as a CLI and a standalone python package. </br>
If you need analytics and tracking, make sure you have a LangFuse server running.</br>
Refer to [LangFuse Docs](https://langfuse.com/docs/get-started) for more details.

### 📦 As a Python Package
```python
import asyncio
from typing import Literal, List

from pydantic import BaseModel, Field

from langbridge.handlers import OpenAiGenerationHandler
from langbridge.schema import OpenAiChatGenerationResponse


class ResponseModel(BaseModel):
    answer: Literal["True", "False"] = Field(description="Whether the statement is True or False")
    reason: str = Field(description="A detailed reason why the statement is True or False")

    
handler = OpenAiGenerationHandler(
    model="gpt-3.5-turbo",
    model_parameters={"temperature": 0.8, "max_tokens": 50},
    inputs=[
        {"text": "The speed of light is the same in all media.", "metadata": {"index": 0}},
        {"text": "Conduction is the only form of heat transfer.", "metadata": {"index": 1}}
    ],
    base_prompt="Answer if the statement below is True or False",
    response_model=ResponseModel,
    max_requests_per_minute=100,
    max_tokens_per_minute=20000
)

responses: List[OpenAiChatGenerationResponse] = asyncio.run(handler.execute())
```
---
## 👨‍💻Contributing
Wanna pitch in? Awesome! Here's how:
1. Clone the repo 👾
2. Create a feature branch (`git checkout -b feature/cool-stuff`) 🌿
3. Commit your changes (`git commit -m 'did cool stuff'`) 🛠
4. Push (`git push origin feature/cool-stuff`)
5. Open a PR ✅
---
## 📜License
Distributed under the MIT License. Check out `LICENSE` for more information.

---
## 🐛Reporting Problems
Got issues or feature requests?, [open an issue](https://github.com/vignesh-nswamy/langbridge/issues) right away!
