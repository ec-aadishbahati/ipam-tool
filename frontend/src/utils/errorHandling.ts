export function getErrorMessage(error: any, fallback: string = "Error"): string {
  if (error?.response?.data?.detail && Array.isArray(error.response.data.detail)) {
    const messages = error.response.data.detail.map((err: any) => 
      err.msg || err.message || JSON.stringify(err)
    );
    return messages.join(', ');
  }
  
  return error?.response?.data?.detail || error?.message || fallback;
}

export function getErrorDetails(error: any): string[] {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((err: any) => err.msg || err.message || JSON.stringify(err));
  }
  return [getErrorMessage(error)];
}
