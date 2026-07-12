"""RunningHub Standard Model API client.

Covers the text-to-image submit + query workflow.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

API_HOST = os.environ.get("RUNNINGHUB_API_HOST", "www.runninghub.cn")
BASE_URL = f"https://{API_HOST}"
DEFAULT_TIMEOUT = 60.0
POLL_TIMEOUT = 600.0


def _api_key(key: str | None = None) -> str:
    k = key or os.environ.get("RUNNINGHUB_API_KEY", "")
    if not k:
        raise ValueError(
            "RUNNINGHUB_API_KEY is not set. "
            "Set the environment variable or pass api_key directly."
        )
    return k


async def text_to_image(
    prompt: str,
    *,
    api_key: str | None = None,
    width: int | None = None,
    height: int | None = None,
    sequential_image_generation: str | None = None,
    max_images: int | None = None,
    tools_type: str | None = None,
) -> dict[str, Any]:
    """Submit a text-to-image task to seedream-v5-lite.

    Returns the task submission response containing taskId.
    """
    key = _api_key(api_key)
    payload: dict[str, Any] = {"prompt": prompt}
    if width is not None:
        payload["width"] = width
    if height is not None:
        payload["height"] = height
    if sequential_image_generation is not None:
        payload["sequentialImageGeneration"] = sequential_image_generation
    if max_images is not None:
        payload["maxImages"] = max_images
    if tools_type is not None:
        payload["toolsType"] = tools_type

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.post(
            f"{BASE_URL}/openapi/v2/seedream-v5-lite/text-to-image",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def query_task(
    task_id: str,
    *,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Query the status and results of a task via /openapi/v2/query.

    Returns the full response including status, results, usage info.
    Status values: QUEUED, RUNNING, SUCCESS, FAILED
    """
    key = _api_key(api_key)
    payload = {"taskId": task_id}

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.post(
            f"{BASE_URL}/openapi/v2/query",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def run_text_to_image(
    prompt: str,
    *,
    api_key: str | None = None,
    width: int | None = None,
    height: int | None = None,
    sequential_image_generation: str | None = None,
    max_images: int | None = None,
    tools_type: str | None = None,
    poll_interval: float = 3.0,
    timeout: float = POLL_TIMEOUT,
) -> dict[str, Any]:
    """Submit a text-to-image task and poll until completion (or timeout).

    Returns the final response when SUCCESS or FAILED.
    """
    import asyncio

    submit_resp = await text_to_image(
        prompt,
        api_key=api_key,
        width=width,
        height=height,
        sequential_image_generation=sequential_image_generation,
        max_images=max_images,
        tools_type=tools_type,
    )

    task_id = submit_resp.get("taskId", "")
    if not task_id:
        return submit_resp

    elapsed = 0.0
    while elapsed < timeout:
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

        query_resp = await query_task(task_id, api_key=api_key)
        status = query_resp.get("status", "")

        if status == "SUCCESS":
            return query_resp
        if status == "FAILED":
            return query_resp

    return {"taskId": task_id, "status": "TIMEOUT", "errorMessage": f"Polling timed out after {timeout}s"}
