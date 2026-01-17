import { useFormStore } from '../store/formStore';

export function DebugPanel() {
  const { 
    sessionId, 
    isRecording, 
    ws, 
    transcripts, 
    current_index, 
    answers,
    currentDraftValue 
  } = useFormStore();

  const isConnected = ws !== null && ws.readyState === WebSocket.OPEN;

  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 text-white p-4 rounded-lg shadow-xl max-w-sm text-xs font-mono z-50">
      <h3 className="font-bold mb-2 text-green-400">Debug Info</h3>
      
      <div className="space-y-1">
        <div>Session: <span className="text-blue-400">{sessionId || 'None'}</span></div>
        <div>WebSocket: <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span></div>
        <div>Recording: <span className={isRecording ? 'text-red-400' : 'text-gray-400'}>
          {isRecording ? 'Yes' : 'No'}
        </span></div>
        <div>Current Field: <span className="text-yellow-400">{current_index}</span></div>
        <div>Filled Fields: <span className="text-yellow-400">{Object.keys(answers).length}</span></div>
        <div>Draft Value: <span className="text-purple-400">{currentDraftValue || 'None'}</span></div>
        <div>Transcripts: <span className="text-yellow-400">{transcripts.length}</span></div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700">
        <div className="font-bold text-green-400 mb-1">Last 3 Events:</div>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {transcripts.slice(-3).map((t, i) => (
            <div key={i} className="text-xs">
              <span className={t.speaker === 'user' ? 'text-blue-400' : 'text-orange-400'}>
                {t.speaker}:
              </span>
              <span className="text-gray-300"> {t.text.substring(0, 50)}...</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
