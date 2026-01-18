import { create } from 'zustand';
import { FormField, FormState, Transcript } from '../types/form';

export type AssistantStatus = 'idle' | 'listening' | 'thinking' | 'speaking';

interface FormStore extends FormState {
  sessionId: string | null;
  isRecording: boolean;
  assistantStatus: AssistantStatus; // Current status: idle, listening, thinking, speaking
  transcripts: Transcript[];
  ws: WebSocket | null;
  currentDraftValue: string; // Real-time value being discussed
  detectedLanguage: string | null; // User's language
  translatedLabels: Record<string, string>; // field_id -> translated label
  lastUpdatedFieldId: string | null; // ID of the last field that was updated

  // Actions
  setSessionId: (id: string) => void;
  setFields: (fields: FormField[]) => void;
  setCurrentIndex: (index: number) => void;
  setAnswer: (fieldId: string, value: string) => void;
  setProgress: (percent: number) => void;
  setRecording: (recording: boolean) => void;
  setAssistantStatus: (status: AssistantStatus) => void;
  addTranscript: (speaker: 'user' | 'assistant', text: string) => void;
  setWebSocket: (ws: WebSocket | null) => void;
  updateFromWSEvent: (type: string, data: any) => void;
  setCurrentDraftValue: (value: string) => void;
  setDetectedLanguage: (lang: string) => void;
  setTranslatedLabel: (fieldId: string, label: string) => void;
  reset: () => void;
}

const initialState = {
  sessionId: null,
  fields: [],
  current_index: 0,
  answers: {},
  progress_percent: 0,
  isRecording: false,
  assistantStatus: 'idle' as AssistantStatus,
  transcripts: [],
  ws: null,
  currentDraftValue: '',
  detectedLanguage: null,
  translatedLabels: {},
  lastUpdatedFieldId: null,
};

export const useFormStore = create<FormStore>((set, get) => ({
  ...initialState,

  setSessionId: (id) => set({ sessionId: id }),

  setFields: (fields) => set({ fields }),

  setCurrentIndex: (index) => set({ current_index: index }),

  setAnswer: (fieldId, value) =>
    set((state) => ({
      answers: { ...state.answers, [fieldId]: value },
      lastUpdatedFieldId: fieldId,
    })),

  setProgress: (percent) => set({ progress_percent: percent }),

  setRecording: (recording) => set({ isRecording: recording }),

  setAssistantStatus: (status) => set({ assistantStatus: status }),

  addTranscript: (speaker, text) =>
    set((state) => ({
      transcripts: [
        ...state.transcripts,
        { speaker, text, timestamp: Date.now() },
      ],
    })),

  setWebSocket: (ws) => set({ ws }),

  setCurrentDraftValue: (value) => set({ currentDraftValue: value }),

  setDetectedLanguage: (lang) => set({ detectedLanguage: lang }),

  setTranslatedLabel: (fieldId, label) =>
    set((state) => ({
      translatedLabels: { ...state.translatedLabels, [fieldId]: label },
    })),

  updateFromWSEvent: (type, data) => {
    const state = get();

    switch (type) {
      case 'initial_state':
        set({
          fields: data.fields || [],
          current_index: data.current_index || 0,
          currentDraftValue: '', // Clear draft when field changes
          lastUpdatedFieldId: null, // Reset highlight on init
        });
        // Update translated label if provided
        if (data.translated_label) {
          state.setTranslatedLabel(data.field_id, data.translated_label);
        }
        break;

      case 'validation_result':
        // Show draft value during validation
        if (data.value) {
          set({ currentDraftValue: data.value });
        }
        console.log('Validation:', data);
        break;

      case 'field_saved':
        set((state) => ({
          answers: { ...state.answers, [data.field_id]: data.value },
          progress_percent: data.progress_percent || state.progress_percent,
          currentDraftValue: '', // Clear draft after saving
          lastUpdatedFieldId: data.field_id,
        }));
        break;

      case 'field_updated':
        set((state) => ({
          answers: { ...state.answers, [data.field_id]: data.value },
          progress_percent: data.progress_percent || state.progress_percent,
          lastUpdatedFieldId: data.field_id,
        }));
        break;

      case 'transcript':
        state.addTranscript(data.speaker, data.text);
        // Detect language from first user transcript
        if (data.speaker === 'user' && !state.detectedLanguage && data.language) {
          state.setDetectedLanguage(data.language);
        }
        // Update draft value when user speaks (potential answer)
        if (data.speaker === 'user' && state.current_index < state.fields.length) {
          set({ currentDraftValue: data.text });
        }
        break;

      case 'form_complete':
        console.log('Form complete!', data);
        break;

      case 'ping':
        // Keep-alive, no action needed
        break;

      default:
        console.warn('Unknown event type:', type);
    }
  },

  reset: () => set(initialState),
}));
