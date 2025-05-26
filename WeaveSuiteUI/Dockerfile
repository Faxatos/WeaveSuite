FROM node:20-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 make g++ && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm

# Setup workdir and permissions
WORKDIR /app
RUN chown node:node /app

# Copy dependency files
COPY --chown=node:node pnpm-lock.yaml package.json ./

# Switch to non-root user
USER node

# Install all dependencies (including devDependencies)
RUN pnpm install

# Copy application code
COPY --chown=node:node . .

# Build the project (requires devDependencies)
RUN pnpm build

# Remove devDependencies after build
RUN pnpm install --prod

# Environment variables
ENV NODE_ENV=production
ENV AUTH_TRUST_HOST=true

EXPOSE 3000
CMD ["pnpm", "start"]