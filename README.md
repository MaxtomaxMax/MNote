# MNote
a simple personal note system utilizing MCP during Nvidia 12th Sky Hackathon competition.

## Guide
Prerequisites：
- [Cherry Studio](https://www.cherry-ai.com/): A desktop client, used as MCP client in this project. 
- [Nodejs](https://nodejs.org/en): Javascript runtime environment. we need it to run some MCP server.
- [ffmpeg](https://ffmpeg.org/): a cross-platform tool for audio and video. In our project developing in Windows11, we download ffmpeg with this [link](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip).
> Do Not Forget to setup environment path!

Environment Setup:
This project includes ​​two locally running MCP server​​ and ​​two remotely invoked MCP server​​. The two remote MCP servers are **​​filesystem**​​ and **​​markmap**​​. Among them, ​​filesystem​​ is a built-in MCP service in Cherry Studio and can be installed via the official documentation [tutorial](https://docs.cherry-ai.com/advanced-basic/mcp), while ​​[markmap]​(https://github.com/jinzcdev/markmap-mcp-server)​ requires manual integration into Cherry Studio.

![](docs\markmap1.png)

import by json format work well by testing.

The locally developed MCP servers all use ​​`uv`​​ to manage projects. If you haven't install `uv`, you can install it via `pip` command.
```cmd
pip install uv
```

After git cloning this repository locally, simply create a virtual environment to proceed.
```cmd
git clone https://github.com/MaxtomaxMax/MNote.git
uv venv
```
Then you need to install some dependencies. Run the following command:
```cmd
uv add fastmcp
uv pip install torch torchaudio openai pydub
uv pip install git+https://github.com/openai/whisper.git speechbrain
uv pip install soundfile
```



​​Next, you need to import the local MCP server into Cherry Studio. Below is a JSON-based import reference. The quick-creation method follows a similar process (TBD)
```json
"WrwmTih41WeliZa8A1WTF": {
      "name": "audio2md",
      "type": "stdio",
      "description": "将音频文件转换成markdown笔记",
      "isActive": true,
      "registryUrl": "",
      "command": "D:\\Your\\uv\\Path\\uv.exe",
      "args": [
        "--directory",
        "D:\\Your\\Path\\MNote",
        "run",
        "audio2md_server.py"
      ]
    },
"5QoifEQ_UdWgE8KLmDREq": {
      "name": "markdown-note-taker",
      "type": "stdio",
      "description": "获取markdown文件内容给大模型并生成结构化笔记的MCP工具",
      "isActive": true,
      "registryUrl": "",
      "command": "D:\\Your\\uv\\Path\\uv.exe",
      "args": [
        "--directory",
        "D:\\Your\\Path\\MNote",
        "run",
        "mcp_note_taker_server.py"
      ]
    },
```
> Note: this Guide is not fully test yet. ​​If you encounter any problems during the environment setup, feel free to propose issue!​ 

---

# 项目报告：基于MCP的个人笔记助手

## 项目概述

## 项目关键技术

## 团队贡献

## 未来展望