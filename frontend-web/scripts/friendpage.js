// Sample data

// Sample data
let currentUserID = localStorage.getItem("userID");
let users = [];

document.getElementById('searchButton').addEventListener('click', function() {
    const token = document.getElementById('searchInput').value;

    // Fetch users from the server based on the search token
    fetch('/users/searchUser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            userID: currentUserID,
            token: token
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            users = data.data.users;
            // alert(`users ${JSON.parse(users)} !`);
            populateUserList();
        } else {
            alert('Error fetching users.');
        }
    });
});


// This function now clears the user list and repopulates it
function populateUserList() {
    const userList = document.getElementById('userList');
    userList.innerHTML = ''; // Clear the user list

    users.forEach(user => {
        const listItem = document.createElement('li');

        const avatarImg = document.createElement('img');
        avatarImg.src = "images/default.jpg";
        avatarImg.alt = user.display_name;
        avatarImg.className = 'avatar';

        const displayNameSpan = document.createElement('span');
        displayNameSpan.innerText = user.display_name;

        const button = document.createElement('button');
        if (user.is_following) {
            button.innerText = 'Unfollow';
            button.className = 'unfollow';
            button.onclick = function() {
                updateUserFollowStatus(user._id, false);
            };
        } else {
            button.innerText = 'Follow';
            button.className = 'follow';
            button.onclick = function() {
                updateUserFollowStatus(user._id, true);
            };
        }

        listItem.appendChild(avatarImg);
        listItem.appendChild(displayNameSpan);
        listItem.appendChild(button);

        userList.appendChild(listItem);
    });
}

function updateUserFollowStatus(targetUserID, follow) {
    const endpoint = follow ? '/users/follow' : '/users/unfollow';
    // alert(`UserID ${currentUserID} targetUserID ${targetUserID}!`);

    // Send the current userID and target userID  to the backend
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            userID: currentUserID,
            target_user_id: targetUserID
        })
    })
    .then(response => response.json())
    .then(data => {
        localStorage.setItem('timeline', JSON.stringify(data.data.timeline));
        localStorage.setItem('following_counts', JSON.stringify(data.data.following_counts));
        localStorage.setItem('followed_counts', JSON.stringify(data.data.followed_counts));
        const action = follow ? 'followed' : 'unfollowed';
        if (data.status === 'success') {
            alert(`User ${action} successfully!`);
            location.reload();
        } else {
            alert(`Error ${action} user.`);
        }
    });
}

// Initialize
populateUserList();
