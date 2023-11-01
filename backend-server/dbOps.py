import sqlite3
import datetime

DATABASE_PATH = "..\\sql\\AggieBookDatabase.db"
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn


def get_followers(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query for users who are following the current user
    cursor.execute("""
        SELECT userInfo.userID, userInfo.display_name 
        FROM userInfo 
        INNER JOIN userRelationship ON userInfo.userID = userRelationship.followerID
        WHERE userRelationship.followingID = ?
    """, (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert the results to a list of dictionaries
    followers = [{'userID': row[0], 'display_name': row[1]} for row in results]
    return followers

def get_following(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query for users that the current user is following
    cursor.execute("""
        SELECT userInfo.userID, userInfo.display_name 
        FROM userInfo 
        INNER JOIN userRelationship ON userInfo.userID = userRelationship.followingID
        WHERE userRelationship.followerID = ?
    """, (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert the results to a list of dictionaries
    following = [{'userID': row[0], 'display_name': row[1]} for row in results]
    return following


def toggle_like(user_id, post_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the like exists
    cursor.execute("SELECT 1 FROM likes WHERE userID=? AND postID=?", (user_id, post_id))
    exists = cursor.fetchone()

    if exists:
        # If the like exists, remove it
        cursor.execute("DELETE FROM likes WHERE userID=? AND postID=?", (user_id, post_id))
    else:
        # Otherwise, add it
        cursor.execute("INSERT INTO likes (userID, postID) VALUES (?, ?)", (user_id, post_id))

    conn.commit()
    conn.close()

def comment(user_id, post_id, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Add the comment to the comments table
    cursor.execute("INSERT INTO comments (postID, userID, content, comment_time) VALUES (?, ?, ?, datetime('now'))", (post_id, user_id, content))
    conn.commit()
    conn.close()

def get_user_with_following_status(user_id, token):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to fetch users with display names containing the token and not the current user.
    cursor.execute("SELECT userID, display_name FROM userInfo WHERE userID != ? AND display_name LIKE ?",
                    (user_id, '%' + token + '%'))
    users = cursor.fetchall()
    
    # For each user, check if the current user follows them.
    for index, user in enumerate(users):
        cursor.execute("SELECT 1 FROM userRelationship WHERE followerID = ? AND followingID = ?",
                       (user_id, user[0]))
        is_following = cursor.fetchone() is not None  # Will be None if no relationship exists.
        users[index] = {
            'userID': user[0],
            'display_name': user[1],
            'is_following': is_following
        }
    
    conn.close()
    
    return users

def user_insert(username, password, displayname):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert the user information into the userInfo table
    cursor.execute("INSERT INTO userInfo (display_name) VALUES (?)", (displayname,))
    
    # Fetch the last inserted userID
    userID = cursor.lastrowid
    
    # Insert the user into the registration table with the fetched userID
    cursor.execute("INSERT INTO registration (user_account, userID, password_) VALUES (?, ?, ?)", 
                    (username, userID, password))
    
    conn.commit()
    conn.close()

def post_insert(userID, title, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Generate a new postID
    cursor.execute("SELECT MAX(postID) FROM posts")
    max_postID = cursor.fetchone()[0]
    new_postID = max_postID + 1 if max_postID else 1
    
    # Get the current date and time
    current_time = datetime.datetime.now()
    
    # Insert the new post into the posts table along with the current time
    cursor.execute("INSERT INTO posts (postID, userID, title, content, post_time) VALUES (?, ?, ?, ?, ?)", 
                    (new_postID, userID, title, content, current_time))
    
    # Get users who are following the current user
    cursor.execute("SELECT followerID FROM userRelationship WHERE followingID=?", (userID,))
    followers = cursor.fetchall()
    
    # Add the new post to the timelines of the followers and the current user
    for follower in followers:
        cursor.execute("INSERT INTO timeline (userID, postID, post_userID) VALUES (?, ?, ?)", 
                        (follower[0], new_postID, userID))
    
    # Add the new post to the current user's timeline
    cursor.execute("INSERT INTO timeline (userID, postID, post_userID) VALUES (?, ?, ?)", 
                    (userID, new_postID, userID))

    conn.commit()
    conn.close()
    
def get_follow_counts(userID):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Count how many users the given user is following
    cursor.execute("SELECT COUNT(*) FROM userRelationship WHERE followerID=?", (userID,))
    following_count = cursor.fetchone()[0]

    # Count how many users are following the given user
    cursor.execute("SELECT COUNT(*) FROM userRelationship WHERE followingID=?", (userID,))
    followed_count = cursor.fetchone()[0]

    conn.close()
    return following_count, followed_count

def follow_insert(userID, targetUserID):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO userRelationship (followerID, followingID) VALUES (?, ?)", (userID, targetUserID))
    
    # Add all the posts of the target user to the timeline of the user
    cursor.execute("SELECT postID FROM posts WHERE userID=?", (targetUserID,))
    target_user_posts = cursor.fetchall()
    for post in target_user_posts:
        cursor.execute("INSERT INTO timeline (userID, postID, post_userID) VALUES (?, ?, ?)", (userID, post[0], targetUserID))
    conn.commit()
    conn.close()


def follow_delete(userID, targetUserID):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remove the relationship from the userRelationship table
    cursor.execute("DELETE FROM userRelationship WHERE followerID=? AND followingID=?", (userID, targetUserID))
    
    # Remove all the posts of the target user from the timeline of the user
    cursor.execute("DELETE FROM timeline WHERE userID=? AND post_userID=?", (userID, targetUserID))
    
    conn.commit()
    conn.close()

def get_userID(username, password_):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT userID FROM Registration WHERE user_account=? AND password_=?", (username, password_))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def get_personal_info(userID):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT display_name, gender, age, occupation, education, location_ FROM UserInfo WHERE userID = ?", (userID,))
    result = cursor.fetchone()

    if result:
        display_name, gender, age, occupation, education, location_ = result
        personal_info = {
            "DisplayName": display_name,
            "Gender": gender,
            "Age": age,   # Convert age to string as shown in the provided format
            "Occupation": occupation,
            "Education": education,
            "Location": location_
        }
    else:
        personal_info = {}

    conn.close()
    return personal_info

def get_timeline_for_user(userID):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch posts from the timeline for the given userID
    cursor.execute("SELECT postID FROM timeline WHERE userID = ? ORDER BY post_time DESC", (userID,))
    post_ids = [row[0] for row in cursor.fetchall()]

    posts_output = []

    for post_id in post_ids:
        # Fetch post details
        cursor.execute("SELECT title, content FROM posts WHERE postID = ?", (post_id,))
        post = cursor.fetchone()

        # Fetch like count
        cursor.execute("SELECT COUNT(*) FROM likes WHERE postID = ?", (post_id,))
        like_count = cursor.fetchone()[0]

        # Check if the user has liked the post
        cursor.execute("SELECT 1 FROM likes WHERE postID = ? AND userID = ?", (post_id, userID))
        is_liked = bool(cursor.fetchone())

        # Fetch comments
        cursor.execute("SELECT userID, content FROM comments WHERE postID = ?", (post_id,))
        comments_data = cursor.fetchall()
        comments = []

        for comment_data in comments_data:
            comment_userID, comment_content = comment_data
            cursor.execute("SELECT display_name FROM userInfo WHERE userID = ?", (comment_userID,))
            comment_username = cursor.fetchone()[0]
            comments.append({"username": comment_username, "content": comment_content})

        post_output = {
            "postID": post_id,
            "title": post[0],
            "content": post[1],
            "likes": like_count,
            "isLiked": is_liked,  # This can be modified based on the user's action
            "comments": comments
        }

        posts_output.append(post_output)
    return posts_output
