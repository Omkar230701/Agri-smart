import re
import markdown
from datetime import datetime

def validate_api_key_format(key: str) -> bool:
    return len(key) > 20 and " " not in key

def estimate_tokens(text: str) -> int:
    return len(text.split()) * 1.5

def extract_checklist_items(markdown_text: str):
    pattern = r"- \[ \] (.+)"
    matches = re.findall(pattern, markdown_text)
    if matches:
        return matches

    # fallback: extract bullet steps
    bullets = re.findall(r"[-•] (.+)", markdown_text)
    return bullets[:10] if bullets else None

def export_to_markdown(question, answer, topic, checklist=None):
    md = f"# AgriSmart Farming Advice\n\n"
    md += f"### Topic: {topic}\n"
    md += f"### Question:\n{question}\n\n"
    md += f"### Answer:\n{answer}\n\n"

    if checklist:
        md += "### Checklist:\n"
        for item in checklist:
            md += f"- [ ] {item}\n"

    md += f"\nGenerated on {datetime.now()}"
    return md

def format_markdown_response(response: str):
    return markdown.markdown(response)

