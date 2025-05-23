FROM node:20-alpine

WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm node-gyp

COPY pnpm-lock.yaml package.json ./

# Install all dependencies (including devDependencies)
RUN pnpm install

COPY . .

# Expose the port for the Next.js development server
EXPOSE 3000

# Default environment variables for development
ENV NODE_ENV development
ENV AUTH_TRUST_HOST true

CMD ["pnpm", "dev"]