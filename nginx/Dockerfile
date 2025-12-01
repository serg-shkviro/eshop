FROM node:20-alpine AS frontend-builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend .
RUN npm run build

FROM nginx:alpine

RUN apk add --no-cache openssl

COPY --from=frontend-builder /app/dist /usr/share/nginx/html
COPY nginx/nginx.prod.conf /etc/nginx/conf.d/default.conf
COPY nginx/generate-ssl.sh /docker-entrypoint.d/10-generate-ssl.sh

RUN chmod +x /docker-entrypoint.d/10-generate-ssl.sh && \
    mkdir -p /etc/nginx/ssl

EXPOSE 3000 8000

