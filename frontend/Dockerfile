# --- ETAPA 1: Construcción del Frontend ---
FROM node:20-alpine AS build-stage

WORKDIR /app

# Argumentos de entorno para compilación
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

ARG VITE_GOOGLE_CLIENT_ID
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

# Copiar manifiestos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --no-audit --prefer-offline || npm install

# Copiar código fuente
COPY . .

# Compilar SPA de producción
RUN npm run build

# --- ETAPA 2: Servidor Web Nginx de Producción ---
FROM nginx:alpine AS production-stage

# Copiar archivos compilados
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto HTTP estándar
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
