/**
 * API service for communicating with the Flask backend
 */

const API_BASE_URL = 'http://localhost:5000/api';

export const api = {
  /**
   * Get available course offerings for a course code
   * @param {string} courseCode - The course code (e.g., "CSSE1001")
   * @returns {Promise<Array>} Array of offerings
   */
  async getOfferings(courseCode) {
    const response = await fetch(`${API_BASE_URL}/offerings/${courseCode}`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch offerings');
    }
    const data = await response.json();
    return data.offerings;
  },

  /**
   * Get deadlines for a selected course offering
   * @param {string} ecpUrl - The ECP URL for the course offering
   * @param {string} courseCode - The course code
   * @returns {Promise<Array>} Array of deadlines
   */
  async getDeadlines(ecpUrl, courseCode) {
    const response = await fetch(`${API_BASE_URL}/deadlines`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ecp_url: ecpUrl,
        course_code: courseCode,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch deadlines');
    }
    
    const data = await response.json();
    return data.deadlines;
  },

  /**
   * Health check endpoint
   * @returns {Promise<boolean>} True if API is reachable
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  },
};


