DROP TABLE IF EXISTS timeline;
DROP TABLE IF EXISTS userRelationship;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS registration;
DROP TABLE IF EXISTS userInfo;

CREATE TABLE userInfo (
    userID INTEGER primary key AUTOINCREMENT,
    display_name CHAR(50) not null,
    avatar text,
    bio text,
    gender CHAR(10),
    birthday date,
    age int,
    occupation char(30),
    education char(30),
    location_ char(30)
);

CREATE TABLE registration (
	user_account char(30) not null PRIMARY key,
    userID int,
    password_ char(30) not null,
	foreign key (userID) references userInfo(userID)
);

CREATE TABLE posts (
    postID INTEGER primary key AUTOINCREMENT,
    userID int not null,
    title text,
    content text,
    post_time datetime,
	FOREIGN key (userID) references userInfo(userID)
);

CREATE TABLE likes (
    postID int not null,
    userID int not null,
	foreign key (postID) references posts(postID),
	FOREIGN key (userID) references userInfo(userID)
);

CREATE TABLE comments (
    postID int not null,
    userID int not null,
    content text,
    comment_time datetime,
	foreign key (postID) references posts(postID),
	FOREIGN key (userID) references userInfo(userID)
);

CREATE TABLE userRelationship (
    followerID int not null,
    followingID int not null,
    closeness_rate float DEFAULT 0,
	foreign key (followerID) references userInfo(userID),
	foreign key (followingID) references userInfo(userID)
);

create TABLE timeline (
    userID int not null,
    postID int not null,
    post_userID int not null,
    post_time datetime,
    is_notified boolean,
	foreign key (userID) references userInfo(userID),
	foreign key (postID) references posts(postID),
	foreign key (post_userID) references userInfo(userID)
);
