document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    fetch('/login', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username, password: password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            localStorage.setItem('userID', JSON.stringify(data.data.userID))
            localStorage.setItem('personalInfo', JSON.stringify(data.data.personal_info));
            localStorage.setItem('timeline', JSON.stringify(data.data.timeline));
            localStorage.setItem('following_counts', JSON.stringify(data.data.following_counts));
            localStorage.setItem('followed_counts', JSON.stringify(data.data.followed_counts))
            window.location.href = 'homepage.html'; // Ensure you have home.html
        } else {
            alert("Invalid username or password");
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
