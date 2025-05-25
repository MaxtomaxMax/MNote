from fastmcp import FastMCP
from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()
NVIDIA_API = os.getenv("NVIDIA_API")

mcp = FastMCP(name="markdown-note-taker")

from openai import OpenAI

@mcp.tool()
def markdown_summarizer(
    markdown_text: str,
    model: str = "qwen/qwen3-235b-a22b"
) -> str:
    """
    summarize markdown text and output with a structured format.

    Args:
        markdown_text (str): The text to summarize.
        model (str): The language model to use.

    Returns:
        str: The summarized text.
    """
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = NVIDIA_API,
    )
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":f"请总结以下的 Markdown 文本，并输出根据总结内容输出结构化的 markdown文本：\n\n{markdown_text}"}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8192,
        extra_body={"chat_template_kwargs": {"thinking":True}},
        stream=False
    )

    summarized_content = []
    for chunk in completion:
        # reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
        # if reasoning:
        #     print(reasoning, end="")
        if chunk.choices[0].delta.content is not None:
            summarized_content.append(chunk.choices[0].delta.content)

    return "".join(summarized_content)

@mcp.tool()
def knowledge_map(
    markdown_text: str,
    model: str = "qwen/qwen3-235b-a22b"
) -> str:
    """
    Generate a structured knowledge map with markdown format from the given markdown text, 
    identifying prerequisite and advanced knowledge relationships to facilitate learning progression.

    This tool analyzes educational content and extracts a hierarchical representation of:
    - Prerequisite knowledge (foundational concepts required to understand the current material)
    - Advanced knowledge (deeper or more complex topics that build upon the current material)

    Args:
        markdown_text (str): The text to generate a knowledge map from.
        model (str): The language model to use.

    Returns:
        str: The generated knowledge map.
    """
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = NVIDIA_API,
    )

    prompt = """
    请根据以下的 Markdown 文本生成知识图谱,知识图谱主要包括前置知识和进阶知识，生成的markdown文本就包含这两个主要内容
    前置知识：指当前知识点所依赖的基础知识或概念
    进阶知识：指在当前知识点的基础上，进一步深入学习的相关知识或概念
    """
    completion =  client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":f"{prompt}\n\n{markdown_text}"}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8192,
        extra_body={"chat_template_kwargs": {"thinking":True}},
        stream=False
    )

    summarized_content = []
    for chunk in completion:
        # reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
        # if reasoning:
        #     print(reasoning, end="")
        if chunk.choices[0].delta.content is not None:
            summarized_content.append(chunk.choices[0].delta.content)

    return "".join(summarized_content)



if __name__ == "__main__":
    mcp.run()