# Knowledge Base Assistant Frontend

This is the frontend application for the Knowledge Base Assistant project, built with React, TypeScript, and Tailwind CSS.

## Features

1. User authentication (login/logout)
2. Chat interface with message history
3. File upload functionality for documents (DOCX, XLSX, etc.)
4. Responsive design that works on desktop and mobile

## Tech Stack

- React 18 with TypeScript
- Tailwind CSS for styling
- React Router for navigation
- Axios for HTTP requests
- Vite for build tooling

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn package manager

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at http://localhost:3000.

## Project Structure

```
src/
├── components/     # Reusable UI components
├── hooks/          # Custom React hooks
├── pages/          # Page components
├── services/       # API service layer
├── App.tsx         # Main app component with routing
├── main.tsx        # Entry point
└── index.css       # Global styles
```

## Development

The frontend is configured to proxy API requests to the backend server running on http://localhost:8000.
This is configured in the `vite.config.ts` file.

## Building for Production

To create a production build:

```bash
npm run build
```

The output will be in the `dist` folder.

## Deployment

You can deploy the frontend to any static hosting service (Netlify, Vercel, GitHub Pages, etc.)
after building the project.