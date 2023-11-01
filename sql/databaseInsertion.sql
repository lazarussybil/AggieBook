DELETE FROM timeline;
DELETE FROM userRelationShip;
DELETE FROM comments;
DELETE FROM likes;
DELETE FROM posts;
DELETE FROM registration;
DELETE FROM userInfo;

-- Insertion 1
INSERT INTO userInfo 
(userID, display_name, avatar, bio, gender, birthday, age, occupation, education, location_) 
VALUES 
(1, 'Ross Li', 'https://example.com/avatar1.png', null, 'Male', '2000-06-25', 22, 'Software Engineer', 'Masters', 'TX');

-- Insertion 2
INSERT INTO userInfo VALUES 
(2, 'Jane Smith', 'https://example.com/avatar2.png', null, 'Female', null, null, 'Data Scientist', 'Bachelors', 'NY');



INSERT INTO registration 
(user_account, userID, password_) 
VALUES 
('john.doe@example.com', 1, 'passwordForJohn');

-- Insertion 2
INSERT INTO registration VALUES 
('jane.smith@example.com', 2, 'passwordForJane');



-- Assuming we already have the users with IDs 1 and 2 in the userInfo table
-- Insertion 1
INSERT INTO posts 
(postID, userID, title, content, post_time) 
VALUES 
(1, 1, 'My First Post', 'This is the content of my first post.', '2023-10-01 10:00:00');

-- Insertion 2
INSERT INTO posts VALUES 
(null, 2, 'Jane''s Adventures', 'Today, I went hiking and it was fun!',  '2023-10-02 12:30:00');


-- Assuming we already have a post with postID 1 and users with IDs 1 and 2
-- Insertion 1: User with userID 1 likes the post with postID 1
INSERT INTO likes 
(postID, userID) 
VALUES 
(1, 1);

-- Insertion 2: User with userID 2 also likes the post with postID 1
INSERT INTO likes VALUES 
(1, 2);


-- Assuming we already have a post with postID 1 and users with IDs 1 and 2
-- Insertion 1: User with userID 1 comments on the post with postID 1
INSERT INTO comments 
(postID, userID, content, comment_time) 
VALUES 
(1, 1, 'Great post! Thanks for sharing.', '2023-10-01 10:30:00');

-- Insertion 2: User with userID 2 also comments on the post with postID 1
INSERT INTO comments VALUES 
(1, 2, 'I found this very informative. Keep it up!', '2023-10-01 11:00:00');



-- Assuming we already have users with IDs 1 and 2 in the userInfo table
-- Insertion 1: User with followerID 1 follows the user with followingID 2 with a default closeness rate
INSERT INTO userRelationship 
(followerID, followingID) 
VALUES 
(1, 2);

-- Insertion 2: User with followerID 2 follows the user with followingID 1 with a specific closeness rate
INSERT INTO userRelationship 
(followerID, followingID, closeness_rate) 
VALUES 
(2, 1, 0.75);


-- Assuming we have users with IDs 1, 2, and 3 and a post with postID 1 posted by user with userID 2
-- Insertion 1: The post with postID 1 (created by user 2) appears on the timeline of user 1
INSERT INTO timeline 
(userID, postID, post_userID, post_time, is_notified) 
VALUES 
(1, 1, 2, '2023-10-01 12:00:00', FALSE);

-- Insertion 2: The post with postID 1 (created by user 2) also appears on the timeline of user 3
INSERT INTO timeline 
(userID, postID, post_userID, post_time, is_notified) 
VALUES 
(2, 1, 2, '2023-10-01 12:15:00', TRUE);
