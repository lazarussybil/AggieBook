// const followersData = [
//     {
//         name: "Amy Dylan",
//         avatar: "./images/default.jpg",
//         bio: "It is a test signature!"
//     },
// ];

followerDDDDDDDDDDDDDDD

document.addEventListener("DOMContentLoaded", function() {

    const container = document.getElementById('followersContainer');
    followersData.forEach(follower => {
        // 创建follower容器
        const followerDiv = document.createElement('div');
        followerDiv.className = 'follower';

        // 创建并添加头像
        const img = document.createElement('img');
        img.src = follower.avatar;
        img.alt = follower.name;
        followerDiv.appendChild(img);

        // 创建并添加名字和签名
        const infoDiv = document.createElement('div');
        infoDiv.className = 'follower-info';

        const h2 = document.createElement('h2');
        h2.textContent = follower.name;
        infoDiv.appendChild(h2);

        const p = document.createElement('p');
        p.textContent = follower.bio;
        infoDiv.appendChild(p);

        followerDiv.appendChild(infoDiv);
        container.appendChild(followerDiv);
    });
});
