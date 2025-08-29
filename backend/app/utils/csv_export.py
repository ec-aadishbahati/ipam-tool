import csv
import io
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any

def create_csv_response(data: List[Dict[str, Any]], headers: List[str], filename: str) -> StreamingResponse:
    """Create a CSV streaming response from data"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    
    for row in data:
        writer.writerow([row.get(header, "") for header in headers])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def create_csv_template(headers: List[str], sample_data: List[str], filename: str) -> StreamingResponse:
    """Create a CSV template with headers and sample data"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerow(sample_data)
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
