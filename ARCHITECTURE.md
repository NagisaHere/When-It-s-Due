# Architecture Overview

## Data Flow Options

### Option 1: Python API (Recommended) ✅

**Architecture:**
```
React Frontend (web/) 
    ↓ HTTP Requests
Flask API (api_server.py)
    ↓ Web Scraping
UQ ECP Website
    ↓ Returns JSON
React Frontend (displays deadlines)
```

**Pros:**
- ✅ Reuses existing Python scraping code
- ✅ No CORS issues (server-side scraping)
- ✅ More reliable and maintainable
- ✅ Can handle authentication, caching, rate limiting
- ✅ Easy to integrate with Google Tasks API later

**Cons:**
- ❌ Requires running a backend server
- ❌ More complex deployment

**Setup:**
1. Install Flask: `pip install flask flask-cors`
2. Run API: `python api_server.py` (runs on http://localhost:5000)
3. React frontend calls: `http://localhost:5000/api/deadlines`

---

### Option 2: JavaScript Web Scraping

**Architecture:**
```
React Frontend
    ↓ Direct HTTP Requests (CORS blocked!)
UQ ECP Website ❌
```

**Why it doesn't work:**
- ❌ **CORS (Cross-Origin Resource Sharing)** blocks direct browser requests to external domains
- ❌ UQ's website doesn't allow cross-origin requests from your domain
- ❌ Would need a proxy server anyway (defeats the purpose)

**Workarounds (not recommended):**
1. Browser extension (Chrome extension with permissions)
2. Proxy server (still need a backend)
3. CORS proxy services (unreliable, security concerns)

---

### Option 3: Hybrid Approach

Use a serverless function (Vercel, Netlify Functions, AWS Lambda) to run Python scraping code. This gives you:
- ✅ No need to manage a server
- ✅ Server-side scraping (no CORS)
- ✅ Scales automatically

---

## Recommended Implementation

**For development:** Use Flask API (Option 1)
**For production:** Consider serverless functions or a proper backend service

## API Endpoints

### `GET /api/offerings/<course_code>`
Returns available course offerings for a course code.

**Response:**
```json
{
  "offerings": [
    {
      "index": 0,
      "year": "2024",
      "ecp_url": "https://..."
    }
  ]
}
```

### `POST /api/deadlines`
Scrapes deadlines from an ECP URL.

**Request:**
```json
{
  "ecp_url": "https://...",
  "course_code": "CSSE1001"
}
```

**Response:**
```json
{
  "deadlines": [
    {
      "title": "Assignment 1",
      "due_date": "2024-03-15T14:00:00+00:00",
      "due_time": "2:00 pm",
      "due_date_display": "15/03/2024 2:00 pm"
    }
  ],
  "course_code": "CSSE1001"
}
```

## Next Steps

1. **Refactor `ecp_parse.py`** to be more modular (separate functions for each step)
2. **Update React frontend** to call the API endpoints
3. **Add error handling** and loading states
4. **Add Google Tasks integration** (optional, can be done client-side or server-side)


