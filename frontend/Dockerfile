FROM node:20-alpine

WORKDIR /app

# Dependency-only layer for caching.
COPY package.json package-lock.json ./
RUN npm ci

# Source (overlaid by the bind mount in docker-compose for dev).
COPY . .

EXPOSE 5173

# --host 0.0.0.0 so Vite binds to all interfaces and the host port mapping works.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
