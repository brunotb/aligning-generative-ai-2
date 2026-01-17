interface MicrophoneIndicatorProps {
  isRecording: boolean;
}

export function MicrophoneIndicator({ isRecording }: MicrophoneIndicatorProps) {
  return (
    <div className="flex flex-col items-center justify-center">
      {/* Message */}
      <p className="text-xl text-gray-700 mb-8 text-center font-medium">
        Talk in your language. Feel free to ask me anything
      </p>

      {/* Microphone Circle */}
      <div className="relative">
        {/* Pulsing rings when recording */}
        {isRecording && (
          <>
            <div className="absolute inset-0 rounded-full bg-blue-400 opacity-75 animate-ping"></div>
            <div className="absolute inset-0 rounded-full bg-blue-400 opacity-50 animate-pulse"></div>
          </>
        )}

        {/* Main microphone button */}
        <div
          className={`relative z-10 w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${
            isRecording
              ? 'bg-red-500 shadow-lg shadow-red-500/50'
              : 'bg-gray-300 shadow-md'
          }`}
        >
          <svg
            className={`w-16 h-16 transition-colors duration-300 ${
              isRecording ? 'text-white' : 'text-gray-600'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      </div>

      {/* Status Text */}
      <div className="mt-6 text-center">
        {isRecording ? (
          <div className="flex items-center gap-2 text-red-600">
            <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
            <span className="font-semibold">Listening...</span>
          </div>
        ) : (
          <span className="text-gray-500">Ready to speak</span>
        )}
      </div>
    </div>
  );
}
