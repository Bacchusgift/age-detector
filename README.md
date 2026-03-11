# Age Checker

A command-line tool to detect if people in images are underage (under 18).

## Features

- Face detection using OpenCV (Haar Cascade or DNN)
- Age estimation using OpenCV DNN with Caffe model
- Support for single image and batch processing
- JSON output support
- Visualization of detection results

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/age-checker.git
cd age-checker

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Download age estimation models (automatically done on first use, or run manually)
python download_models.py
```

## Model Files

The tool requires two model files in the `models/` directory:

1. **age_net.caffemodel** - Pre-trained Caffe model for age estimation
2. **age_deploy.prototxt** - Model architecture definition

Run `python download_models.py` to download them automatically, or download manually from:
- [tkim602/age-gender-prediction-opencv](https://github.com/tkim602/age-gender-prediction-opencv/tree/main/AgeGender)

## Usage

### Check a single image

```bash
# Basic usage
python -m age_checker check image.jpg

# Or using the installed command
age-checker check image.jpg
```

### Batch processing

```bash
# Process all images in a directory
age-checker check ./images/
```

### Save results to JSON

```bash
age-checker check ./images/ --output results.json
```

### Visualize results

```bash
# Show visualization window (requires display)
age-checker check image.jpg --visualize

# Save visualization images (when --output is specified)
age-checker check image.jpg --visualize --output results.json
```

## Output Format

The tool outputs JSON with the following structure:

```json
{
  "summary": {
    "total_images": 1,
    "total_faces": 2,
    "total_underage": 1
  },
  "results": [
    {
      "image": "test.jpg",
      "faces_detected": 2,
      "underage_count": 1,
      "results": [
        {
          "face_id": 1,
          "bbox": [100, 150, 200, 250],
          "age_interval": "(15-20)",
          "estimated_age": 17.5,
          "is_under_18": true,
          "confidence": 0.85
        },
        {
          "face_id": 2,
          "bbox": [300, 150, 400, 250],
          "age_interval": "(25-32)",
          "estimated_age": 28.5,
          "is_under_18": false,
          "confidence": 0.72
        }
      ]
    }
  ]
}
```

## Age Intervals

The model estimates age in the following intervals:

- (0-2), (4-6), (8-12), (15-20), (21-24), (25-32), (38-43), (48-53), (60-100)

A person is considered **underage** if the midpoint of the predicted interval is less than 18.

## Visualization

- **Green box**: Person is 18 or older (adult)
- **Red box**: Person is under 18 (underage)

## Technical Details

- **Face Detection**: Uses OpenCV Haar Cascade (built-in, no download required)
  - Optionally supports OpenCV DNN face detector if model files are present
- **Age Estimation**: Uses Caffe model with OpenCV DNN module
- **Underage Detection**: Based on age interval midpoint < 18

## Project Structure

```
age-checker/
├── age_checker/
│   ├── __init__.py
│   ├── __main__.py
│   ├── detector.py       # Face detection module
│   ├── age_estimator.py  # Age estimation module
│   └── cli.py            # Command-line interface
├── models/
│   ├── age_net.caffemodel
│   └── age_deploy.prototxt
├── requirements.txt
├── setup.py
├── download_models.py
└── README.md
```

## Limitations

- Age estimation accuracy depends on the pre-trained model
- Face detection works best with frontal faces
- Lighting and image quality affect detection accuracy

## License

MIT License
