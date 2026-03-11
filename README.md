# Age Detector

A tool to detect if people in images are underage (under 18). Supports CLI and HTTP API for n8n integration.

## Features

- Face detection using OpenCV (Haar Cascade or DNN)
- Age estimation using Caffe model
- CLI tool for single/batch image processing
- HTTP API server for n8n integration
- JSON output and visualization support
- Docker deployment ready

## Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/age-detector.git
cd age-detector

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Download age estimation models
python download_models.py
```

## Usage

### CLI

```bash
# Check a single image
python3 -m age_detector check image.jpg

# Batch process a directory
python3 -m age_detector check ./images/ --output results.json

# With visualization
python3 -m age_detector check image.jpg --visualize --output results.json
```

### HTTP API

```bash
# Start the API server
python3 -m age_detector.api --port 5000
```

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/check` | POST | Check image (JSON body) |
| `/check/file` | POST | Check uploaded file |

#### POST /check Request Body

**Option 1: Base64 Image**
```json
{
  "image": "base64_encoded_image_data"
}
```

**Option 2: Image URL**
```json
{
  "url": "https://example.com/image.jpg"
}
```

#### Response

```json
{
  "success": true,
  "faces_detected": 1,
  "underage_count": 0,
  "results": [
    {
      "face_id": 1,
      "bbox": [100, 150, 200, 250],
      "age_interval": "(25-32)",
      "estimated_age": 28.5,
      "is_under_18": false,
      "confidence": 0.85
    }
  ]
}
```

## n8n Integration

### Using HTTP Request Node

1. **Method**: `POST`
2. **URL**: `http://your-server:5000/check`
3. **Body Content Type**: `JSON`
4. **Body**:
   ```json
   {
     "url": "{{$json.imageUrl}}"
   }
   ```

### Example n8n Workflow

```
[Webhook] → [HTTP Request: Age Detection] → [IF: Underage?] → [Actions]
```

## Deployment

### Docker

```bash
# Build the image
docker build -t age-detector .

# Run the container
docker run -p 5000:5000 age-detector
```

### Docker Compose

```bash
# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Cloud Deployment

#### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt && python download_models.py`
4. Set start command: `python -m age_detector.api --host 0.0.0.0 --port $PORT`

#### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and deploy
fly auth login
fly launch
fly deploy
```

## Age Intervals

The model estimates age in the following intervals:

- (0-2), (4-6), (8-12), (15-20), (21-24), (25-32), (38-43), (48-53), (60-100)

A person is considered **underage** if the midpoint of the predicted interval is less than 18.

## Visualization

- **Green box**: Person is 18 or older (adult)
- **Red box**: Person is under 18 (underage)

## Project Structure

```
age-detector/
├── age_detector/
│   ├── __init__.py
│   ├── __main__.py
│   ├── detector.py       # Face detection module
│   ├── age_estimator.py  # Age estimation module
│   ├── cli.py            # Command-line interface
│   └── api.py            # HTTP API server
├── models/
│   ├── age_deploy.prototxt
│   └── age_net.caffemodel (downloaded)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── setup.py
├── download_models.py
└── README.md
```

## License

MIT License
