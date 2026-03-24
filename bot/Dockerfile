FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy pyproject.toml and uv.lock for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync --frozen (locked versions)
RUN uv sync --frozen

# Copy bot source code
COPY . .

# Set PYTHONPATH to include /app for imports
ENV PYTHONPATH=/app

# Run the bot
CMD ["uv", "run", "bot.py"]
