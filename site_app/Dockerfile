# syntax=docker/dockerfile:1.7

FROM oven/bun:1.2.5-alpine AS base
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

FROM base AS deps
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN bun run db:generate && bun run build

FROM oven/bun:1.2.5-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
# Override this in your deployment platform if needed.
ENV DATABASE_URL=file:./db/custom.db

RUN addgroup -S nextjs && adduser -S nextjs -G nextjs

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
COPY --from=builder /app/db ./db

RUN chown -R nextjs:nextjs /app
USER nextjs

EXPOSE 3000

CMD ["bun", "server.js"]
