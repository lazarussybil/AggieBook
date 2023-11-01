
const followingsData = [
    {
        name: "John Doe",
        avatar: "./images/test.jpg",
        bio: "I love coding!"
    },
    {
        name: "Jane Smith",
        avatar: "./images/default2.jpg",
        bio: "Travel enthusiast"
    },
];

document.addEventListener("DOMContentLoaded", function() {

    const container = document.getElementById('followingsContainer');
    followingsData.forEach(following => {
        // 创建following容器
        const followingDiv = document.createElement('div');
        followingDiv.className = 'following';

        // 创建并添加头像
        const img = document.createElement('img');
        img.src = following.avatar;
        img.alt = following.name;
        followingDiv.appendChild(img);

        // 创建并添加名字和签名
        const infoDiv = document.createElement('div');
        infoDiv.className = 'following-info';

        const h2 = document.createElement('h2');
        h2.textContent = following.name;
        infoDiv.appendChild(h2);

        const p = document.createElement('p');
        p.textContent = following.bio;
        infoDiv.appendChild(p);

        followingDiv.appendChild(infoDiv);
        container.appendChild(followingDiv);
    });
});
