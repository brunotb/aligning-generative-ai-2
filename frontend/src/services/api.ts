const API_BASE = '/api';

export async function createSession(): Promise<string> {
  const response = await fetch(`${API_BASE}/session/start`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Failed to create session');
  }

  const data = await response.json();
  return data.session_id;
}

export async function updateField(
  sessionId: string,
  fieldId: string,
  value: string
): Promise<{ ok: boolean; is_valid: boolean; message: string }> {
  const response = await fetch(
    `${API_BASE}/session/${sessionId}/field/${fieldId}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ value }),
    }
  );

  if (!response.ok) {
    throw new Error('Failed to update field');
  }

  return response.json();
}

export async function downloadPDF(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/session/${sessionId}/pdf`);

  if (!response.ok) {
    throw new Error('Failed to generate PDF');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `anmeldung_${new Date().toISOString().split('T')[0]}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
