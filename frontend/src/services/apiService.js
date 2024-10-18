import axios from 'axios';

const axiosClient = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:4000/conve',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken'); // Adjust based on your auth implementation
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add any custom headers
    config.headers['X-Custom-Header'] = 'CustomHeaderValue';

    return config;
  },
  (error) => {
    // Handle request errors
    return Promise.reject(error);
  }
);

// Response interceptor to handle responses globally
axiosClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      let message = 'An error occurred.';
      if (status === 400) message = data.message || 'Bad Request.';
      if (status === 401) message = data.message || 'Unauthorized.';
      if (status === 404) message = data.message || 'Not Found.';
      if (status === 500) message = data.message || 'Internal Server Error.';
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // Request was made but no response received
      return Promise.reject(new Error('No response from server.'));
    } else {
      // Something else happened while setting up the request
      return Promise.reject(new Error(error.message));
    }
  }
);

const fetchStream = async (question, onMessage, onError, onEnd) => {
  try {
    const response = await fetch('http://localhost:4000/conversation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Custom-Header': 'CustomHeaderValue',
        // // Authorization header if needed
        // ...(localStorage.getItem('authToken') && {
        //   Authorization: `Bearer ${localStorage.getItem('authToken')}`,
        // }),
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let done = false;
    let buffer = '';

    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;

      if (value) {
        buffer += decoder.decode(value, { stream: true });

        // Assuming each event is separated by double newlines as per SSE
        const events = buffer.split('\n');
        buffer = events.pop(); // Last event might be incomplete
        events.forEach((event) => {
          if (event.startsWith('data:')) {
            const data = JSON.parse(event.replace('data:', '').trim());
            if (data && data.message !== "") {
              console.log(data);
              onMessage(data.message);
            }
          }
        });
      }
    }

    if (buffer.startsWith('data:')) {
      const data = buffer.replace('data:', '').trim();
      if (data) {
        onMessage(data);
      }
    }

    onEnd();
  } catch (error) {
    onError(error);
  }
};

const apiService = {
  sendMessage(message) {
    return axiosClient.post('/conversation', { message });
  },

  /**
   * Sends a question to the /conversation endpoint and handles streaming response.
   * @param {string} question - The user's question.
   * @param {Function} onMessage - Callback invoked with each incoming message chunk.
   * @param {Function} onError - Callback invoked on error.
   * @param {Function} onEnd - Callback invoked when the stream ends.
   */
  startConversation(question, onMessage, onError, onEnd) {
    return fetchStream(question, onMessage, onError, onEnd);
  },
};

export default apiService;
