import json
import asyncio
from enum import Enum
from pathlib import Path
from typing import *
from ast import literal_eval

import rich.progress
import typer
from pydantic import Field, create_model
from rich import box
from rich.console import Console
from rich.panel import Panel

from langbridge.handlers import OpenAiGenerationHandler
from langbridge.settings import get_openai_settings
from langbridge.utils import get_logger


console = Console(width=100)

_logger = get_logger()
_openai_settings = get_openai_settings()


class ApiService(str, Enum):
    openai = "openai"


def generation(
    service: ApiService = typer.Option(default=ApiService.openai),
    model: str = typer.Option(help="Name of model to use for API calls"),
    infile: Path = typer.Option(help="Path to a `jsonl` file containing the input texts and optional metadata",
                                exists=True),
    outfile: Path = typer.Option(help="Path to a `jsonl` file to write the outputs to"),
    prompt_file: Path = typer.Option(default=None, help="Path to file containing the prompt", exists=True),
    response_format_file: Path = typer.Option(default=None, help="Path to file containing the response format json",
                                              exists=True),
    model_parameters: str = typer.Option(callback=literal_eval),
    max_requests_per_minute: int = typer.Option(default=100, help="Maximum number of requests per minute"),
    max_tokens_per_minute: int = typer.Option(default=39500, help="Maximum number of tokens per minute"),
    max_attempts_per_request: int = typer.Option(default=5, help="Maximum number of attempts per request"),
):
    """
    This method is responsible for processing requests using the specified model via API calls. It reads input texts and
    optional metadata from a provided .jsonl file and builds a list of generations using the provided prompt and response format files.

    Args:
        service: The name of the LLM Service to be used for generations. Currently only `openai` is supported.
        model: Name of the model to use for API calls (default is None).
        infile: Path to a .jsonl file containing the input texts and optional metadata. The file must exist.
        outfile: Path to a .jsonl file where the outputs will be written.
        prompt_file: Path to a file containing the prompt, if exists.
        response_format_file: Path to a .jsonl file containing the response format json, if exists.
        model_parameters: Model parameters to be included in the API call.
        max_requests_per_minute: Maximum number of requests per minute (default is 100).
        max_tokens_per_minute: Maximum number of tokens per minute (default is 39500).
        max_attempts_per_request: Maximum number of attempts per request (default is 5).
    """
    if not isinstance(model_parameters, dict):
        raise ValueError("The parameter `model_parameters` must be passed as a JSON String")

    console.print(
        Panel(
            "[bold]Welcome to the OpenAI Processor CLI![/bold]", box=box.DOUBLE,
        )
    )

    with rich.progress.open(infile, "r", description="Reading input file...", console=console) as f:
        lines: List[dict] = [
            json.loads(line.strip())
            for line in f.readlines()
        ]

    with rich.progress.open(prompt_file, "r", description="Reading prompt file...", console=console) as pf:
        prompt = pf.read()

    response_model = None
    if response_format_file:
        with rich.progress.open(response_format_file, "r", description="Reading response schema...",
                                console=console) as schema_file:
            schema = json.load(schema_file)

        fields = {
            field_name: (
                eval(properties["type"]),
                Field(
                    default=properties.get("default", None),
                    description=properties["description"]
                )
            )
            for field_name, properties in schema.items()
        }

        response_model = create_model(
            "ResponseModel",
            **fields
        )

    handler = OpenAiGenerationHandler(
        model=model,
        model_parameters=model_parameters,
        inputs=lines,
        base_prompt=prompt,
        response_model=response_model,
        max_requests_per_minute=max_requests_per_minute,
        max_tokens_per_minute=max_tokens_per_minute,
        max_attempts_per_request=max_attempts_per_request
    )

    _ = typer.confirm(
        f"{len(lines)} requests are scheduled, "
        f"collectively containing {handler.approximate_tokens} tokens."
        f"Total approximate cost is ${round(handler.approximate_cost, 2)}."
        f" Proceed?",
        abort=True
    )
    with rich.progress.Progress(
        rich.progress.SpinnerColumn(),
        rich.progress.TextColumn("[progress.description]{task.description}"),
        rich.progress.TimeElapsedColumn(),
        console=console
    ) as progress:
        progress.add_task(description="Initiating API calls and waiting for responses...")
        asyncio.run(
            handler.execute(outfile=outfile)
        )

    _logger.info("All responses have been written.")