# Development Plan — LMS Telegram Bot

## Overview

This document outlines the plan for building a Telegram bot that integrates with the LMS backend. The bot allows users to check system health, browse labs and scores, and ask questions in plain language using an LLM for intent routing.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point** (`bot.py`) — Handles Telegram connection and `--test` mode
2. **Handlers** (`handlers/`) — Pure functions that process commands and return text
3. **Services** (`services/`) — API client for LMS backend, LLM client for intent routing
4. **Configuration** (`config.py`) — Environment variable loading

This separation means handlers can be tested without Telegram, making development and debugging much easier.

## Task 1: Scaffold

**Status:** ✅ Completed

**Goal:** Create project structure with testable handlers and `--test` mode.

- Create `bot/` directory with handlers, services, config
- Implement placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Add `--test` mode to call handlers directly without Telegram
- Create `pyproject.toml` with dependencies (aiogram, python-dotenv, httpx)

**Acceptance:** `uv run bot.py --test "/start"` prints a welcome message and exits 0.

## Task 2: Backend Integration

**Status:** ✅ Completed

**Goal:** Connect handlers to the LMS backend API.

**Implementation:**

- Created `services/api_client.py` with `LMSClient` class
- Uses `httpx` for HTTP requests with Bearer token authentication
- Implemented `/health` — calls `GET /items/` to verify backend health
- Implemented `/labs` — fetches and displays labs from backend
- Implemented `/scores <lab>` — fetches pass rates from `GET /analytics/pass-rates?lab=`
- Error handling shows actual error (e.g., "Connection refused") without raw tracebacks

**Acceptance:** Commands return real data from the backend. Backend down produces a friendly error message.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Allow users to ask questions in plain language.

- Create LLM client service
- Define tool descriptions for all backend endpoints
- Implement intent router that uses LLM to decide which tool to call
- Handle multi-step reasoning (e.g., "How am I doing?" → fetch labs → fetch scores)

**Acceptance:** Plain text like "what labs are available" triggers the same logic as `/labs`.

## Task 4: Containerize and Deploy

**Goal:** Deploy the bot alongside the backend on the VM.

- Create `Dockerfile` for the bot
- Add bot service to `docker-compose.yml`
- Configure Docker networking (containers use service names, not localhost)
- Document deployment process in README

**Acceptance:** Bot runs in Docker and responds to Telegram messages.

## Testing Strategy

- **Unit tests** — Test handlers in isolation (no Telegram, no network)
- **Integration tests** — Test API client with backend
- **Manual testing** — Use `--test` mode during development
- **E2E testing** — Deploy and test in Telegram

## Environment Variables

- `BOT_TOKEN` — Telegram bot token from @BotFather
- `LMS_API_URL` — Backend URL (e.g., `http://localhost:42002`)
- `LMS_API_KEY` — Backend API key for authentication
- `LLM_API_KEY` — LLM API key for intent routing
- `LLM_API_BASE_URL` — LLM API base URL
- `LLM_API_MODEL` — LLM model name

## Git Workflow

For each task:

1. Create a Git issue describing the work
2. Create a branch: `task-1-scaffold`
3. Implement and test locally with `--test` mode
4. Create a PR referencing the issue: `Closes #...`
5. Partner review
6. Merge to main
