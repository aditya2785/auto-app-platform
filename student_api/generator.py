import os

def generate_app(task_info):
    task_name = task_info["task"]
    app_path = os.path.join("student_apps", task_name)
    os.makedirs(app_path, exist_ok=True)

    # Minimal HTML/JS placeholder
    html_content = f"<html><body><h1>{task_info['brief']}</h1></body></html>"
    with open(os.path.join(app_path, "index.html"), "w") as f:
        f.write(html_content)

    # Add README.md
    readme_content = f"# {task_name}\n\nGenerated app.\n"
    with open(os.path.join(app_path, "README.md"), "w") as f:
        f.write(readme_content)

    # Add MIT LICENSE
    mit_content = "MIT License..."
    with open(os.path.join(app_path, "LICENSE"), "w") as f:
        f.write(mit_content)

    return app_path
