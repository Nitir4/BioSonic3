# Standard React Build stage
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage with Nginx for standalone frontend serving
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Standard Nginx port
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
