from setuptools import setup, find_packages
import os

# Read README for long description
readme_path = "README.md"
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = """
Talk to Your PC - MCP Server

A Model Context Protocol server that enables natural language control and troubleshooting 
of your PC through AI assistants like Claude, ChatGPT, or any MCP-compatible tool.

Features:
- System Diagnosis: Find what's wrong with your computer
- PC Settings: Check volume, WiFi, battery, and more  
- Troubleshooting: Fix common system issues safely
- Cross-Platform: Works on Windows, macOS, and Linux
- Multiple LLMs: Supports OpenAI, Claude, and Azure OpenAI

Simply install, set your API key, and start talking to your PC through your AI assistant!
"""

requirements = [
    "mcp>=0.1.0",
    "openai>=1.0.0",
    "anthropic>=0.7.0", 
    "python-dotenv>=1.0.0",
]

setup(
    name="talk-to-pc-mcp",
    version="0.1.1",
    author="Irene-123",
    author_email="kirtipurohit025@gmail.com",
    description="MCP Server for PC system management and troubleshooting using natural language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Irene-123/talk-to-your-pc-mcp-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators", 
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "talk-to-your-pc-mcp-server=talk_to_your_pc_mcp_server.cli:cli",
        ],
    },
    keywords=[
        "mcp", "model-context-protocol", "ai", "assistant", "system-administration", 
        "troubleshooting", "claude", "openai", "pc-control", "automation", "chatgpt"
    ],
    project_urls={
        "Bug Reports": "https://github.com/Irene-123/talk-to-your-pc-mcp-server/issues",
        "Source": "https://github.com/Irene-123/talk-to-your-pc-mcp-server",
        "Documentation": "https://github.com/Irene-123/talk-to-your-pc-mcp-server/blob/main/README.md",
        "Changelog": "https://github.com/Irene-123/talk-to-your-pc-mcp-server/releases",
    },
    include_package_data=True,
    zip_safe=False,
)