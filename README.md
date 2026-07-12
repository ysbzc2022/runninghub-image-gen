# RunningHub Image Gen MCP Plugin

A Codex MCP plugin for generating images via RunningHub's seedream-v5-lite model.

## Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) package manager
- A RunningHub API key (set as `RUNNINGHUB_API_KEY`)

## Install

```bash
cd work/runninghub-image-gen
uv sync
```

## Usage

### Environment variable

```bash
export RUNNINGHUB_API_KEY=your-api-key-here
```

### Tools

| Tool | Description |
|------|-------------|
| `text_to_image` | Submit a text-to-image task, returns taskId |
| `query_task` | Poll task status/results by taskId |
| `run_text_to_image` | Submit + poll until complete |

### Available parameters

- `prompt` (required) — Text description of the image
- `width` / `height` — Image dimensions in pixels
- `max_images` — Number of images to generate
- `sequential_image_generation` — "enabled" or "disabled"
- `tools_type` — e.g. "web_search"

### Running standalone

```bash
RUNNINGHUB_API_KEY=your-key uv run runninghub-image-gen
```

## API

- Submit: `POST /openapi/v2/seedream-v5-lite/text-to-image`
- Query:  `POST /openapi/v2/query`
