document.getElementById("registerForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let username = document.getElementById("newUsername").value;
    let password = document.getElementById("newPassword").value;
    let displayname = document.getElementById("newDisplayName").value;

    fetch('/users/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username, password: password, displayname: displayname}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // localStorage.setItem('personalInfo', JSON.stringify(data.data));
            window.location.href = 'login.html'; // Ensure you have home.html
        } else {
            alert("Invalid username or password or displayname");
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
