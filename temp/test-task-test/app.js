
document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    app.innerHTML = `
        <p>This is a placeholder for the application logic.</p>
        <p>Brief: Create a simple hello world app</p>
    `;

    const urlParams = new URLSearchParams(window.location.search);
    const imageUrl = urlParams.get('url');

    if (imageUrl) {
        const img = document.createElement('img');
        img.src = imageUrl;
        app.appendChild(img);

        setTimeout(() => {
            const solution = "Solved Captcha Text"; // Placeholder
            const solutionDiv = document.createElement('div');
            solutionDiv.textContent = solution;
            app.appendChild(solutionDiv);
        }, 5000);
    }
});
