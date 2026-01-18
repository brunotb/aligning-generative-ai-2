import { AssistantStatus } from '../store/formStore';

interface MicrophoneIndicatorProps {
  isRecording: boolean;
  assistantStatus: AssistantStatus;
}

export function MicrophoneIndicator({ isRecording, assistantStatus }: MicrophoneIndicatorProps) {
  // Determine the actual display state
  // isRecording takes precedence when true
  const displayStatus = isRecording ? 'listening' : assistantStatus;

  // Get styling based on status
  const getButtonStyle = () => {
    switch (displayStatus) {
      case 'listening':
        return 'bg-red-500 shadow-lg shadow-red-500/50';
      case 'thinking':
        return 'bg-yellow-500 shadow-lg shadow-yellow-500/50';
      case 'speaking':
        return 'bg-blue-500 shadow-lg shadow-blue-500/50';
      default:
        return 'bg-gray-300 shadow-md';
    }
  };

  const getPulseColor = () => {
    switch (displayStatus) {
      case 'listening':
        return 'bg-red-400';
      case 'thinking':
        return 'bg-yellow-400';
      case 'speaking':
        return 'bg-blue-400';
      default:
        return 'bg-gray-400';
    }
  };

  const getIconColor = () => {
    return displayStatus !== 'idle' ? 'text-white' : 'text-gray-600';
  };

  const getStatusText = () => {
    switch (displayStatus) {
      case 'listening':
        return { text: 'Listening...', color: 'text-red-600' };
      case 'thinking':
        return { text: 'Thinking...', color: 'text-yellow-600' };
      case 'speaking':
        return { text: 'Speaking...', color: 'text-blue-600' };
      default:
        return { text: 'Ready to speak', color: 'text-gray-500' };
    }
  };

  const status = getStatusText();
  const showAnimation = displayStatus !== 'idle';

  return (
    <div className="flex flex-col items-center justify-center">
      {/* Message */}
      <p className="text-xl text-gray-700 mb-8 text-center font-medium">
        Talk in your language. Feel free to ask me anything
      </p>

      {/* Microphone Circle */}
      <div className="relative">
        {/* Pulsing rings when active */}
        {showAnimation && (
          <>
            <div className={`absolute inset-0 rounded-full ${getPulseColor()} opacity-75 animate-ping`}></div>
            <div className={`absolute inset-0 rounded-full ${getPulseColor()} opacity-50 animate-pulse`}></div>
          </>
        )}

        {/* Main microphone button */}
        <div
          className={`relative z-10 w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${getButtonStyle()}`}
        >
          {displayStatus === 'thinking' ? (
            // Show spinner when thinking
            <svg
              className="w-12 h-12 text-white animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          ) : displayStatus === 'speaking' ? (
            // Show speaker icon when speaking
            <svg
              className={`w-16 h-16 transition-colors duration-300 ${getIconColor()}`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            // Show microphone icon for listening and idle
            <svg
              className={`w-16 h-16 transition-colors duration-300 ${getIconColor()}`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>
      </div>

      {/* Status Text */}
      <div className="mt-6 text-center">
        <div className={`flex items-center gap-2 ${status.color}`}>
          {showAnimation && (
            <div className={`w-2 h-2 ${displayStatus === 'listening' ? 'bg-red-600' : displayStatus === 'thinking' ? 'bg-yellow-600' : 'bg-blue-600'} rounded-full animate-pulse`}></div>
          )}
          <span className={showAnimation ? 'font-semibold' : ''}>{status.text}</span>
        </div>
      </div>
    </div>
  );
}
