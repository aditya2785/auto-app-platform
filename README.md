# Auto App Platform

The Auto App Platform is a fully automated system for building, deploying, and evaluating simple web applications. It consists of a student-facing API for receiving app-building tasks and an instructor-side set of scripts for managing the evaluation process.

## Features

- **Automated App Generation**: A FastAPI endpoint receives task descriptions and generates simple HTML/JS applications.
- **GitHub Integration**: Automatically creates GitHub repositories, pushes the generated code, and enables GitHub Pages.
- **Two-Round Evaluation Process**: Supports an initial build phase and a revision phase for iterative development.
- **Comprehensive Evaluation**: Scripts for evaluating submissions based on criteria like the presence of a LICENSE file, README quality, and Playwright tests.
- **Database Logging**: All tasks, submissions, and results are logged in a SQLite database.

## Project Structure

```
auto-app-platform/
├── database/
│   ├── db_utils.py
│   └── schema.sql
├── evaluation_scripts/
│   ├── round1.py
│   ├── evaluate.py
│   └── round2.py
├── student_api/
│   ├── app.py
│   ├── generator.py
│   └── github_helper.py
├── submissions.csv
├── requirements.txt
└── .gitignore
```

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/auto-app-platform.git
   cd auto-app-platform
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root directory.
   - Add your GitHub personal access token and a secret for the API:
     ```
     GITHUB_TOKEN=your_github_token
     API_SECRET=a_secure_secret
     ```

4. **Initialize the database:**
   ```bash
   python -m database.db_utils
   ```

5. **Install Playwright browsers:**
    ```bash
    playwright install
    ```

## How to Run

1. **Start the student API:**
   ```bash
   python -m student_api.app
   ```
   The API will be running at `http://localhost:8000`.

2. **Run the evaluation scripts:**

   - **Round 1: Send initial tasks**
     ```bash
     python -m evaluation_scripts.round1
     ```

   - **Evaluate submissions:**
     Before running the evaluation script, you need to add the repo information to the `repos` table. You can do this manually or by creating a simple script to listen for the evaluation notifications from the student API.

     ```bash
     python -m evaluation_scripts.evaluate
     ```

   - **Round 2: Send revision tasks**
     ```bash
     python -m evaluation_scripts.round2
     ```

## How It Works

### 1. Build Phase (Student Side)

- The `evaluation_scripts/round1.py` script reads the `submissions.csv` file and sends a POST request to the student API for each submission.
- The student API (`student_api/app.py`) receives the task, generates the application code using `student_api/generator.py`, and creates a new GitHub repository using `student_api/github_helper.py`.
- The student API then sends a notification to the `evaluation_url` with the repository information.

### 2. Evaluation Phase (Instructor Side)

- The `evaluation_scripts/evaluate.py` script fetches the repositories from the database, clones them, and evaluates them based on a set of checks.
- The evaluation includes checking for a `LICENSE` file, the quality of the `README.md`, and running Playwright tests.
- The results are stored in the `results` table in the database.

### 3. Revise Phase (Round 2 Updates)

- The `evaluation_scripts/round2.py` script generates new tasks for round 2 based on the evaluation results and sends them to the student API.
- The student API updates the existing repository with the new code and sends a notification to the `evaluation_url`.