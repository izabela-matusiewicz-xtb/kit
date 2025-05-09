"""MCP server implementation for kit."""

from __future__ import annotations

from typing import Dict, List, Optional, Any
import logging
import json
import sys
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field, ValidationError

from ..repository import Repository
from ..vector_searcher import VectorSearcher
from ..dependency_analyzer import DependencyAnalyzer
from ..docstring_indexer import DocstringIndexer
from ..summaries import Summarizer
from ..tree_sitter_symbol_extractor import TreeSitterSymbolExtractor

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("kit-mcp")


def create_error_content(code: str, message: str) -> TextContent:
    return TextContent(type="text", text=json.dumps({"error": message, "code": code}))


class MCPError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

    def to_error_data(self) -> ErrorData:
        return ErrorData(code=self.code, message=self.message)


class OpenRepoParams(BaseModel):
    path_or_url: str
    github_token: Optional[str] = None


class SearchParams(BaseModel):
    repo_id: str
    query: str
    pattern: str = "*.py"


class GetFileContentParams(BaseModel):
    repo_id: str
    file_path: str


class ExtractSymbolsParams(BaseModel):
    repo_id: str
    file_path: str
    symbol_type: Optional[str] = None


class FindSymbolUsagesParams(BaseModel):
    repo_id: str
    symbol_name: str
    file_path: Optional[str] = None


class GetFileTreeParams(BaseModel):
    repo_id: str


class SemanticSearchParams(BaseModel):
    repo_id: str
    query: str
    limit: Optional[int] = 10


class AnalyzeDependenciesParams(BaseModel):
    repo_id: str
    file_path: Optional[str] = None
    depth: Optional[int] = 1


class GetDocumentationParams(BaseModel):
    repo_id: str
    symbol_name: Optional[str] = None
    file_path: Optional[str] = None


class GetCodeSummaryParams(BaseModel):
    repo_id: str
    file_path: str
    symbol_name: Optional[str] = None


class KitServerLogic:
    def __init__(self):
        self._repos: Dict[str, Repository] = {}
        self._analyzers: Dict[str, Dict[str, Any]] = {}

    def get_repo(self, repo_id: str) -> Repository:
        repo = self._repos.get(repo_id)
        if not repo:
            raise MCPError(code=INVALID_PARAMS, message=f"Repository {repo_id} not found")
        return repo
    
    def open_repository(
        self, path_or_url: str, github_token: Optional[str] = None
    ) -> str:
        try:
            repo = Repository(path_or_url, github_token=github_token)
            repo_id = str(len(self._repos) + 1)
            self._repos[repo_id] = repo
            self._analyzers[repo_id] = {}
            return repo_id
        except FileNotFoundError as e:
            raise MCPError(code=INVALID_PARAMS, message=f"Repository path not found: {str(e)}")
        except Exception as e:
            raise MCPError(code=INVALID_PARAMS, message=str(e))

    def search_code(self, repo_id: str, query: str, pattern: str = "*.py") -> list[str]:
        repo = self.get_repo(repo_id)
        try:
            return repo.search_text(query, file_pattern=pattern)
        except Exception as e:
            raise MCPError(code=INVALID_PARAMS, message=f"Invalid search pattern: {str(e)}")

    def get_file_content(self, repo_id: str, file_path: str) -> str:
        repo = self.get_repo(repo_id)
        try:
            return repo.get_file_content(file_path)
        except FileNotFoundError as e:
            raise MCPError(code=INVALID_PARAMS, message=str(e))
        except Exception as e:
            raise MCPError(code=INVALID_PARAMS, message=f"Error reading file: {str(e)}")

    def extract_symbols(
        self, repo_id: str, file_path: str, symbol_type: Optional[str] = None
    ) -> list[dict]:
        repo = self.get_repo(repo_id)
        try:
            symbols = repo.extract_symbols(file_path)
            return (
                [s for s in symbols if s["type"] == symbol_type] if symbol_type else symbols
            )
        except FileNotFoundError as e:
            raise MCPError(code=INVALID_PARAMS, message=str(e))
        except Exception as e:
            raise MCPError(code=INVALID_PARAMS, message=f"Error extracting symbols: {str(e)}")

    def find_symbol_usages(
        self, repo_id: str, symbol_name: str, file_path: Optional[str] = None
    ) -> list[dict]:
        repo = self.get_repo(repo_id)
        return repo.find_symbol_usages(symbol_name, file_path=file_path)

    def get_file_tree(
        self,
        repo_id: str,
    ) -> Any:
        repo = self.get_repo(repo_id)
        tree_list = repo.get_file_tree()

        return tree_list

    def get_analyzer(self, repo_id: str, analyzer_name: str, kwargs: Optional[dict] = None) -> Any:
        if repo_id not in self._analyzers:
            raise MCPError(
                code=INVALID_PARAMS, message=f"Repository {repo_id} not found"
            )
        if analyzer_name not in self._analyzers[repo_id]:
            repo = self._repos[repo_id]
            if analyzer_name == "vector_searcher":
                embed_fn = kwargs.get("embed_fn")
                if not embed_fn:
                    raise MCPError(code=INVALID_PARAMS, message="embed_fn is required for vector_searcher")
                self._analyzers[repo_id][analyzer_name] = VectorSearcher(repo, embed_fn=embed_fn)
            elif analyzer_name == "dependency_analyzer":
                self._analyzers[repo_id][analyzer_name] = DependencyAnalyzer(repo)
            elif analyzer_name == "docstring_indexer":
                self._analyzers[repo_id][analyzer_name] = DocstringIndexer(repo)
            elif analyzer_name == "code_summarizer":
                self._analyzers[repo_id][analyzer_name] = Summarizer(repo)
            elif analyzer_name == "symbol_extractor":
                self._analyzers[repo_id][analyzer_name] = TreeSitterSymbolExtractor(
                    repo
                )
            else:
                raise MCPError(
                    code=INVALID_PARAMS, message=f"Unknown analyzer: {analyzer_name}"
                )
        return self._analyzers[repo_id][analyzer_name]

    def semantic_search(self, repo_id: str, query: str, limit: int) -> Any:
        analyzer = self.get_analyzer(repo_id, "vector_searcher")
        if analyzer is None:
            raise MCPError(code=INTERNAL_ERROR, message="Vector search not available")
        return analyzer.search(query, limit=limit)

    def analyze_dependencies(
        self, repo_id: str, file_path: Optional[str], depth: Optional[int]
    ) -> Any:
        analyzer = self.get_analyzer(repo_id, "dependency_analyzer")
        return analyzer.analyze(file_path=file_path, depth=depth)

    def get_documentation(
        self, repo_id: str, symbol_name: Optional[str], file_path: Optional[str]
    ) -> Any:
        analyzer = self.get_analyzer(repo_id, "docstring_indexer")
        return analyzer.get_documentation(symbol_name=symbol_name, file_path=file_path)

    def get_code_summary(
        self, repo_id: str, file_path: str, symbol_name: Optional[str] = None
    ) -> Any:
        repo = self.get_repo(repo_id)
        try:
            analyzer = self.get_analyzer(repo_id, "code_summarizer")
            
            # Get all three types of summaries
            summaries = {}
            
            # Always get file summary
            summaries["file"] = analyzer.summarize_file(file_path)
            
            # Get function and class summaries only if symbol_name is provided
            if symbol_name:
                try:
                    summaries["function"] = analyzer.summarize_function(file_path, symbol_name)
                except ValueError as e:
                    # If symbol is not a function, set to None
                    summaries["function"] = None
                    
                try:
                    summaries["class"] = analyzer.summarize_class(file_path, symbol_name)
                except ValueError as e:
                    # If symbol is not a class, set to None
                    summaries["class"] = None
            
            return summaries
            
        except Exception as e:
            raise MCPError(code=INVALID_PARAMS, message=str(e))
    
    def list_tools(self) -> list[Tool]:
        return [
        Tool(name="open_repository", description="Open a repository and return its ID", inputSchema=OpenRepoParams.model_json_schema()),
        Tool(name="search_code", description="Search for text in a repository", inputSchema=SearchParams.model_json_schema()),
        Tool(name="get_file_content", description="Get the content of a file", inputSchema=GetFileContentParams.model_json_schema()),
        Tool(name="extract_symbols", description="Extract code symbols from a file", inputSchema=ExtractSymbolsParams.model_json_schema()),
        Tool(name="find_symbol_usages", description="Find all usages of a symbol", inputSchema=FindSymbolUsagesParams.model_json_schema()),
        Tool(name="get_file_tree", description="Get the repository file structure", inputSchema=GetFileTreeParams.model_json_schema()),
        Tool(name="semantic_search", description="Search code using semantic similarity", inputSchema=SemanticSearchParams.model_json_schema()),
        Tool(name="analyze_dependencies", description="Analyze code dependencies", inputSchema=AnalyzeDependenciesParams.model_json_schema()),
        Tool(name="get_documentation", description="Get documentation and docstrings", inputSchema=GetDocumentationParams.model_json_schema()),
        Tool(name="get_code_summary", description="Get a summary of code for a given file. If symbol_name is provided, also attempts to summarize it as a function and class.", inputSchema=GetCodeSummaryParams.model_json_schema()),
    ]

    def list_prompts(self) -> list[Prompt]:
        return [
        Prompt(
            name="open_repo",
            description="Open a repository and explore its contents",
            arguments=[
                PromptArgument(name="path_or_url", description="Path to local repository or GitHub URL", required=True),
                PromptArgument(name="github_token", description="GitHub token for private repositories", required=False),
            ],
        ),
        Prompt(
            name="search_repo",
            description="Search for code in a repository",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
                PromptArgument(name="query", description="Text search query", required=True),
                PromptArgument(name="pattern", description="Optional file pattern (e.g. *.py)", required=False),
            ],
        ),
        Prompt(
            name="get_file_content",
            description="Get the content of a specific file",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
                PromptArgument(name="file_path", description="Path to the file", required=True),
            ],
        ),
        Prompt(
            name="extract_symbols",
            description="Extract functions, classes or symbols from a file",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
                PromptArgument(name="file_path", description="Path to the file", required=True),
                PromptArgument(name="symbol_type", description="Optional filter: function or class", required=False),
            ],
        ),
        Prompt(
            name="find_symbol_usages",
            description="Find all usages of a given symbol",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
                PromptArgument(name="symbol_name", description="Name of the symbol to find", required=True),
                PromptArgument(name="file_path", description="Optional file path to narrow the search", required=False),
            ],
        ),
        Prompt(
            name="get_file_tree",
            description="Get the file structure of the repository",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
            ],
        ),
        Prompt(
            name="semantic_search",
            description="Perform semantic code search",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
                PromptArgument(name="query", description="Semantic query", required=True),
                PromptArgument(name="limit", description="Max number of results", required=False),
            ],
        ),
        Prompt(
            name="analyze_dependencies",
            description="Analyze code dependencies",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
                PromptArgument(name="file_path", description="Optional path to a specific file", required=False),
                PromptArgument(name="depth", description="Optional dependency depth", required=False),
            ],
        ),
        Prompt(
            name="get_documentation",
            description="Extract docstrings or documentation from code",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
                PromptArgument(name="symbol_name", description="Symbol to get documentation for", required=False),
                PromptArgument(name="file_path", description="File to extract documentation from", required=False),
            ],
        ),
        Prompt(
            name="get_code_summary",
            description="Get a summary of code for a given file. If symbol_name is provided, also attempts to summarize it as a function and class.",
            arguments=[
                PromptArgument(name="repo_id", description="ID of the repository", required=True),
                PromptArgument(name="file_path", description="Path to the file", required=True),
                PromptArgument(name="symbol_name", description="Optional name of a function or class to summarize. If provided, will attempt to summarize it as both a function and class.", required=False),
            ],
        ),
    ]

    def get_prompt(self, name: str, arguments: dict | None) -> GetPromptResult:
        if not arguments:
            raise MCPError(code=INVALID_PARAMS, message="Arguments are required")

        try:
            match name:
                case "open_repo":
                    path_or_url = arguments["path_or_url"]
                    github_token = arguments.get("github_token")
                    repo_id = self.open_repository(path_or_url, github_token)
                    repo = self._repos[repo_id]
                    return GetPromptResult(
                        description=f"Repository opened with ID: {repo_id}",
                        messages=[
                            PromptMessage(role="user", content=TextContent(type="text", text=f"Opened repo {repo_id} with tree:\n{repo.get_file_tree()}"))
                        ],
                    )
                case "search_repo":
                    results = self.search_code(arguments["repo_id"], arguments["query"], arguments.get("pattern", "*.py"))
                    return GetPromptResult(description="Search results", messages=[PromptMessage(role="user", content=TextContent(type="text", text=str(results)))])
                case "get_file_content":
                    content = self.get_file_content(arguments["repo_id"], arguments["file_path"])
                    return GetPromptResult(description="File content", messages=[PromptMessage(role="user", content=TextContent(type="text", text=content))])
                case "extract_symbols":
                    symbols = self.extract_symbols(arguments["repo_id"], arguments["file_path"], arguments.get("symbol_type"))
                    return GetPromptResult(description="Extracted symbols", messages=[PromptMessage(role="user", content=TextContent(type="text", text=json.dumps(symbols, indent=2)))])
                case "find_symbol_usages":
                    usages = self.find_symbol_usages(arguments["repo_id"], arguments["symbol_name"], arguments.get("file_path"))
                    return GetPromptResult(description="Symbol usages", messages=[PromptMessage(role="user", content=TextContent(type="text", text=json.dumps(usages, indent=2)))])
                case "get_file_tree":
                    tree = self.get_file_tree(arguments["repo_id"])
                    return GetPromptResult(description="File tree", messages=[PromptMessage(role="user", content=TextContent(type="text", text=json.dumps(tree, indent=2)))])
                case "semantic_search":
                    results = self.semantic_search(arguments["repo_id"], arguments["query"], arguments.get("limit", 10))
                    return GetPromptResult(description="Semantic search results", messages=[PromptMessage(role="user", content=TextContent(type="text", text=json.dumps(results, indent=2)))])
                case "analyze_dependencies":
                    deps = self.analyze_dependencies(arguments["repo_id"], arguments.get("file_path"), arguments.get("depth"))
                    return GetPromptResult(description="Dependencies", messages=[PromptMessage(role="user", content=TextContent(type="text", text=json.dumps(deps, indent=2)))])
                case "get_documentation":
                    docs = self.get_documentation(arguments["repo_id"], arguments.get("symbol_name"), arguments.get("file_path"))
                    return GetPromptResult(description="Documentation", messages=[PromptMessage(role="user", content=TextContent(type="text", text=json.dumps(docs, indent=2)))])
                case "get_code_summary":
                    summary = self.get_code_summary(arguments["repo_id"], arguments["file_path"], arguments.get("symbol_name"))
                    return GetPromptResult(description="Code summary", messages=[PromptMessage(role="user", content=TextContent(type="text", text=json.dumps(summary, indent=2)))])
                case _:
                    raise MCPError(code=INVALID_PARAMS, message=f"Unknown prompt: {name}")
        except KeyError as e:
            raise MCPError(code=INVALID_PARAMS, message=f"Missing required argument: {e.args[0]}")

async def serve() -> None:
    server = Server("kit")
    logic = KitServerLogic()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            if name == "open_repository":
                args = OpenRepoParams(**arguments)
                repo_id = logic.open_repository(args.path_or_url, args.github_token)
                return [TextContent(type="text", text=repo_id)]
            elif name == "search_code":
                args = SearchParams(**arguments)
                results = logic.search_code(args.repo_id, args.query, args.pattern)
                return [TextContent(type="text", text=json.dumps(results, indent=2))]
            elif name == "get_file_content":
                args = GetFileContentParams(**arguments)
                content = logic.get_file_content(args.repo_id, args.file_path)
                return [TextContent(type="text", text=content)]
            elif name == "extract_symbols":
                args = ExtractSymbolsParams(**arguments)
                symbols = logic.extract_symbols(
                    args.repo_id, args.file_path, args.symbol_type
                )
                return [TextContent(type="text", text=json.dumps(symbols, indent=2))]
            elif name == "find_symbol_usages":
                args = FindSymbolUsagesParams(**arguments)
                usages = logic.find_symbol_usages(
                    args.repo_id, args.symbol_name, args.file_path
                )
                return [TextContent(type="text", text=json.dumps(usages, indent=2))]
            elif name == "get_file_tree":
                args = GetFileTreeParams(**arguments)
                tree = logic.get_file_tree(
                    args.repo_id
                )
                return [TextContent(type="text", text=json.dumps(tree, indent=2))]
            elif name == "semantic_search":
                args = SemanticSearchParams(**arguments)
                results = logic.semantic_search(args.repo_id, args.query, args.limit)
                return [TextContent(type="text", text=json.dumps(results, indent=2))]
            elif name == "analyze_dependencies":
                args = AnalyzeDependenciesParams(**arguments)
                deps = logic.analyze_dependencies(
                    args.repo_id, args.file_path, args.depth
                )
                return [TextContent(type="text", text=json.dumps(deps, indent=2))]
            elif name == "get_documentation":
                args = GetDocumentationParams(**arguments)
                docs = logic.get_documentation(
                    args.repo_id, args.symbol_name, args.file_path
                )
                return [TextContent(type="text", text=json.dumps(docs, indent=2))]
            elif name == "get_code_summary":
                args = GetCodeSummaryParams(**arguments)
                summary = logic.get_code_summary(
                    args.repo_id, args.file_path, args.symbol_name
                )
                return [TextContent(type="text", text=json.dumps(summary, indent=2))]
            else:
                raise MCPError(code=INVALID_PARAMS, message=f"Unknown tool: {name}")
        except ValidationError as e:
            return [create_error_content(INVALID_PARAMS, str(e))]
        except MCPError as e:
            return [create_error_content(e.code, e.message)]
        except Exception as e:
            return [create_error_content(INTERNAL_ERROR, str(e))]
        
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return logic.list_tools()

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return logic.list_prompts()

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        return logic.get_prompt(name, arguments)

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
