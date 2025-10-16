import os

def generate_app(brief: str, attachments: list[dict]) -> dict[str, str]:
    """
    Generates a simple HTML/JS application based on the brief and attachments.
    This is a placeholder for a more sophisticated LLM-based generator.
    """
    files = {}

    # Create a professional README.md
    readme_content = f"""
# Task: {brief}

This project is an auto-generated application to fulfill the requirements of the task.

## Description

{brief}

## Attachments

"""
    for attachment in attachments:
        readme_content += f"- {attachment['name']}\n"
    files["README.md"] = readme_content

    # Create an MIT License file
    license_content = """
MIT License

Copyright (c) 2023

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    files["LICENSE"] = license_content

    # Create a simple index.html
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brief}</title>
    <style>
        body {{ font-family: sans-serif; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        img {{ max-width: 100%; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{brief}</h1>
        <div id="app"></div>
    </div>
    <script src="app.js"></script>
</body>
</html>
"""
    files["index.html"] = html_content

    # Create a simple app.js
    js_content = f"""
document.addEventListener('DOMContentLoaded', () => {{
    const app = document.getElementById('app');
    app.innerHTML = `
        <p>This is a placeholder for the application logic.</p>
        <p>Brief: {brief}</p>
    `;

    const urlParams = new URLSearchParams(window.location.search);
    const imageUrl = urlParams.get('url');

    if (imageUrl) {{
        const img = document.createElement('img');
        img.src = imageUrl;
        app.appendChild(img);

        setTimeout(() => {{
            const solution = "Solved Captcha Text"; // Placeholder
            const solutionDiv = document.createElement('div');
            solutionDiv.textContent = solution;
            app.appendChild(solutionDiv);
        }}, 5000);
    }}
}});
"""
    files["app.js"] = js_content

    return files
