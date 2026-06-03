#!/usr/bin/env python3
"""
Job Description AI Analyzer
Loads job listings from a CSV, runs Claude analysis on each description,
and saves results incrementally so progress is never lost.

Usage:
    python analyze_jobs.py --input full_job_data.csv.csv --output results.csv
    python analyze_jobs.py --input full_job_data.csv.csv --output results.csv --limit 50
    python analyze_jobs.py --input full_job_data.csv.csv --output results.csv --resume
"""

import anthropic
import pandas as pd
import time
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
DATA_PATH = '../data/'

# ── Configuration ─────────────────────────────────────────────────────────────

MODEL = "claude-haiku-4-5"          # cheapest model; swap to claude-sonnet-4-5 for quality
MAX_DESC_CHARS = 2000               # truncate long descriptions to save tokens
MAX_OUTPUT_TOKENS = 400             # per-job response length
REQUESTS_PER_MINUTE = 50           # stay safely under API rate limits
RETRY_ATTEMPTS = 3                  # retries on transient errors
RETRY_DELAY = 5                     # seconds between retries

SYSTEM_PROMPT = """You are a job market analyst. Given a job description, respond with a concise JSON object containing:
- "seniority": one of [entry, mid, senior, lead, principal, director, executive]
- "category": the broad job category (e.g. "Software Engineering", "Data Science", "Product Management")
- "skills": list of up to 5 key required skills
- "remote": true/false based on whether remote work is mentioned
- "summary": one sentence describing the role

Respond with JSON only. No markdown, no explanation."""

ANALYSIS_PROMPT = """Analyze this job description:

{description}"""


# ── Core Analysis ──────────────────────────────────────────────────────────────

def analyze_job(client: anthropic.Anthropic, description: str) -> dict:
    """Call Claude API to analyze a single job description."""
    truncated = description[:MAX_DESC_CHARS] if len(description) > MAX_DESC_CHARS else description

    for attempt in range(RETRY_ATTEMPTS):
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": ANALYSIS_PROMPT.format(description=truncated)}
                ]
            )
            raw = message.content[0].text.strip()

            import json
            result = json.loads(raw)
            result["_tokens_in"] = message.usage.input_tokens
            result["_tokens_out"] = message.usage.output_tokens
            result["_error"] = None
            return result

        except anthropic.RateLimitError:
            wait = 60 if attempt < RETRY_ATTEMPTS - 1 else 0
            print(f"    Rate limit hit — waiting {wait}s...")
            time.sleep(wait)

        except anthropic.APIStatusError as e:
            if attempt < RETRY_ATTEMPTS - 1:
                print(f"    API error ({e.status_code}), retry {attempt + 1}...")
                time.sleep(RETRY_DELAY)
            else:
                return {"_error": str(e), "_tokens_in": 0, "_tokens_out": 0}

        except Exception as e:
            return {"_error": str(e), "_tokens_in": 0, "_tokens_out": 0}

    return {"_error": "Max retries exceeded", "_tokens_in": 0, "_tokens_out": 0}


# ── CSV Helpers ────────────────────────────────────────────────────────────────

def load_progress(output_path: str) -> set:
    """Return set of already-processed row indices from a partial output file."""
    if not os.path.exists(output_path):
        return set()
    try:
        done = pd.read_csv(output_path)
        return set(done["_original_index"].dropna().astype(int).tolist())
    except Exception:
        return set()


def get_description(row) -> str:
    """Extract description text from a row, handling the source/site column split."""
    desc = row.get("description", "")
    if pd.isna(desc) or str(desc).strip() == "":
        return ""
    return str(desc).strip()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyze job descriptions with Claude API")
    parser.add_argument("--input",  required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--limit",  type=int, default=None, help="Only process first N jobs")
    parser.add_argument("--resume", action="store_true", help="Skip already-processed rows")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    # Load data
    print(f"Loading {args.input}...")
    df = pd.read_csv(args.input)
    df["_original_index"] = df.index

    # Combine source columns
    df["_source"] = df["source"].fillna(df["site"]) if "site" in df.columns else df.get("source", "unknown")

    if args.limit:
        df = df.head(args.limit)
        print(f"Limited to first {args.limit} rows.")

    total = len(df)
    print(f"Total jobs to process: {total}")

    # Resume support
    done_indices = set()
    if args.resume:
        done_indices = load_progress(args.output)
        print(f"Resuming — {len(done_indices)} already done, {total - len(done_indices)} remaining.")

    client = anthropic.Anthropic()
    results = []
    delay = 60 / REQUESTS_PER_MINUTE

    total_tokens_in = 0
    total_tokens_out = 0
    errors = 0
    start_time = datetime.now()

    # Open output file for incremental writing
    output_exists = os.path.exists(args.output) and args.resume
    write_header = not output_exists

    for i, (_, row) in enumerate(df.iterrows()):
        idx = int(row["_original_index"])

        if idx in done_indices:
            continue

        desc = get_description(row)
        if not desc:
            result = {"_error": "no description", "_tokens_in": 0, "_tokens_out": 0}
        else:
            result = analyze_job(client, desc)

        # Build output row
        out_row = {
            "_original_index": idx,
            "company":  row.get("company", ""),
            "title":    row.get("title", ""),
            "location": row.get("location", ""),
            "source":   row.get("_source", ""),
            "url":      row.get("url", ""),
            "seniority":  result.get("seniority", ""),
            "category":   result.get("category", ""),
            "skills":     str(result.get("skills", "")),
            "remote":     result.get("remote", ""),
            "summary":    result.get("summary", ""),
            "_tokens_in":  result.get("_tokens_in", 0),
            "_tokens_out": result.get("_tokens_out", 0),
            "_error":      result.get("_error", ""),
        }

        total_tokens_in  += result.get("_tokens_in", 0)
        total_tokens_out += result.get("_tokens_out", 0)
        if result.get("_error"):
            errors += 1

        # Write incrementally (append mode after first row)
        out_df = pd.DataFrame([out_row])
        out_df.to_csv(args.output, mode="a", header=write_header, index=False)
        write_header = False

        # Progress logging
        processed = i + 1
        elapsed = (datetime.now() - start_time).total_seconds()
        rate = processed / elapsed if elapsed > 0 else 0
        eta_s = (total - processed) / rate if rate > 0 else 0
        eta_m = eta_s / 60

        print(
            f"[{processed:>5}/{total}] "
            f"{row.get('company','')[:20]:<20} | "
            f"{result.get('category','error'):<25} | "
            f"tokens in/out: {result.get('_tokens_in',0):>4}/{result.get('_tokens_out',0):<4} | "
            f"ETA: {eta_m:.1f}m"
        )

        time.sleep(delay)

    # Summary
    elapsed_total = (datetime.now() - start_time).total_seconds()
    haiku_cost = (total_tokens_in / 1e6 * 0.80) + (total_tokens_out / 1e6 * 4.00)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print(f"  Processed:    {total - len(done_indices)} jobs")
    print(f"  Errors:       {errors}")
    print(f"  Tokens in:    {total_tokens_in:,}")
    print(f"  Tokens out:   {total_tokens_out:,}")
    print(f"  Est. cost:    ${haiku_cost:.4f} (Haiku pricing)")
    print(f"  Time elapsed: {elapsed_total/60:.1f} minutes")
    print(f"  Output saved: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()