# AI-Powered bbmodel Generator

A scalable, user-friendly application that leverages artificial intelligence to generate bbmodel (Blockbench) models complete with animations and textures from natural language prompts. The platform includes a subscription system, social features, and a community marketplace.

## Project Overview

The AI-Powered bbmodel Generator is designed for 3D artists, game developers, modders (e.g., Minecraft modding communities), and creative hobbyists seeking rapid prototyping and model generation. It allows users to describe the 3D model they want to create, and the AI will generate a complete bbmodel file compatible with Blockbench.

## Core Features

- **Prompt-Based Generation**: Users submit descriptive prompts to generate 3D models.
- **Model Output**: Generate models in the bbmodel format compatible with Blockbench.
- **Animations**: Automatically create simple or complex animations based on prompt details.
- **Textures**: AI-generated textures applied to model surfaces.
- **Interactive UI**: A modern, responsive UI that allows previewing, editing, and fine-tuning.
- **Integration**: Import/export features with Blockbench for further refinement.
- **Scalability**: A microservices architecture to support high user concurrency and evolving feature sets.

## Enhanced Features

### Subscription & Monetization
- **Token System**: Virtual tokens for generating models with different complexity levels
- **Tiered Subscriptions**: Basic, Pro, and Enterprise plans with varying token allocations
- **One-Time Purchases**: Option to buy additional tokens without a subscription
- **Usage Tracking**: Dashboard showing token usage and transaction history

### Social & Community
- **Public Gallery**: Browse and discover models shared by the community
- **Likes & Comments**: Engage with other creators' work
- **Follow System**: Follow favorite creators and get updates on their new models
- **Notifications**: Real-time notifications for social interactions
- **Profile Customization**: Personalized user profiles with avatars and bios

### Sharing & Discovery
- **Visibility Controls**: Set models as private, public, or unlisted
- **Tagging System**: Categorize models with tags for better discoverability
- **Search Functionality**: Find models by keywords, tags, or creators
- **Analytics**: Track views, likes, and downloads of your shared models

## Project Structure

The project is organized into two main components:

### Backend (FastAPI)

The backend is built with FastAPI and provides the following features:

- User authentication and management
- Model generation using AI
- API endpoints for model management
- Storage and retrieval of generated models
- Subscription and token management
- Social features (likes, comments, follows)
- Notification system

### Frontend (React)

The frontend is built with React and provides the following features:

- User registration and login
- Model generation interface
- Model preview and management
- Dashboard for viewing and managing models
- Subscription management
- Social interactions
- Community gallery

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- PostgreSQL database
- Docker (optional, for containerization)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bbmodel-ai-generator.git
   cd bbmodel-ai-generator
   ```

2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```
   cd ../frontend
   npm install
   ```

### Running the Application

#### Development Mode

1. Start the backend server:
   ```
   cd backend
   python run.py
   ```

2. Start the frontend development server:
   ```
   cd frontend
   npm start
   ```

3. Open your browser and navigate to:
   - Frontend: http://localhost:59555
   - Backend API: http://localhost:53006/api

#### Using Docker Compose

```
docker-compose up -d
```

### Deployment

For production deployment, use the provided deployment script:

```
sudo ./deploy.sh
```

This script will:
1. Install all necessary dependencies
2. Configure Nginx as a reverse proxy
3. Set up SSL certificates with Let's Encrypt
4. Deploy the application using Docker Compose
5. Initialize the database with default data

## API Documentation

Once the backend is running, you can access the API documentation at:
http://localhost:53006/docs

## Database Schema

The application uses PostgreSQL with the following main tables:
- Users
- UserProfiles
- Models
- Tags
- Subscriptions
- UserSubscriptions
- TokenTransactions
- Likes
- Comments
- Follows
- Notifications

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Blockbench for their amazing 3D modeling tool
- The open-source AI community for their contributions to model generation