# Build stage
FROM node:16-alpine as build

# Set the working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dos2unix
RUN apk add --no-cache dos2unix

# Convert Windows line endings to Unix
RUN dos2unix package.json

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# Convert Windows line endings to Unix for all JS files
RUN find src -type f -name "*.js" -exec dos2unix {} \;

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
