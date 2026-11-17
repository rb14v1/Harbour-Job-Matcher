FROM node:22-alpine AS build
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:22-alpine AS dev
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN chown -R node:node /app
EXPOSE 8080
USER node
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
RUN sed -i 's#^pid .*#pid /tmp/nginx.pid;#' /etc/nginx/nginx.conf && grep -q '^pid /tmp/nginx.pid;' /etc/nginx/nginx.conf
RUN mkdir -p /tmp/nginx-cache && chown -R nginx:nginx /tmp/nginx-cache /var/cache/nginx && printf 'server {\n  listen 8080;\n  listen [::]:8080;\n  server_name _;\n  client_body_temp_path /tmp/nginx-cache/client_temp;\n  proxy_temp_path /tmp/nginx-cache/proxy_temp;\n  fastcgi_temp_path /tmp/nginx-cache/fastcgi_temp;\n  uwsgi_temp_path /tmp/nginx-cache/uwsgi_temp;\n  scgi_temp_path /tmp/nginx-cache/scgi_temp;\n  root /usr/share/nginx/html;\n  index index.html;\n  location / {\n    try_files $uri /index.html;\n  }\n}\n' > /etc/nginx/conf.d/default.conf
USER nginx
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
