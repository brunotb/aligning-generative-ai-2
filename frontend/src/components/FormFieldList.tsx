import { useState } from 'react';
import { FormField, FieldStatus } from '../types/form';
import { updateField } from '../services/api';

interface FormFieldListProps {
  fields: FormField[];
  currentIndex: number;
  answers: Record<string, string>;
  sessionId: string | null;
  currentDraftValue: string;
  translatedLabels: Record<string, string>;
}

export function FormFieldList({
  fields,
  currentIndex,
  answers,
  sessionId,
  currentDraftValue,
  translatedLabels,
}: FormFieldListProps) {
  const [editingFieldId, setEditingFieldId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const getFieldStatus = (index: number): FieldStatus => {
    if (index < currentIndex) return 'completed';
    if (index === currentIndex) return 'current';
    return 'pending';
  };

  const handleEdit = (fieldId: string, currentValue: string) => {
    setEditingFieldId(fieldId);
    setEditValue(currentValue || '');
    setValidationError(null);
  };

  const handleSave = async (fieldId: string) => {
    if (!sessionId) return;

    try {
      const result = await updateField(sessionId, fieldId, editValue);
      if (result.is_valid) {
        setEditingFieldId(null);
        setValidationError(null);
      } else {
        setValidationError(result.message);
      }
    } catch (error) {
      setValidationError('Failed to update field');
      console.error('Update error:', error);
    }
  };

  const handleCancel = () => {
    setEditingFieldId(null);
    setEditValue('');
    setValidationError(null);
  };

  const formatEnumValue = (field: FormField, value: string): string => {
    if (field.enum_values && value) {
      const numValue = parseInt(value, 10);
      return field.enum_values[numValue] || value;
    }
    return value;
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Form Fields</h2>
        <p className="text-sm text-gray-500">
          {Object.keys(answers).length} of {fields.length} completed
        </p>
      </div>

      {/* Scrollable Field List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {fields.map((field, index) => {
          const status = getFieldStatus(index);
          const value = answers[field.field_id] || '';
          const isEditing = editingFieldId === field.field_id;
          const displayValue = formatEnumValue(field, value);
          const translatedLabel = translatedLabels[field.field_id] || field.label;
          
          // Show draft value for current field if available
          const showDraftValue = status === 'current' && currentDraftValue && !value;

          return (
            <div
              key={field.field_id}
              className={`p-4 rounded-lg border-2 transition-all ${
                status === 'current'
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : status === 'completed'
                  ? 'border-green-200 bg-white hover:border-green-300'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              {/* Field Label */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {status === 'completed' && (
                    <svg
                      className="w-5 h-5 text-green-600 flex-shrink-0"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                  {status === 'current' && (
                    <svg
                      className="w-5 h-5 text-blue-600 flex-shrink-0 animate-pulse"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                  <h3
                    ctranslatedLe={`font-semibold text-sm ${
                      status === 'pending' ? 'text-gray-400' : 'text-gray-900'
                    }`}
                  >
                    {field.label}
                  </h3>
                </div>

                {/* Edit button for completed fields */}
                {status === 'completed' && !isEditing && (
                  <button
                    onClick={() => handleEdit(field.field_id, value)}
                    className="text-blue-600 hover:text-blue-700 text-xs font-medium"
                  >
                    Edit
                  </button>
                )}
              </div>

              {/* Field Value or Input */}
              {isEditing ? (
                <div className="space-y-2">
                  <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    placeholder={field.examples[0] || ''}
                  />
                  {validationError && (
                    <p className="text-xs text-red-600">{validationError}</p>
                  )}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSave(field.field_id)}
                      className="px-3 py-1 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700"
                    >
                      Save
                    </button>
                    <button
                      onClick={handleCancel}
                      className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs font-medium hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (showDraftValue ? (
                    <p className="text-sm text-blue-600 italic animate-pulse">
                      "{currentDraftValue}"
                    </p>
                  ) : 
                <>
                  {value ? (
                    <p className="text-sm text-gray-700 font-medium">{displayValue}</p>
                  ) : (
                    <p className="text-xs text-gray-400 italic">
                      {status === 'current' ? 'Listening for answer...' : 'Not filled yet'}
                    </p>
                  )}

                  {/* Show examples for current field */}
                  {status === 'current' && field.examples.length > 0 && (
                    <div className="mt-2 text-xs text-gray-500">
                      <span className="font-medium">Example:</span> {field.examples[0]}
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
