FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN chown -R node:node /app
USER node

EXPOSE 8080
CMD ["npm", "run", "serve", "--", "--port", "8080", "--host", "0.0.0.0"]
