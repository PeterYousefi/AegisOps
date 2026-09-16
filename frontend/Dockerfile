# AegisOps frontend — production-style multi-stage container image.
# Uses Next.js standalone output. Runs as a non-root user.

# ---- deps: install node_modules from the lockfile ----
FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ---- build: compile the Next.js app ----
FROM node:22-slim AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---- runtime: minimal image running the standalone server ----
FROM node:22-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

# Next.js standalone output bundles a minimal server + only needed deps.
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public

# Run as the built-in non-root `node` user.
USER node

EXPOSE 3000

CMD ["node", "server.js"]
