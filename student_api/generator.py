import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

TEXT_MODEL = "models/text-bison-001"        # Free text model
VISION_MODEL = "models/vision-bison-001"    # Free vision model

def solve_captcha(image_data_uri: str) -> str:
    """
    Solves the captcha from a data URI using Gemini's free vision model.
    """
    try:
        model = genai.GenerativeModel(VISION_MODEL)
        prompt = "Read the text from this captcha image."
        response = model.generate_content([prompt, image_data_uri])
        return response.text.strip() if response and response.text else "Could not solve captcha"
    except Exception as e:
        print(f"Error solving captcha with Gemini: {e}")
        return "Error solving captcha"

def create_prompt(brief: str, processed_data: dict, captcha_solution: str) -> str:
    """
    Creates a prompt for the LLM to generate the application code.
    """
    sample_image_uri = ""
    for name, data in processed_data.items():
        if name.endswith((".png", ".jpg", ".jpeg")):
            sample_image_uri = data
            break

    prompt = f"""
You are an expert web developer. Your task is to build a single-page web application based on the following brief.

**Brief:**
{brief}

**Application Requirements:**
1. The page must display a captcha image.
2. The image URL is provided via a `?url=` query parameter.
3. If the `?url=` parameter is not present, the page should default to displaying the sample captcha image provided below.
4. Below the image, the page must display the solved text of the captcha.
5. The solved text for the sample captcha is: **{captcha_solution}**
6. The application must be a single `index.html` file with embedded CSS and JavaScript. No external files.
7. The solved captcha text must be displayed within 15 seconds of the page loading. The provided solution should be used.

**Sample Captcha Image Data URI:**
`{sample_image_uri}`

**Instructions:**
- Generate a complete HTML file with embedded CSS and JavaScript.
- The JavaScript code should parse the `?url=` query parameter from the window's location.
- If the URL parameter exists, use it as the `src` for the captcha `<img>` tag.
- If the URL parameter does not exist, use the Sample Captcha Image Data URI as the `src`.
- The solved captcha text, `{captcha_solution}`, should be hardcoded into the HTML or JavaScript and displayed on the page. **Do not try to solve it on the client side.**
- Generate a professional README.md file with setup instructions, code explanation, usage, and a license.
- Generate an MIT LICENSE file.

**Output Format:**
```html
<!-- index.html -->
...
<!-- README.md -->
...
<!-- LICENSE -->
...
"""
return prompt

def parse_generated_code(generated_code: str) -> dict[str, str]:
"""
Parses the generated code and splits it into files.
"""
files = {}
file_patterns = {
"index.html": r"html\n<!-- index.html -->\n(.*?)\n",
"README.md": r"markdown\n<!-- README.md -->\n(.*?)\n",
"LICENSE": r"text\n<!-- LICENSE -->\n(.*?)\n",
}
for file_name, pattern in file_patterns.items():
    match = re.search(pattern, generated_code, re.DOTALL)
    if match:
        files[file_name] = match.group(1).strip()

return files
def generate_app(brief: str, processed_data: dict) -> dict[str, str]:
"""
Generates a simple HTML/JS application based on the brief and processed data using Gemini.
"""
sample_image_uri = ""
for name, data in processed_data.items():
if name.endswith((".png", ".jpg", ".jpeg")):
sample_image_uri = data
break
captcha_solution = solve_captcha(sample_image_uri) if sample_image_uri else "No sample image provided."
prompt = create_prompt(brief, processed_data, captcha_solution)

try:
    response = genai.chat(
        model=TEXT_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert web developer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    generated_code = response["candidates"][0]["content"]
    files = parse_generated_code(generated_code)
    return files
except Exception as e:
    print(f"Error generating code with Gemini: {e}")
    return {"error": "Gemini API error"}
