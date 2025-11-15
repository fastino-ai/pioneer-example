import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [userEmail, setUserEmail] = useState(null);
  const [userId, setUserId] = useState(null);
  const [emailInput, setEmailInput] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [registrationError, setRegistrationError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const messagesEndRef = useRef(null);

  // Load user and theme from localStorage on mount
  useEffect(() => {
    const storedEmail = localStorage.getItem('pioneer_user_email');
    const storedUserId = localStorage.getItem('pioneer_user_id');
    const storedTimestamp = localStorage.getItem('pioneer_user_timestamp');
    const storedTheme = localStorage.getItem('pioneer_theme');
    
    if (storedEmail && storedUserId && storedTimestamp) {
      // Check if stored data is less than 30 days old
      const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
      if (parseInt(storedTimestamp) > thirtyDaysAgo) {
        setUserEmail(storedEmail);
        setUserId(storedUserId);
        console.log('Restored user session from localStorage:', storedEmail, storedUserId);
      } else {
        // Clear expired data
        console.log('User session expired, clearing localStorage');
        localStorage.removeItem('pioneer_user_email');
        localStorage.removeItem('pioneer_user_id');
        localStorage.removeItem('pioneer_user_timestamp');
      }
    }
    
    // Load theme preference
    if (storedTheme === 'dark') {
      setIsDarkMode(true);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const registerUser = async (e) => {
    e.preventDefault();
    
    if (!emailInput.trim() || isRegistering) return;

    setIsRegistering(true);
    setRegistrationError(null);

    try {
      const trimmedEmail = emailInput.trim();
      
      // Check if we have existing data for this email
      const storedEmail = localStorage.getItem('pioneer_user_email');
      const storedUserId = localStorage.getItem('pioneer_user_id');
      
      // If email changed, clear old user_id
      if (storedEmail && storedEmail !== trimmedEmail) {
        console.log('Email changed, clearing old user data');
        localStorage.removeItem('pioneer_user_id');
        localStorage.removeItem('pioneer_user_timestamp');
      }
      
      const response = await axios.post(`${API_BASE_URL}/register`, {
        email: trimmedEmail
      });

      if (response.data.success && response.data.user_id) {
        const newUserId = response.data.user_id;
        
        // Store in state
        setUserEmail(trimmedEmail);
        setUserId(newUserId);
        
        // Store in localStorage
        localStorage.setItem('pioneer_user_email', trimmedEmail);
        localStorage.setItem('pioneer_user_id', newUserId);
        localStorage.setItem('pioneer_user_timestamp', Date.now().toString());
        
        console.log('User registered successfully:', {
          email: trimmedEmail,
          user_id: newUserId
        });
      } else {
        throw new Error('Registration did not return user_id');
      }
    } catch (error) {
      console.error('Error registering user:', error);
      setRegistrationError(
        error.response?.data?.detail || 
        error.message ||
        'Failed to register. Please check your email and try again.'
      );
    } finally {
      setIsRegistering(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: inputMessage,
        conversation_history: messages,
        user_id: userId,
        user_email: userEmail  // Send both for backward compatibility and debugging
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        context: response.data.relevant_context
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.data.user_profile && !userProfile) {
        setUserProfile(response.data.user_profile);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}. Please make sure your API keys are configured correctly in the backend .env file.`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setUserProfile(null);
  };

  const logout = () => {
    // Clear state
    setMessages([]);
    setUserProfile(null);
    setUserEmail(null);
    setUserId(null);
    setEmailInput('');
    
    // Clear localStorage (but keep theme preference)
    localStorage.removeItem('pioneer_user_email');
    localStorage.removeItem('pioneer_user_id');
    localStorage.removeItem('pioneer_user_timestamp');
    
    console.log('User logged out, cleared all session data');
  };

  const toggleDarkMode = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('pioneer_theme', newMode ? 'dark' : 'light');
  };

  // Show registration screen if user hasn't registered
  if (!userEmail || !userId) {
    return (
      <div className={`app ${isDarkMode ? 'dark-mode' : ''}`}>
        <div className="registration-container">
          <button 
            className="theme-toggle"
            onClick={toggleDarkMode}
            aria-label="Toggle dark mode"
          >
            {isDarkMode ? 'Toggle Theme' : 'Toggle Theme'}
          </button>
          <div className="registration-card">
            <div className="registration-header">
              <h1>Welcome to Pioneer Chat</h1>
              <p className="registration-subtitle">
                Experience AI that learns and adapts to you
              </p>
            </div>

            <div className="registration-content">
              <div className="features-grid">
                <div className="feature-item">
                  <strong>Contextual Memory</strong>
                  <p>Remembers your preferences across conversations</p>
                </div>
                <div className="feature-item">
                  <strong>Personalized Responses</strong>
                  <p>Adapts to your communication style</p>
                </div>
                <div className="feature-item">
                  <strong>Privacy First</strong>
                  <p>All data is anonymized and secure</p>
                </div>
              </div>

              <form onSubmit={registerUser} className="registration-form">
                <label htmlFor="email">Enter your email to get started</label>
                <input
                  id="email"
                  type="email"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  placeholder="your.email@example.com"
                  disabled={isRegistering}
                  className="email-input"
                  required
                />
                {registrationError && (
                  <div className="error-message">
                    {registrationError}
                  </div>
                )}
                <button 
                  type="submit" 
                  disabled={isRegistering || !emailInput.trim()}
                  className="register-button"
                >
                  {isRegistering ? 'Registering...' : 'Start Chatting'}
                </button>
              </form>

              <div className="registration-note">
                <p>
                  <strong>Note:</strong> Your email is used to personalize your experience.
                  Use the same email as your Pioneer API account for best results.
                </p>
              </div>
            </div>
          </div>

          <footer className="footer">
            <p>
              Built with <a href="https://fastino.ai" target="_blank" rel="noopener noreferrer">Pioneer API</a> 
              {' '} + <a href="https://openai.com" target="_blank" rel="noopener noreferrer">OpenAI GPT-4o</a>
            </p>
            <p className="footer-note">
              Open source example • <a href="https://github.com/fastino-ai/pioneer-example" target="_blank" rel="noopener noreferrer">View on GitHub</a>
            </p>
          </footer>
        </div>
      </div>
    );
  }

  return (
    <div className={`app ${isDarkMode ? 'dark-mode' : ''}`}>
      <header className="header">
        <div className="header-content">
          <h1>Pioneer Chat</h1>
          <p className="subtitle">
            Logged in as: <strong>{userEmail}</strong>
          </p>
        </div>
        <div className="header-actions">
          <button 
            className="theme-toggle"
            onClick={toggleDarkMode}
            aria-label="Toggle dark mode"
          >
            {isDarkMode ? 'Toggle Theme' : 'Toggle Theme'}
          </button>
          <button 
            className="clear-btn"
            onClick={clearChat}
            disabled={messages.length === 0}
          >
            Clear Chat
          </button>
          <button 
            className="logout-btn"
            onClick={logout}
          >
            Logout
          </button>
        </div>
      </header>

      <div className="container">
        <div className="chat-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>Welcome to Pioneer Chat</h2>
              <p>This AI assistant learns from your conversations and provides personalized responses.</p>
              <div className="features">
                <div className="feature">
                  <div>
                    <strong>Contextual Memory</strong>
                    <p>Remembers your preferences and past conversations</p>
                  </div>
                </div>
                <div className="feature">
                  <div>
                    <strong>Personalized Responses</strong>
                    <p>Adapts to your communication style and needs</p>
                  </div>
                </div>
                <div className="feature">
                  <div>
                    <strong>Privacy First</strong>
                    <p>All data is anonymized and secure</p>
                  </div>
                </div>
              </div>
              <p className="start-prompt">Start chatting to see personalization in action</p>
            </div>
          ) : (
            <div className="messages">
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}>
                  <div className="message-header">
                    <span className="message-role">
                      {msg.role === 'user' ? 'You' : 'Assistant'}
                    </span>
                    <span className="message-time">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message assistant loading">
                  <div className="message-header">
                    <span className="message-role">Assistant</span>
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <form className="input-form" onSubmit={sendMessage}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="message-input"
          />
          <button 
            type="submit" 
            disabled={isLoading || !inputMessage.trim()}
            className="send-button"
          >
            Send
          </button>
        </form>
      </div>

      <footer className="footer">
        <p>
          Built with <a href="https://fastino.ai" target="_blank" rel="noopener noreferrer">Pioneer API</a> 
          {' '} + <a href="https://openai.com" target="_blank" rel="noopener noreferrer">OpenAI GPT-4o</a>
        </p>
        <p className="footer-note">
          Open source example • <a href="https://github.com/fastino-ai/pioneer-example" target="_blank" rel="noopener noreferrer">View on GitHub</a>
        </p>
      </footer>
    </div>
  );
}

export default App;

