CREATE TABLE IF NOT EXISTS tasks (
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    email TEXT,
    task TEXT,
    round INTEGER,
    nonce TEXT,
    brief TEXT,
    attachments TEXT,
    checks TEXT,
    evaluation_url TEXT,
    endpoint TEXT,
    statuscode INTEGER,
    secret TEXT
);

CREATE TABLE IF NOT EXISTS repos (
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    email TEXT,
    task TEXT,
    round INTEGER,
    nonce TEXT,
    repo_url TEXT,
    commit_sha TEXT,
    pages_url TEXT
);

CREATE TABLE IF NOT EXISTS results (
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    email TEXT,
    task TEXT,
    round INTEGER,
    repo_url TEXT,
    commit_sha TEXT,
    pages_url TEXT,
    check_name TEXT,
    score INTEGER,
    reason TEXT,
    logs TEXT
);