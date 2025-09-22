# Development container with both Node.js and Python
FROM mcr.microsoft.com/devcontainers/base:bullseye

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install Python 3.9 and dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    postgresql-client \
    redis-tools \
    git \
    curl \
    wget \
    vim \
    nano \
    htop \
    tree \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.9 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Install global npm packages
RUN npm install -g \
    typescript \
    ts-node \
    nodemon \
    prettier \
    eslint \
    @vitejs/plugin-react

# Install global Python packages
RUN python -m pip install --upgrade pip \
    && pip install \
    black \
    flake8 \
    pylint \
    pytest \
    jupyter

# Create workspace directory
WORKDIR /workspace

# Copy package.json files if they exist (for faster rebuilds)
COPY ["frontend/package*.json", "./frontend/"] 2>/dev/null || true
COPY ["backend/requirements*.txt", "./backend/"] 2>/dev/null || true

# Install dependencies if package files exist
RUN if [ -f "./frontend/package.json" ]; then \
        cd frontend && npm install; \
    fi

RUN if [ -f "./backend/requirements.txt" ]; then \
        cd backend && python -m venv venv && \
        . venv/bin/activate && \
        pip install -r requirements.txt; \
    fi

# Set up git safe directory
RUN git config --global --add safe.directory /workspace

# Expose ports
EXPOSE 3000 5000 5432 6379

CMD ["sleep", "infinity"]