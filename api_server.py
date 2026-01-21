"""
Flask API server for UQDeadline web scraping
Run with: python api_server.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from ecp_parse import ecpparser
import datetime
import re
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

def extract_deadlines_from_ecp(ecp_url):
    """Extract all deadlines from an ECP URL, handling multiple dates per assessment"""
    import requests
    from bs4 import BeautifulSoup
    
    ecp_results = requests.get(ecp_url)
    ecpsoup = BeautifulSoup(ecp_results.content, 'html.parser')
    
    # Try to find assessment section - could be in different formats
    # First try the common ID patterns
    assessment_section = ecpsoup.find(id="assessment--section")
    if not assessment_section:
        assessment_section = ecpsoup.find(id="assessment-section")
    if not assessment_section:
        assessment_section = ecpsoup.find(id="assessment")
    
    # If not found by ID, try finding by heading
    if not assessment_section:
        assessment_heading = ecpsoup.find('h2', string=lambda text: text and 'assessment' in text.lower())
        if assessment_heading:
            # Find the parent section or table
            assessment_section = assessment_heading.find_next('table')
            if not assessment_section:
                assessment_section = assessment_heading.find_next('div', class_=lambda x: x and 'assessment' in ' '.join(x).lower() if x else False)
            if not assessment_section:
                assessment_section = assessment_heading.find_parent()
    
    # Last resort: try finding any table or section that contains assessment-related content
    if not assessment_section:
        # Look for tables that might contain assessment data
        all_tables = ecpsoup.find_all('table')
        for table in all_tables:
            table_text = table.get_text().lower()
            if 'assessment' in table_text and ('due' in table_text or 'date' in table_text):
                assessment_section = table
                break
    
    if not assessment_section:
        raise ValueError('Assessment section not found in ECP. The page structure may have changed.')
    
    temp = assessment_section.find_all('tr')
    collected_data = []
    
    print(f"DEBUG: Found {len(temp)} table rows in assessment section")
    
    for c, t in enumerate(temp):
        # Get assessment name/label - try multiple strategies
        label = "Unknown"
        
        # Skip header row (usually first row with no dates)
        if c == 0:
            # Check if header row has dates - if not, skip it
            row_text_check = t.get_text(separator=' ', strip=True)
            date_pattern_check = r'\d{1,2}\/\d{2}\/\d{4}\s+\d{1,2}:\d{1,2}\s+[ap]m'
            if not re.search(date_pattern_check, row_text_check, re.IGNORECASE):
                print(f"DEBUG: Skipping header row {c}")
                continue
        
        # Try to find label in first cell (td)
        first_td = t.find('td')
        if first_td:
            # Try to get text from first td
            label_text = first_td.get_text(separator=' ', strip=True)
            # Remove date patterns from label text to get clean name
            label_text_clean = re.sub(r'\d{1,2}\/\d{2}\/\d{4}.*', '', label_text).strip()
            if label_text_clean and len(label_text_clean) > 2:
                label = label_text_clean
        
        # Fallback: try finding link, strong, or other elements
        if label == "Unknown" or len(label) < 2:
            label_elem = t.find('a')
            if not label_elem:
                label_elem = t.find('strong')
            if not label_elem:
                label_elem = t.find('th')
            if label_elem:
                label_text = label_elem.get_text(separator=' ', strip=True)
                # Remove date patterns
                label_text_clean = re.sub(r'\d{1,2}\/\d{2}\/\d{4}.*', '', label_text).strip()
                if label_text_clean and len(label_text_clean) > 2:
                    label = label_text_clean
        
        # Get all text content from this row
        row_text = t.get_text(separator=' ', strip=True)
        
        # Find ALL date patterns in the entire row - be more flexible with spacing
        # Try multiple date patterns - first try dates WITH times
        date_patterns_with_time = [
            r'\d{1,2}\/\d{2}\/\d{4}\s+\d{1,2}:\d{1,2}\s+[ap]m',  # Original: spaces required
            r'\d{1,2}\/\d{2}\/\d{4}\s*\d{1,2}:\d{1,2}\s*[ap]m',  # Flexible spacing
            r'\d{1,2}\/\d{2}\/\d{4}\s+\d{1,2}:\d{1,2}\s*[ap]m',  # Flexible am/pm spacing
        ]
        
        # Pattern for dates WITHOUT times (just date)
        date_pattern_without_time = r'\d{1,2}\/\d{2}\/\d{4}'
        
        all_dates = []
        
        # First, find all dates with times
        for pattern in date_patterns_with_time:
            dates = re.findall(pattern, row_text, re.IGNORECASE)
            if dates:
                all_dates.extend(dates)
        
        # Then, find dates without times and add default time
        dates_without_time = re.findall(date_pattern_without_time, row_text)
        for date_str in dates_without_time:
            # Check if this date is already in all_dates (with a time)
            date_with_time_exists = any(date_str in d for d in all_dates)
            if not date_with_time_exists:
                # Add default time of 8:00 am
                date_with_default_time = f"{date_str} 8:00 am"
                all_dates.append(date_with_default_time)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_dates = []
        for date_str in all_dates:
            # Extract just the date part for comparison
            date_part = re.search(r'\d{1,2}\/\d{2}\/\d{4}', date_str)
            if date_part:
                date_key = date_part.group()
                if date_key not in seen:
                    seen.add(date_key)
                    unique_dates.append(date_str)
        all_dates = unique_dates
        
        print(f"DEBUG: Row {c}, Label: '{label}', Found {len(all_dates)} dates")
        
        if all_dates:
            # For each date found, create a separate entry
            for date_idx, date_str in enumerate(all_dates):
                # Try to extract context/description before the date
                date_index = row_text.lower().find(date_str.lower())
                if date_index > 0:
                    # Get text before the date (up to 100 chars)
                    context = row_text[max(0, date_index-100):date_index].strip()
                    # Clean up context - remove extra whitespace and previous dates
                    context = ' '.join(context.split())
                    # Remove any date patterns from context
                    context = re.sub(r'\d{1,2}\/\d{2}\/\d{4}.*', '', context).strip()
                    # Use context if it's meaningful, otherwise use label
                    if len(context) > 3 and not context.startswith(label) and context != label:
                        title = f"{label} - {context}"
                    else:
                        title = label
                else:
                    title = label
                
                # If multiple dates for same assessment, add index
                if len(all_dates) > 1:
                    title = f"{title} ({date_idx + 1})"
                
                print(f"DEBUG: Adding deadline - Title: '{title}', Date: '{date_str}'")
                collected_data.append([title, date_str])
        else:
            # Fallback: try the old method with paragraphs and other elements
            # Check all text elements in the row
            stuff = t.findAll('p')
            if not stuff:
                stuff = t.findAll('td')
            if not stuff:
                stuff = t.findAll('div')
            
            # Define date patterns for fallback (same as above)
            date_patterns_with_time_fallback = [
                r'\d{1,2}\/\d{2}\/\d{4}\s+\d{1,2}:\d{1,2}\s+[ap]m',
                r'\d{1,2}\/\d{2}\/\d{4}\s*\d{1,2}:\d{1,2}\s*[ap]m',
                r'\d{1,2}\/\d{2}\/\d{4}\s+\d{1,2}:\d{1,2}\s*[ap]m',
            ]
            date_pattern_without_time_fallback = r'\d{1,2}\/\d{2}\/\d{4}'
            
            for s in stuff:
                para_text = s.get_text(separator=' ', strip=True) if hasattr(s, 'get_text') else str(s)
                # Try all date patterns with times first
                dates_in_para = []
                for pattern in date_patterns_with_time_fallback:
                    dates = re.findall(pattern, para_text, re.IGNORECASE)
                    if dates:
                        dates_in_para.extend(dates)
                
                # Then find dates without times and add default time
                dates_without_time = re.findall(date_pattern_without_time_fallback, para_text)
                for date_str in dates_without_time:
                    # Check if this date already has a time
                    date_with_time_exists = any(date_str in d for d in dates_in_para)
                    if not date_with_time_exists:
                        # Add default time of 8:00 am
                        date_with_default_time = f"{date_str} 8:00 am"
                        dates_in_para.append(date_with_default_time)
                
                # Remove duplicates
                seen = set()
                unique_dates_para = []
                for date_str in dates_in_para:
                    date_part = re.search(r'\d{1,2}\/\d{2}\/\d{4}', date_str)
                    if date_part:
                        date_key = date_part.group()
                        if date_key not in seen:
                            seen.add(date_key)
                            unique_dates_para.append(date_str)
                dates_in_para = unique_dates_para
                
                for date_idx, date_str in enumerate(dates_in_para):
                    # Extract context from paragraph
                    date_index = para_text.lower().find(date_str.lower())
                    if date_index > 0:
                        context = para_text[max(0, date_index-50):date_index].strip()
                        context = ' '.join(context.split())
                        context = re.sub(r'\d{1,2}\/\d{2}\/\d{4}.*', '', context).strip()
                        if len(context) > 3 and context != label:
                            title = f"{label} - {context}"
                        else:
                            title = label
                    else:
                        title = label
                    
                    if len(dates_in_para) > 1:
                        title = f"{title} ({date_idx + 1})"
                    
                    print(f"DEBUG: Adding deadline (fallback) - Title: '{title}', Date: '{date_str}'")
                    collected_data.append([title, date_str])
    
    print(f"DEBUG: Total deadlines collected: {len(collected_data)}")
    
    # Format the data
    now = datetime.datetime.now(datetime.timezone.utc)
    deadlines = []
    for row in collected_data:
        try:
            # Extract time string
            time_match = re.search(r"\d{1,2}:\d{1,2}\s[ap]m", row[1], re.IGNORECASE)
            time_str = time_match.group() if time_match else ""
            
            # Parse the datetime
            tempdatetime = datetime.datetime.strptime(row[1].upper(), "%d/%m/%Y %I:%M %p")
            tempdatetime = tempdatetime.replace(tzinfo=datetime.timezone.utc)
            
            # Calculate days remaining
            time_diff = tempdatetime - now
            days_remaining = time_diff.days
            
            # Format date as dd-mm-yyyy HH:MM:SS
            formatted_date = tempdatetime.strftime("%d-%m-%Y %H:%M:%S")
            
            deadlines.append({
                'title': row[0],
                'due_date': tempdatetime.isoformat(),
                'due_time': time_str,
                'due_date_display': formatted_date,
                'days_remaining': days_remaining
            })
        except ValueError as e:
            # Skip dates that can't be parsed
            print(f"Warning: Could not parse date '{row[1]}': {e}")
            continue
    
    # ------------------------------------------------------------
    # ADDED SORTING LOGIC HERE
    # Sorts by 'due_date' (ISO format string sorts chronologically)
    deadlines.sort(key=lambda x: x['due_date'])
    # ------------------------------------------------------------

    return deadlines

@app.route('/api/offerings/<course_code>', methods=['GET'])
def get_offerings(course_code):
    """Get available course offerings for a given course code"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        base_url = "https://programs-courses.uq.edu.au/course.html?course_code="
        response = requests.get(base_url + course_code)
        resoup = BeautifulSoup(response.content, 'html.parser')
        content = resoup.find(id="course-notfound")
        
        if content is not None:
            return jsonify({'error': 'Course code does not exist'}), 404
        
        cur_offerings = resoup.find(id="course-current-offerings")
        if cur_offerings is None:
            return jsonify({'error': 'Course is not offered'}), 404
        
        offerings = cur_offerings.findAll(class_="course-offering-year")
        all_profiles = cur_offerings.findAll('a', class_="profile-available", href=True)
        
        offerings_list = []
        for i, offering in enumerate(offerings):
            offerings_list.append({
                'index': i,
                'year': offering.text,
                'ecp_url': all_profiles[i]['href'] if i < len(all_profiles) else None
            })
        
        return jsonify({'offerings': offerings_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deadlines', methods=['POST'])
def get_deadlines():
    """Get deadlines for a selected course offering"""
    try:
        data = request.json
        ecp_url = data.get('ecp_url')
        course_code = data.get('course_code')
        
        if not ecp_url:
            return jsonify({'error': 'ECP URL is required'}), 400
        
        import requests
        from bs4 import BeautifulSoup
        
        deadlines = extract_deadlines_from_ecp(ecp_url)
        return jsonify({'deadlines': deadlines, 'course_code': course_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/course/<course_code>', methods=['GET'])
def get_course_deadlines(course_code):
    """Get deadlines for a course code (automatically selects first offering)"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        base_url = "https://programs-courses.uq.edu.au/course.html?course_code="
        response = requests.get(base_url + course_code)
        resoup = BeautifulSoup(response.content, 'html.parser')
        content = resoup.find(id="course-notfound")
        
        if content is not None:
            return jsonify({'error': 'Course code does not exist'}), 404
        
        cur_offerings = resoup.find(id="course-current-offerings")
        if cur_offerings is None:
            return jsonify({'error': 'Course is not offered'}), 404
        
        # Try multiple strategies to find ECP links
        all_profiles = cur_offerings.findAll('a', class_="profile-available", href=True)
        
        # If no "profile-available" links, try other patterns
        if not all_profiles:
            # Try just "profile" class
            all_profiles = cur_offerings.findAll('a', class_="profile", href=True)
        
        if not all_profiles:
            # Try any link with "profile" in class name
            all_profiles = cur_offerings.findAll('a', class_=lambda x: x and 'profile' in ' '.join(x).lower(), href=True)
        
        if not all_profiles:
            # Last resort: try any link in the offerings section that might be an ECP
            all_links = cur_offerings.findAll('a', href=True)
            # Filter for links that look like ECP/course profile URLs
            all_profiles = [link for link in all_links if 
                          'course-profile' in link.get('href', '').lower() or 
                          'course-profiles' in link.get('href', '').lower() or
                          'ecp' in link.get('href', '').lower() or 
                          'profile' in link.get('href', '').lower()]
        
        if not all_profiles:
            return jsonify({
                'error': 'No ECP available for this course',
                'debug': 'Try visiting /api/debug/' + course_code + ' to see available links',
                'suggestion': 'The course may not have an ECP published yet, or the HTML structure may have changed'
            }), 404
        
        # Use first available ECP
        ecp_url = all_profiles[0]['href']
        
        # Make sure the URL is absolute and points to course-profiles
        if ecp_url.startswith('/'):
            # If it's a relative path, it might be relative to programs-courses or course-profiles
            # Check if it looks like a course profile path
            if '/course-profiles/' in ecp_url or '/course-profile/' in ecp_url:
                ecp_url = 'https://course-profiles.uq.edu.au' + ecp_url
            else:
                # Try both domains
                ecp_url = 'https://course-profiles.uq.edu.au' + ecp_url
        elif not ecp_url.startswith('http'):
            # Handle protocol-relative URLs
            if ecp_url.startswith('//'):
                ecp_url = 'https:' + ecp_url
            else:
                ecp_url = 'https://course-profiles.uq.edu.au/' + ecp_url
        
        # Ensure we're using course-profiles domain (not programs-courses)
        if 'programs-courses.uq.edu.au' in ecp_url:
            # Replace with course-profiles domain
            ecp_url = ecp_url.replace('programs-courses.uq.edu.au', 'course-profiles.uq.edu.au')
        
        # Add #assessment anchor if not present (for direct navigation to assessment section)
        if '#assessment' not in ecp_url and '#assessment--section' not in ecp_url:
            ecp_url = ecp_url + '#assessment'
        
        # Get deadlines from ECP using the helper function
        try:
            deadlines = extract_deadlines_from_ecp(ecp_url)
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        
        return jsonify({'deadlines': deadlines, 'course_code': course_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/ecp/<path:ecp_url>', methods=['GET'])
def debug_ecp(ecp_url):
    """Debug endpoint to see the raw HTML structure of an ECP"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Decode URL if needed
        if not ecp_url.startswith('http'):
            ecp_url = 'https://' + ecp_url
        
        response = requests.get(ecp_url)
        ecpsoup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find assessment section
        assessment_section = ecpsoup.find(id="assessment--section")
        if not assessment_section:
            assessment_section = ecpsoup.find(id="assessment-section")
        if not assessment_section:
            assessment_section = ecpsoup.find(id="assessment")
        
        debug_info = {
            'url': ecp_url,
            'status_code': response.status_code,
            'has_assessment_section': assessment_section is not None,
            'assessment_section_id': None,
        }
        
        if assessment_section:
            debug_info['assessment_section_id'] = assessment_section.get('id')
            rows = assessment_section.find_all('tr')
            debug_info['row_count'] = len(rows)
            debug_info['rows'] = []
            
            for i, row in enumerate(rows[:10]):  # Limit to first 10 rows
                row_data = {
                    'index': i,
                    'html': str(row)[:500],  # First 500 chars
                    'text': row.get_text(separator=' | ', strip=True)[:200],
                    'td_count': len(row.find_all('td')),
                }
                # Check for dates
                row_text = row.get_text()
                date_pattern = r'\d{1,2}\/\d{2}\/\d{4}\s+\d{1,2}:\d{1,2}\s+[ap]m'
                dates = re.findall(date_pattern, row_text, re.IGNORECASE)
                row_data['dates_found'] = dates
                debug_info['rows'].append(row_data)
        else:
            # Show all tables
            all_tables = ecpsoup.find_all('table')
            debug_info['total_tables'] = len(all_tables)
            debug_info['table_ids'] = [t.get('id') for t in all_tables if t.get('id')]
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': str(__import__('traceback').format_exc())}), 500

@app.route('/api/debug/<course_code>', methods=['GET'])
def debug_course(course_code):
    """Debug endpoint to see what's available for a course"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        base_url = "https://programs-courses.uq.edu.au/course.html?course_code="
        response = requests.get(base_url + course_code)
        resoup = BeautifulSoup(response.content, 'html.parser')
        
        debug_info = {
            'course_code': course_code,
            'url': base_url + course_code,
            'status_code': response.status_code,
            'has_notfound': resoup.find(id="course-notfound") is not None,
            'has_offerings_section': resoup.find(id="course-current-offerings") is not None,
        }
        
        cur_offerings = resoup.find(id="course-current-offerings")
        if cur_offerings:
            # Find all links in the offerings section
            all_links = cur_offerings.findAll('a', href=True)
            profile_available = cur_offerings.findAll('a', class_="profile-available", href=True)
            profile_links = cur_offerings.findAll('a', class_="profile", href=True)
            any_profile = cur_offerings.findAll('a', class_=lambda x: x and 'profile' in x.lower(), href=True)
            
            debug_info.update({
                'total_links_in_offerings': len(all_links),
                'profile_available_count': len(profile_available),
                'profile_links_count': len(profile_links),
                'any_profile_count': len(any_profile),
                'sample_links': [{'text': link.text.strip(), 'href': link.get('href'), 'classes': link.get('class')} for link in all_links[:5]],
                'offerings_text': [offering.text.strip() for offering in cur_offerings.findAll(class_="course-offering-year")],
            })
        else:
            debug_info['offerings_section_html'] = str(cur_offerings)[:500] if cur_offerings else None
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': str(__import__('traceback').format_exc())}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

