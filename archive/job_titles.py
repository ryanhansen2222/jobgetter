#!/usr/bin/env python3
"""
Resume Job Title Suggester
Uses the Anthropic Claude API to analyze a resume (PDF or image)
and suggest suitable job titles based on the experience found.
"""

import anthropic
import base64
import sys
import os
from pathlib import Path

RESUME_PATH = "C:\\Users\\ryanr\\Downloads\\RyanHansen_ATS_05_26_AI_ENG (4).pdf"


def encode_file(file_path: str) -> tuple[str, str]:
    """Encode a file to base64 and determine its media type."""
    path = Path(file_path)
    ext = path.suffix.lower()

    media_type_map = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    media_type = media_type_map.get(ext)
    if not media_type:
        raise ValueError(
            f"Unsupported file type: {ext}. "
            "Supported types: PDF, PNG, JPG, JPEG, WEBP, GIF"
        )

    with open(file_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    return data, media_type


def suggest_job_titles(file_path: str, num_suggestions: int = 8) -> str:
    """
    Analyze a resume and suggest job titles.

    Args:
        file_path: Path to the resume file (PDF or image)
        num_suggestions: Number of job title suggestions to generate

    Returns:
        String containing the job title suggestions and reasoning
    """
    client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

    print(f"Reading resume: {file_path}")
    file_data, media_type = encode_file(file_path)

    # Build the content block depending on file type
    if media_type == "application/pdf":
        file_content = {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": file_data,
            },
        }
    else:
        file_content = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": file_data,
            },
        }

    prompt = f"""Please analyze this resume carefully and suggest {num_suggestions} job titles that would be an excellent match for this candidate.

For each suggestion, provide:
1. **Job Title** – the specific role name
2. **Why it fits** – 1–2 sentences explaining how their background aligns
3. **Seniority level** – e.g. Entry, Mid, Senior, Lead, Principal, Director

After the individual suggestions, add a brief **Summary** section (2–3 sentences) highlighting the candidate's strongest overall profile and the types of industries or companies where they'd thrive.

Format your response clearly with numbered suggestions."""

    print("Sending to Claude API for analysis...")
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": [
                    file_content,
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    return message.content[0].text


def main():


    file_path = RESUME_PATH
    num_suggestions = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Get your key at https://console.anthropic.com/")
        sys.exit(1)

    result = suggest_job_titles(file_path, num_suggestions)

    print("\n" + "=" * 60)
    print("JOB TITLE SUGGESTIONS")
    print("=" * 60)
    print(result)
    print("=" * 60)


if __name__ == "__main__":
    main()