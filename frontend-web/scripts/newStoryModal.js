const newStoryTitleInput = document.getElementById('newStoryTitle');
const newStoryContentTextarea = document.getElementById('newStoryContent');
const newStoryCompleteBtn = document.getElementById('newStoryCompleteBtn');
const newStoryCancelBtn = document.getElementById('newStoryCancelBtn');

function openNewStoryModal() {
    document.getElementById("newStoryModal").style.display = "block";
}

function closeNewStoryModal() {
    document.getElementById("newStoryModal").style.display = "none";
}

newStoryCompleteBtn.addEventListener('click', () => {
    let title = newStoryTitleInput.value.trim();
    let content = newStoryContentTextarea.value.trim();

    if (title === '' || content === '') {
        alert('title or content cannot be empty');
    } else {
        
        fetch('/newstory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userID: localStorage.getItem('userID'), title: title, content: content}),
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

        newStoryTitleInput.value = '';
        newStoryContentTextarea.value = '';
        alert('Your post has been sent!');
        closeNewStoryModal();
        freshPosts();
    }
})

newStoryCancelBtn.addEventListener('click', closeNewStoryModal);