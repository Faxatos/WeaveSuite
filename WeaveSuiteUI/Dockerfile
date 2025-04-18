FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

#copy the rest of the application
COPY . .

EXPOSE 3000

#set development environment
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

#start the development server with hot reloading
CMD ["npm", "run", "dev"]