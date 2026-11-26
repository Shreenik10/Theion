# OSCE Simulation Web App Frontend

A modern web-based frontend for the OSCE (Objective Structured Clinical Examination) simulation application. Built with React, TypeScript, and Tailwind CSS.

## Features

- Patient configuration with customizable traits and difficulty levels
- Real-time chat interface for patient-doctor interaction
- Comprehensive evaluation feedback
- Responsive design for all screen sizes

## Prerequisites

- Node.js 16.x or later
- npm 7.x or later

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Development

The application is structured into three main components:

1. **PatientSetup**: Configures the simulated patient's characteristics
2. **ExamPage**: Handles the real-time chat interaction
3. **EvaluationPage**: Displays the evaluation results

## API Integration

The frontend communicates with a FastAPI backend through the following endpoints:

- `POST /api/patient`: Create a new patient session
- `POST /api/chat`: Send and receive chat messages
- `POST /api/submit`: Submit the case for evaluation
- `GET /api/evaluate/{session_id}`: Get evaluation results

## Styling

The application uses Tailwind CSS for styling with custom component classes defined in `src/index.css`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
