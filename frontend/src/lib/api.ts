import { AnalysisRequest, AnalysisSuccessResponse } from "@/types/analysis";
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
export async function analyzeText(request: AnalysisRequest): Promise<AnalysisSuccessResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/analyze/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.message || 'Analysis failed');
  }
  return response.json();
}
export async function analyzeFile(file: File): Promise<AnalysisSuccessResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${BACKEND_URL}/api/v1/analyze/file`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.message || 'File analysis failed');
  }
  return response.json();
}
