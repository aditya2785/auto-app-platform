# Deploying Your API for Evaluation

To get a public URL for your API, you can use a tool like `ngrok`. `ngrok` creates a secure tunnel to your local machine, allowing you to share your local server with the world.

## 1. Install ngrok

You can download and install `ngrok` from the official website: https://ngrok.com/download

## 2. Get Your Authtoken

You'll need to sign up for a free `ngrok` account to get an authtoken. You can find your authtoken on your `ngrok` dashboard.

## 3. Run Your API

Start your FastAPI application by running the following command in your terminal:

```bash
python -m uvicorn student_api.app:app --host 0.0.0.0 --port 8000
```

## 4. Start ngrok

Open a new terminal window and run the following command, replacing `<YOUR_AUTHTOKEN>` with your `ngrok` authtoken:

```bash
ngrok http 8000 --authtoken <YOUR_AUTHTOKEN>
```

## 5. Get Your Public URL

`ngrok` will display a "Forwarding" URL that looks something like this:

```
Forwarding                    https://<random-string>.ngrok-free.app -> http://localhost:8000
```

The `https://` URL is your public API endpoint. You can now use this URL to submit your project for evaluation. For example, your submission URL would be `https://<random-string>.ngrok-free.app/api-endpoint`.