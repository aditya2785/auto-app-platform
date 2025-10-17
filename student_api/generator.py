import os
import re
import json
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo"

def create_prompt(brief: str, processed_data: dict) -> str:
    """
    Creates a prompt for the LLM to generate the application code.
    """
    prompt = f"""
You are an expert web developer. Your task is to build a single-page web application based on the following brief and data.

**Brief:**
{brief}

**Data:**
"""
    for name, data in processed_data.items():
        prompt += f"**{name}:**\n```json\n{json.dumps(data, indent=2)}\n```\n"

    prompt += """
**Instructions:**
- Generate a complete HTML file with embedded CSS and JavaScript.
- The application should be fully functional and meet all the requirements of the brief.
- Use the provided attachments to populate the application with data.
- Ensure that all the required elements are present and have the correct IDs.
- Generate a professional README.md file with setup instructions, code explanation, usage, and a license.
- Generate an MIT LICENSE file.

**Output Format:**
Please generate the files in the following format, with each file enclosed in a code block with the specified language.

```html
<!-- index.html -->
...
```

```markdown
<!-- README.md -->
...
```

```text
<!-- LICENSE -->
...
```
"""
    return prompt

def parse_generated_code(generated_code: str) -> dict[str, str]:
    """
    Parses the generated code and splits it into files.
    """
    files = {}
    file_patterns = {
        "index.html": r"```html\n<!-- index.html -->\n(.*?)\n```",
        "README.md": r"```markdown\n<!-- README.md -->\n(.*?)\n```",
        "LICENSE": r"```text\n<!-- LICENSE -->\n(.*?)\n```",
    }

    for file_name, pattern in file_patterns.items():
        match = re.search(pattern, generated_code, re.DOTALL)
        if match:
            files[file_name] = match.group(1).strip()

    return files

def generate_app(brief: str, processed_data: dict) -> dict[str, str]:
    """
    Generates a simple HTML/JS application based on the brief and processed data.
    """
    prompt = create_prompt(brief, processed_data)

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
        )
        generated_code = response.choices[0].message.content
        files = parse_generated_code(generated_code)
        return files
    except Exception as e:
        print(f"Error generating code: {e}")
        return {}