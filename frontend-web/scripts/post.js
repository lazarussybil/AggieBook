// const posts = [
//     {
//         title: 'Post Title 1',
//         content: 'This is the content of the first post.',
//         likes: 3,
//         isLiked: false,
//         comments: [
//             ["fan1", "This is the content of the fan1 comment"],
//             ["Longxiang Li", "hello?"],
//             ["fan2", "This is the content of the fan2 comment"],
//         ],
//     },
//     {
//         title: 'Post Title 2',
//         content: 'This is the content of the second post.',
//         likes: 5,
//         isLiked: false,
//         comments: [],
//     },
//     {
//         title: 'Post Title 3',
//         content: 'This is the content of the third post.',
//         likes: 6,
//         isLiked: false,
//         comments: [],
//     }
// ];

// posts = localStorage.getItem("timeline");
const postContainer = document.querySelector('.post-container');

function freshPosts() {
    posts = JSON.parse(localStorage.getItem("timeline"));
    // window.alert("update");

    document.querySelectorAll('.post').forEach(function(element) {
        element.remove();
    });
    

    posts.forEach((post, index) => {
        const postElement = document.createElement('div');
        postElement.classList.add('post');
        // window.alert("you like a post");
    
        const titleElement = document.createElement('h2');
        titleElement.textContent = post.title;
        // titleElement.textContent = post["title"];
    
        const contentElement = document.createElement('p');
        contentElement.textContent = post.content;
        // contentElement.textContent = post["content"];

        const likeButton = document.createElement('button');
        likeButton.classList.add('like-button');
        likeButton.textContent = `Like(${post.likes})`;
        likeButton.id = `likeButton${index}`; 
    
    
        const commentButton = document.createElement('button');
        commentButton.classList.add('comment-button');
        commentButton.textContent = 'Comment';
        commentButton.id = `commentButton${index}`; 
        
        let counter = post.likes;
        // let counter = post["likes"];
        let isLiked = post.isLiked; 
        // let isLiked = post["isLiked"]; 
    
        likeButton.addEventListener('click', () => {
            if (isLiked) {
                counter -= 1;
            } else {
                counter += 1;
            }
            likeButton.textContent = `Like(${counter})`;
            isLiked = !isLiked; 
            let postID = post.postID;
            // isLiked = !isLiked;
            fetch('/like', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userID: localStorage.getItem('userID'), postID: postID}),
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
            // freshPosts();
        });
    
        commentButton.addEventListener('click', () => {
            modal.style.display = 'block';
    
            const postTitle = post.title;
            const postContent = post.content;
            const postLikes = counter;
            const modalPostContent = document.querySelector('.modal .post-content');
            const commentList = document.getElementById('commentList');
            modalPostIndex = parseInt(commentButton.id.substring(13))
            // modalPostIndex = 0
            modalPostContent.innerHTML = `<h2>${postTitle}</h2><p>${postContent}</p><span class="like-count">${postLikes}</span> Likes`;
            
            commentList.innerHTML = '';
            comments = post.comments;
            comments.forEach(element => {
                const commentItem = document.createElement('li');
                commentItem.textContent = element.username + " : " + element.content;
                commentList.appendChild(commentItem);
            });
        });
    
        postElement.appendChild(titleElement);
        postElement.appendChild(contentElement);
        postElement.appendChild(likeButton);
        postElement.appendChild(commentButton);
        postContainer.appendChild(postElement);
    });    
}

freshPosts();
