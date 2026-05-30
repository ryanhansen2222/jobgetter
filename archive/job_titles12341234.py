#!/usr/bin/env python3
"""
Resume Job Title Suggester
Uses the Google Gemini API to analyze a resume (PDF or image)
and suggest suitable job titles based on the experience found.
"""

import google.genai as genai
import base64
import sys
import os
from pathlib import Path

# NOTE: Replace with the actual path to your resume file.
# It's generally good practice to pass this as a command-line argument
# or configure it dynamically, but for direct testing, you can set it here.
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
        data = base64.b64encode(f.read()).decode("utf-8") # Use b64encode directly

    return data, media_type


def suggest_job_titles(file_path: str, num_suggestions: int = 8) -> str:
    """
    Analyze a resume and suggest job titles using Google Gemini.

    Args:
        file_path: Path to the resume file (PDF or image)
        num_suggestions: Number of job title suggestions to generate

    Returns:
        String containing the job title suggestions and reasoning
    """
    # Configure the Gemini API client using the environment variable
    # The API key is usually automatically picked up if set as GOOGLE_API_KEY
    # but explicit configuration is good for clarity.
    #google_api_key = os.environ.get("GOOGLE_API_KEY")
    google_api_key = GOOGLE_API_KEY
    print(google_api_key)
    if not google_api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY environment variable is not set. "
            "Please set it to your Gemini API key."
        )
    genai.configure(api_key=google_api_key)

    # Initialize the Gemini Vision model
    # 'gemini-pro-vision' is suitable for multimodal inputs
    model = genai.GenerativeModel('gemini-pro-vision')

    print(f"Reading resume: {file_path}")
    file_data_base64, media_type = encode_file(file_path)

    # Gemini uses genai.upload_file for large files, or direct data for smaller ones.
    # For small files, we can create a Part object directly.
    # Note: Google models do not differentiate between 'document' and 'image' types
    # in the same way Anthropic does; it's all handled as a "fileData" part with mime_type.
    file_part = {
        "mime_type": media_type,
        "data": base64.b64decode(file_data_base64) # Gemini expects bytes here, not base64 string
    }

    # The prompt for Gemini
    prompt_text = f"""Please analyze this resume carefully and suggest {num_suggestions} job titles that would be an excellent match for this candidate.

For each suggestion, provide:
1. **Job Title** – the specific role name
2. **Why it fits** – 1–2 sentences explaining how their background aligns
3. **Seniority level** – e.g. Entry, Mid, Senior, Lead, Principal, Director

After the individual suggestions, add a brief **Summary** section (2–3 sentences) highlighting the candidate's strongest overall profile and the types of industries or companies where they'd thrive.

Format your response clearly with numbered suggestions."""

    print("Sending to Gemini API for analysis...")

    try:
        response = model.generate_content([file_part, prompt_text])
        # Access the text content from the response
        return response.text
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        # Depending on the error, you might want to print more details or re-raise
        # For production, consider structured logging and error handling.
        raise


def main():
    file_path = RESUME_PATH
    # Allow num_suggestions to be passed as a command-line argument
    # Default to 8 if not provided
    num_suggestions = 8
    if len(sys.argv) > 1:
        # Assuming the first argument might be the file path if RESUME_PATH is removed
        # For this setup, we'll assume num_suggestions is the first optional arg after the script name
        try:
            num_suggestions = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid number of suggestions '{sys.argv[1]}'. Using default of 8.")

    if not os.path.exists(file_path):
        print(f"Error: File not found at the configured path: {file_path}")
        sys.exit(1)

    try:
        result = suggest_job_titles(file_path, num_suggestions)

        print("\n" + "=" * 60)
        print("JOB TITLE SUGGESTIONS (Powered by Google Gemini)")
        print("=" * 60)
        print(result)
        print("=" * 60)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()