import { MicrophoneIndicator } from './MicrophoneIndicator';
import { FormFieldList } from './FormFieldList';
import { ProgressBar } from './ProgressBar';
import { PrintPDFButton } from './PrintPDFButton';
import { DebugPanel } from './DebugPanel';
import { ChatHistory } from './ChatHistory';
import { useFormStore } from '../store/formStore';

export function ConversationScreen() {
  const {
    sessionId,
    fields,
    current_index,
    answers,
    progress_percent,
    isRecording,
    currentDraftValue,
    translatedLabels,
    lastUpdatedFieldId,
  } = useFormStore();

  const hasAnswers = Object.keys(answers).length > 0;

  return (
    <div className="h-screen bg-gray-100 flex">
      {/* Left Panel - 2/3 - Microphone + Chat */}
      <div className="w-2/3 bg-white flex flex-col p-6">
        {/* Microphone Section - Top */}
        <div className="flex items-center justify-center py-8">
          <MicrophoneIndicator isRecording={isRecording} />
        </div>

        {/* Chat History - Bottom (scrollable) */}
        <div className="flex-1 overflow-hidden">
          <ChatHistory />
        </div>
      </div>

      {/* Right Panel - 1/3 - Form Fields */}
      <div className="w-1/3 bg-gray-50 border-l border-gray-200 flex flex-col">
        {/* Form Field List - Scrollable */}
        <div className="flex-1 overflow-hidden">
          <FormFieldList
            fields={fields}
            currentIndex={current_index}
            currentDraftValue={currentDraftValue}
            translatedLabels={translatedLabels}
            answers={answers}
            sessionId={sessionId}
            lastUpdatedFieldId={lastUpdatedFieldId}
          />
        </div>

        {/* Bottom Section - Progress & PDF Button */}
        <div className="border-t border-gray-200 p-4 bg-white space-y-4">
          <ProgressBar progress={progress_percent} />
          <PrintPDFButton sessionId={sessionId} hasAnswers={hasAnswers} />
        </div>
      </div>

      {/* Debug Panel */}
      {/*<DebugPanel />*/}
    </div>
  );
}
