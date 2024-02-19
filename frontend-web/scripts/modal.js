
const modal = document.getElementById('modal');
const CommentCloseModalButton = document.getElementById('commentCloseModalButton');
const commentInput = document.getElementById('commentInput');
const addCommentButton = document.getElementById('addCommentButton');
const commentList = document.getElementById('commentList');
let modalPostIndex = 0;

// monitor close modal button
CommentCloseModalButton.addEventListener('click', () => {
    modal.style.display = 'none';
});

// monitor add comment button
addCommentButton.addEventListener('click', () => {
    const commentText = commentInput.value;
    if (commentText.trim() !== '') {
        const commentItem = document.createElement('li');
        commentItem.textContent = username + " : " + commentText;
        postID = posts[modalPostIndex].postID;

        posts[modalPostIndex].comments.push({username: username, content: commentText});
        commentList.appendChild(commentItem);

        fetch('/posts/comment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userID: localStorage.getItem('userID'), postID: postID, content: commentText}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                localStorage.setItem('timeline', JSON.stringify(data.data.timeline));
            } else {
                alert("Invalid username or password");
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        commentInput.value = '';
    }
});
