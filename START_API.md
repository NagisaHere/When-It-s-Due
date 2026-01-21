# Quick Start Guide

## Running the API Server Locally

1. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

2. **Start the Flask API server**:
```bash
python api_server.py
```

The API will run on `http://localhost:5000`

3. **In a separate terminal, start the React frontend**:
```bash
cd web
npm install  # if first time
npm run dev
```

The frontend will run on `http://localhost:5173` (or another port if 5173 is taken)

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/offerings/<course_code>` - Get available course offerings
- `POST /api/deadlines` - Get deadlines for a specific ECP URL
- `GET /api/course/<course_code>` - Get deadlines for a course (auto-selects first offering)

## Usage

1. Open the React app in your browser
2. Enter a course code (e.g., "CSSE1001")
3. Click "Go" or press Enter
4. The deadlines will be displayed in a table format matching the Figma design

## Example Course Codes

- CSSE1001
- COMP1100
- MATH1051
- Any valid UQ course code


