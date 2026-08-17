"""Gmail SMTP email dispatch module for sending ranked job shortlists."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


def send_job_digest_email(
    to_email: Optional[str] = None,
    matched_jobs: Optional[List[Dict[str, Any]]] = None,
    subject: str = "🎯 NGO Job Openings - Ranked Matches Digest"
) -> Dict[str, Any]:
    """Send ranked job shortlist email using Gmail SMTP."""
    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient = to_email or os.getenv("DEFAULT_RECIPIENT_EMAIL") or sender_email
    
    if not sender_email or not sender_password:
        return {
            "status": "error",
            "error": "GMAIL_USER or GMAIL_APP_PASSWORD not set in environment or .env file. Generate a Google App Password to enable email."
        }
        
    if not recipient:
        return {"status": "error", "error": "No recipient email address specified"}
        
    if not matched_jobs:
        return {"status": "error", "error": "No matched jobs provided to email"}
        
    # Construct Plain Text Body
    text_lines = [f"Found {len(matched_jobs)} Top NGO Job Matches:\n"]
    for idx, job in enumerate(matched_jobs, 1):
        text_lines.append(f"{idx}. {job.get('title')} - {job.get('organization')}")
        text_lines.append(f"   Location: {job.get('location')} | Source: {job.get('source')}")
        text_lines.append(f"   Match Score: {job.get('total_score')}/100 | {job.get('fit_note')}")
        text_lines.append(f"   Apply Link: {job.get('url')}\n")
        
    text_body = "\n".join(text_lines)
    
    # Construct Clean HTML Body
    html_items = []
    for idx, job in enumerate(matched_jobs, 1):
        item_html = f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: #fafafa;">
            <h3 style="margin-top: 0; color: #1a5276;">
                #{idx} <a href="{job.get('url')}" target="_blank" style="text-decoration: none; color: #1a5276;">{job.get('title')}</a>
            </h3>
            <p style="margin: 5px 0; color: #333;"><strong>Organization:</strong> {job.get('organization')}</p>
            <p style="margin: 5px 0; color: #555;"><strong>Location:</strong> {job.get('location')} | <strong>Source:</strong> {job.get('source')}</p>
            <div style="display: inline-block; background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-top: 5px;">
                Score: {job.get('total_score')}/100
            </div>
            <p style="margin-top: 8px; color: #5d6d7e; font-style: italic;">💡 {job.get('fit_note')}</p>
            <a href="{job.get('url')}" target="_blank" style="display: inline-block; background-color: #2980b9; color: white; padding: 8px 12px; border-radius: 4px; text-decoration: none; font-weight: bold; margin-top: 8px;">View & Apply &rarr;</a>
        </div>
        """
        html_items.append(item_html)
        
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 650px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px;">🎯 NGO Job Shortlist Digest</h2>
        <p>Here are your top <strong>{len(matched_jobs)}</strong> matched NGO job openings based on your resume profile:</p>
        {"".join(html_items)}
        <hr style="border: none; border-top: 1px solid #eee; margin-top: 30px;" />
        <p style="font-size: 12px; color: #95a5a6; text-align: center;">Sent automatically by NGO Jobs MCP Server</p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient
    
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [recipient], msg.as_string())
            
        return {
            "status": "success",
            "message": f"Successfully emailed {len(matched_jobs)} job matches to {recipient}",
            "recipient": recipient,
            "matched_count": len(matched_jobs)
        }
    except Exception as err:
        return {"status": "error", "error": f"Failed to send email via Gmail SMTP: {str(err)}"}
