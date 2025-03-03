# EXIF Checker API

A production-ready FastAPI backend for extracting and analyzing EXIF metadata from images, with special support for Fujifilm recipes.

## Features

- Extract complete EXIF metadata from images
- Extract Fujifilm recipe information from Fujifilm images
- Generate filename proposals based on EXIF data
- Batch process multiple images at once
- API rate limiting for security
- Containerized for easy deployment
- Production-ready with Gunicorn

## Requirements

- Python 3.8+
- ExifTool (must be installed on the system)
- Docker (optional, for containerized deployment)

## Quick Start

### Local Development

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/exif-checker-api.git
   cd exif-checker-api
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure ExifTool is installed:
   - On Ubuntu/Debian: `sudo apt-get install libimage-exiftool-perl`
   - On macOS with Homebrew: `brew install exiftool`
   - On Windows: Download from [ExifTool website](https://exiftool.org/) and add to PATH

5. Create a `.env` file (or copy from `.env.example`):
   ```
   HOST=0.0.0.0
   PORT=8000
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   MAX_FILE_SIZE=10
   TEMP_DIR=temp_uploads
   LOG_LEVEL=INFO
   ```

6. Run the development server:
   ```bash
   python run.py --reload
   ```

7. Access the API documentation at http://localhost:8000/docs

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t exif-checker-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env exif-checker-api
   ```

3. Access the API at http://localhost:8000

## Production Deployment

For production deployment, we use Gunicorn as the WSGI server with Uvicorn workers:

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Heroku Deployment

This application is ready for Heroku deployment:

1. Create a Heroku app:
   ```bash
   heroku create your-app-name
   ```

2. Add the ExifTool buildpack:
   ```bash
   heroku buildpacks:add https://github.com/bobwol/heroku-buildpack-exiftool
   heroku buildpacks:add heroku/python
   ```

3. Configure environment variables:
   ```bash
   heroku config:set ALLOWED_ORIGINS=https://your-frontend-app.com,http://localhost:3000
   heroku config:set MAX_FILE_SIZE=10
   ```

4. Deploy:
   ```bash
   git push heroku main
   ```

## API Endpoints

### Health Endpoints

- `GET /` - Root endpoint to verify API is running
- `GET /health` - Health check endpoint to verify dependencies

### EXIF Endpoints

- `POST /api/v1/exif/analyze` - Analyze EXIF data from an uploaded image
- `POST /api/v1/exif/fuji` - Extract Fujifilm recipe data from a Fujifilm image
- `POST /api/v1/exif/batch` - Batch process multiple images for EXIF data
- `POST /api/v1/exif/rename` - Generate a filename proposal based on EXIF data

## React Frontend Integration

To integrate with a React frontend:

1. Configure CORS by updating the `ALLOWED_ORIGINS` in your `.env` file to include your React app's URL
2. Use the API endpoints from your React app using `fetch` or Axios

Example React code:

```javascript
// Example using the /api/v1/exif/analyze endpoint
async function analyzeImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/exif/analyze', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze image');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error;
  }
}
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 