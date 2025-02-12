# Deployment Instructions

This application is configured to be deployed on Vercel with both frontend and backend components.

## Prerequisites

1. A Vercel account
2. Vercel CLI installed (`npm i -g vercel`)
3. Your project pushed to a Git repository

## Environment Setup

1. Create the following environment variables in your Vercel project settings:

```bash
NEXT_PUBLIC_BACKEND_URL=/api  # For production
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1Ijoia2FzaW5hZGhzYXJtYSIsImEiOiJjbTY5NGJkcGMwNWY5Mmpxd2g2MXgxemloIn0.DRcazuU3mvV5Q2HIRXYoOA  # For map functionality
```

Note: The Mapbox token is required for the emergency response map to function properly.

## Deployment Steps

1. Login to Vercel CLI:
```bash
vercel login
```

2. Deploy the project:
```bash
vercel
```

3. Link your repository to Vercel for automatic deployments:
   - Go to Vercel dashboard
   - Import your repository
   - Configure the build settings using the existing vercel.json

## Important Notes

- The backend runs on Python 3.9 runtime
- Maximum Lambda size is set to 15MB
- Function timeout is set to 30 seconds
- Memory allocation is 3008MB for Python functions
- The frontend proxies API requests to the backend through the /api path

## Troubleshooting

1. If the backend fails to start, check the Vercel logs for Python package installation issues
2. Ensure all required dependencies are listed in requirements-vercel.txt
3. Monitor the backend health status in the dashboard
