# Troubleshooting: "No ECP available for this course"

## Potential Reasons

When you get the error "No ECP available for this course" for a valid course code like CSSE2010, here are the most likely causes:

### 1. **ECP Not Published Yet** ⏰
- The course exists and is offered, but the ECP (Electronic Course Profile) hasn't been published yet
- Common for courses that are:
  - Newly created
  - Not yet scheduled for the current semester
  - Still being prepared by course coordinators

### 2. **HTML Structure Changed** 🔄
- UQ's website structure may have changed
- The CSS classes or HTML structure for ECP links might be different
- The selector `class="profile-available"` might no longer be used

### 3. **Different Link Format** 🔗
- ECP links might be:
  - Using a different class name (e.g., just "profile" instead of "profile-available")
  - Not directly in the offerings section
  - Using JavaScript to load dynamically (not in initial HTML)

### 4. **Course Has No Assessments** 📝
- The course might exist but have no assessment section
- Some courses might not have deadlines listed in the ECP

### 5. **Archived or Future Offerings** 📅
- The course might only have past or future offerings
- Current offerings might not be available

## How to Debug

### Step 1: Use the Debug Endpoint

Visit this URL in your browser or use curl:
```
http://localhost:5000/api/debug/CSSE2010
```

This will show you:
- Whether the course exists
- What links are available in the offerings section
- What CSS classes are being used
- Sample HTML structure

### Step 2: Check the Actual Website

1. Visit: `https://programs-courses.uq.edu.au/course.html?course_code=CSSE2010`
2. Look for the "Current Offerings" section
3. Check if there are any ECP/profile links
4. Right-click on an ECP link and "Inspect Element"
5. Note the CSS classes and structure

### Step 3: Check Browser Console

If you're testing through the React app, check the browser console for:
- Network errors
- CORS issues
- Detailed error messages

## Solutions

### Solution 1: Updated Selector (Already Implemented)

The API now tries multiple strategies to find ECP links:
1. `class="profile-available"` (original)
2. `class="profile"` (fallback)
3. Any link with "profile" in class name
4. Any link with "ecp" or "profile" in the URL

### Solution 2: Manual Inspection

If the debug endpoint shows links but they're not being found, you may need to:
1. Update the CSS selector in `api_server.py`
2. Check if links are loaded via JavaScript (would require Selenium/Playwright)

### Solution 3: Wait for ECP Publication

If the course exists but has no ECP links, you may need to wait until:
- The course coordinator publishes the ECP
- The semester starts
- The ECP becomes available

## Testing the Debug Endpoint

```bash
# Using curl
curl http://localhost:5000/api/debug/CSSE2010

# Or visit in browser
http://localhost:5000/api/debug/CSSE2010
```

## Example Debug Output

```json
{
  "course_code": "CSSE2010",
  "url": "https://programs-courses.uq.edu.au/course.html?course_code=CSSE2010",
  "status_code": 200,
  "has_notfound": false,
  "has_offerings_section": true,
  "total_links_in_offerings": 2,
  "profile_available_count": 0,
  "profile_links_count": 1,
  "any_profile_count": 1,
  "sample_links": [
    {
      "text": "2024",
      "href": "/student/...",
      "classes": ["profile"]
    }
  ],
  "offerings_text": ["2024", "2023"]
}
```

## Next Steps

1. **Run the debug endpoint** to see what's actually available
2. **Check the actual UQ website** to verify the course structure
3. **Update selectors** if the HTML structure is different
4. **Report the issue** if it's a legitimate case where ECP should be available


