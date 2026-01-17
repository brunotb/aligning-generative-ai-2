/**
 * Form field definition
 */
export interface FormField {
  field_id: string;
  label: string;
  description: string;
  examples: string[];
  required: boolean;
  validator_type: string;
  enum_values?: Record<number, string>;
}

/**
 * Form state
 */
export interface FormState {
  fields: FormField[];
  current_index: number;
  answers: Record<string, string>;
  progress_percent: number;
}

/**
 * WebSocket event types
 */
export type WSEventType =
  | 'initial_state'
  | 'field_changed'
  | 'validation_result'
  | 'field_saved'
  | 'field_updated'
  | 'transcript'
  | 'form_complete'
  | 'ping';

/**
 * WebSocket message
 */
export interface WSMessage {
  type: WSEventType;
  data: any;
}

/**
 * Transcript entry
 */
export interface Transcript {
  speaker: 'user' | 'assistant';
  text: string;
  timestamp: number;
}

/**
 * Field status for UI
 */
export type FieldStatus = 'pending' | 'current' | 'completed';
