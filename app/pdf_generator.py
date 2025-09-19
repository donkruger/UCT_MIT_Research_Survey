"""
PDF generation for the Research Survey Application.

This module creates PDF summaries of survey submissions.
"""

import io
import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.utils import text_wrap

def make_pdf(payload: Dict[str, Any]) -> bytes:
    """
    Render all survey responses to a simple, printable PDF.
    
    Args:
        payload: Dictionary containing survey responses
        
    Returns:
        bytes: PDF file content as bytes
    """
    # Validate payload type
    if not isinstance(payload, dict):
        # Return a simple error PDF instead of crashing
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        w, h = A4
        margin = 40
        y = h - margin
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y, "Error: Invalid Data Format")
        y -= 2 * 14
        c.setFont("Helvetica", 10)
        c.drawString(margin, y, f"Received: {type(payload).__name__}")
        y -= 14
        c.drawString(margin, y, "Expected: Dictionary")
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.read()
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    line_height = 14
    margin = 40
    y = h - margin

    def check_page_break(y_pos):
        """Adds a new page if content gets too close to the bottom margin."""
        if y_pos < margin + 2 * line_height:
            c.showPage()
            return h - margin
        return y_pos

    # Title and header
    c.setFont("Helvetica-Bold", 16)
    survey_type = payload.get("Survey Type", "Survey Response")
    c.drawString(margin, y, f"{survey_type} – Summary Report")
    y -= 2 * line_height
    
    # Timestamp
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M}")
    y -= 1.5 * line_height
    
    # Process each section
    for section, data in payload.items():
        # Skip metadata fields
        if section in ["Survey Type"]:
            continue
            
        y = check_page_break(y)
        c.setFont("Helvetica-Bold", 12)
        y -= line_height
        c.drawString(margin, y, str(section))
        y -= 0.5 * line_height
        c.line(margin, y, w - margin, y)
        y -= line_height
        c.setFont("Helvetica", 9)

        # Handle different data types
        if isinstance(data, list):
            # Handle list of items (e.g., multiple responses)
            for i, item in enumerate(data):
                y = check_page_break(y)
                item_prefix = f"  Item {i + 1}: "
                if isinstance(item, dict):
                    c.drawString(margin, y, item_prefix)
                    y -= line_height
                    for k, v in item.items():
                        y = check_page_break(y)
                        label = f"    • {k}: "
                        value_text = str(v) if v not in (None, "") else "(not provided)"
                        
                        # Handle long text with wrapping
                        wrapped_lines = text_wrap(value_text, 70)
                        c.drawString(margin, y, label + wrapped_lines[0] if wrapped_lines else label)
                        y -= line_height
                        for extra_line in wrapped_lines[1:]:
                            y = check_page_break(y)
                            c.drawString(margin + 40, y, extra_line)
                            y -= line_height
                else:
                    # Simple list item
                    text = f"{item_prefix}{item}"
                    wrapped_lines = text_wrap(text, 90)
                    for line in wrapped_lines:
                        y = check_page_break(y)
                        c.drawString(margin, y, line)
                        y -= line_height
                        
        elif isinstance(data, dict):
            # Handle nested dictionary (e.g., grouped fields)
            if "Records" in data and "Count" in data:
                # Special handling for collection-style data
                count = data.get("Count", 0)
                c.drawString(margin, y, f"  Total Count: {count}")
                y -= line_height
                
                records = data.get("Records", [])
                for i, record in enumerate(records):
                    y = check_page_break(y)
                    c.drawString(margin, y, f"  Record #{i + 1}:")
                    y -= line_height
                    if isinstance(record, dict):
                        for k, v in record.items():
                            y = check_page_break(y)
                            label = f"    • {k}: "
                            value_text = str(v) if v not in (None, "", False) else "(not provided)"
                            if v is True:
                                value_text = "Yes"
                            
                            # Handle long text
                            wrapped_lines = text_wrap(value_text, 70)
                            c.drawString(margin, y, label + wrapped_lines[0] if wrapped_lines else label)
                            y -= line_height
                            for extra_line in wrapped_lines[1:]:
                                y = check_page_break(y)
                                c.drawString(margin + 40, y, extra_line)
                                y -= line_height
            else:
                # Regular nested dictionary
                for key, value in data.items():
                    y = check_page_break(y)
                    label = f"  • {key}: "
                    
                    if isinstance(value, (list, dict)):
                        # Complex nested structure - stringify it
                        value_text = str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
                    else:
                        value_text = str(value) if value not in (None, "", False) else "(not provided)"
                        if value is True:
                            value_text = "Yes"
                    
                    # Handle long text
                    wrapped_lines = text_wrap(value_text, 70)
                    c.drawString(margin, y, label + wrapped_lines[0] if wrapped_lines else label)
                    y -= line_height
                    for extra_line in wrapped_lines[1:]:
                        y = check_page_break(y)
                        c.drawString(margin + 40, y, extra_line)
                        y -= line_height
                        
        else:
            # Handle simple values (string, number, boolean, etc.)
            value_text = str(data) if data not in (None, "", False) else "(not provided)"
            if data is True:
                value_text = "Yes"
            
            wrapped_lines = text_wrap(value_text, 90)
            for line in wrapped_lines:
                y = check_page_break(y)
                c.drawString(margin, y, f"  {line}")
                y -= line_height

        y -= 0.5 * line_height  # Extra space between sections

    # Footer on last page
    y = check_page_break(margin + 4 * line_height)
    c.line(margin, y, w - margin, y)
    y -= line_height
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(margin, y, "This document was generated automatically from survey responses.")
    y -= line_height
    c.drawString(margin, y, f"Generated on: {datetime.datetime.now():%Y-%m-%d at %H:%M}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()