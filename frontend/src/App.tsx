import { useState, useEffect } from 'react';
import { WelcomeScreen } from './components/WelcomeScreen';
import { ConversationScreen } from './components/ConversationScreen';
import { useFormStore } from './store/formStore';
import { useWebSocket } from './hooks/useWebSocket';
import { createSession } from './services/api';

function App() {
  const [hasStarted, setHasStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { sessionId, setSessionId, setRecording } = useFormStore();

  // Initialize WebSocket connection
  useWebSocket(sessionId);

  const handleStart = async () => {
    setIsLoading(true);
    try {
      const newSessionId = await createSession();
      setSessionId(newSessionId);
      setHasStarted(true);
      setRecording(true); // Assume recording starts immediately
    } catch (error) {
      console.error('Failed to start session:', error);
      alert('Failed to start session. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
          <p className="mt-4 text-gray-600">Starting session...</p>
        </div>
      </div>
    );
  }

  if (!hasStarted) {
    return <WelcomeScreen onStart={handleStart} />;
  }

  return <ConversationScreen />;
}

export default App;
