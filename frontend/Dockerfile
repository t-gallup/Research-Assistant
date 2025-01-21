FROM node:18-alpine

WORKDIR /app

# Copy frontend files
COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm run build

# Serve the app
CMD ["npm", "start"] 