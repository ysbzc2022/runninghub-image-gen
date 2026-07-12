"""RunningHub Image Gen MCP Server.

Exposes text-to-image tools via FastMCP for the RunningHub
seedream-v5-lite model.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP

from . import client

mcp = FastMCP(
    name="RunningHub Image Gen",
    instructions=(
        "RunningHub text-to-image MCP plugin. "
        "Uses the seedream-v5-lite model to generate images from text prompts. "
        "Submit a task with a prompt, then poll for results. "
        "Requires RUNNINGHUB_API_KEY environment variable."
    ),
)


@mcp.tool(
    description=(
        "Submit a text-to-image generation task to RunningHub (seedream-v5-lite). "
        "Returns a taskId that can be used with query_task to get results. "
        "Images are submitted asynchronously; use query_task to poll for completion."
    ),
    tags={"runninghub", "text-to-image"},
)
async def text_to_image(
    prompt: Annotated[str, "Text prompt describing the image to generate"],
    width: Annotated[
        int | None, "Image width in pixels (e.g. 1024, 2048)"
    ] = None,
    height: Annotated[
        int | None, "Image height in pixels (e.g. 1024, 2048)"
    ] = None,
    sequential_image_generation: Annotated[
        str | None, "Enable sequential generation: 'enabled' or 'disabled'"
    ] = None,
    max_images: Annotated[
        int | None, "Maximum number of images to generate (e.g. 1, 4)"
    ] = None,
    tools_type: Annotated[
        str | None, "Tools type, e.g. 'web_search'"
    ] = None,
) -> dict[str, Any]:
    """Submit a text-to-image generation task."""
    return await client.text_to_image(
        prompt,
        width=width,
        height=height,
        sequential_image_generation=sequential_image_generation,
        max_images=max_images,
        tools_type=tools_type,
    )


@mcp.tool(
    description=(
        "Query the status and results of a previously submitted task. "
        "Use the taskId returned by text_to_image. "
        "Status values: QUEUED (waiting), RUNNING (processing), "
        "SUCCESS (completed, results available), FAILED (error occurred). "
        "When SUCCESS, results contains image URLs in the 'url' field."
    ),
    tags={"runninghub", "query"},
)
async def query_task(
    task_id: Annotated[str, "Task ID returned by text_to_image"],
) -> dict[str, Any]:
    """Query task status and results."""
    return await client.query_task(task_id)


@mcp.tool(
    description=(
        "Submit a text-to-image task and poll until completion. "
        "Combines text_to_image + query_task polling into one call. "
        "Returns immediately with image URLs when SUCCESS, "
        "or status details if FAILED or TIMEOUT. "
        "Default timeout is 10 minutes."
    ),
    tags={"runninghub", "text-to-image", "workflow"},
)
async def run_text_to_image(
    prompt: Annotated[str, "Text prompt describing the image to generate"],
    width: Annotated[
        int | None, "Image width in pixels (e.g. 1024, 2048)"
    ] = None,
    height: Annotated[
        int | None, "Image height in pixels (e.g. 1024, 2048)"
    ] = None,
    sequential_image_generation: Annotated[
        str | None, "Enable sequential generation: 'enabled' or 'disabled'"
    ] = None,
    max_images: Annotated[
        int | None, "Maximum number of images to generate (e.g. 1, 4)"
    ] = None,
    tools_type: Annotated[
        str | None, "Tools type, e.g. 'web_search'"
    ] = None,
    poll_interval: Annotated[
        float, "Polling interval in seconds between status checks"
    ] = 3.0,
    timeout: Annotated[
        float, "Maximum wait time in seconds before timing out"
    ] = 600.0,
) -> dict[str, Any]:
    """Submit and wait for a text-to-image task."""
    return await client.run_text_to_image(
        prompt,
        width=width,
        height=height,
        sequential_image_generation=sequential_image_generation,
        max_images=max_images,
        tools_type=tools_type,
        poll_interval=poll_interval,
        timeout=timeout,
    )


def main() -> None:
    """MCP server entry point."""
    mcp.run()


if __name__ == "__main__":
    main()
