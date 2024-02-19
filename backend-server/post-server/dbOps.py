import datetime
from pymongo import MongoClient


def get_mongodb_connection():
    # Placeholder for actual connection creation to your MongoDB instance
    mongodbUri = 'mongodb+srv://dbUser:eAbpyKdugWtswBju@storedb.7vgpy9v.mongodb.net/?retryWrites=true&w=majority'
    return MongoClient(mongodbUri)

def comment(userID, post_id, content):
    # Connect to MongoDB
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    posts_collection = db.posts
    
    # Prepare the comment document to be inserted
    comment = {
        "userID": userID,
        "content": content,
        "comment_time": datetime.datetime.now()
    }
    
    from bson import ObjectId
    if not isinstance(post_id, ObjectId):
        post_id = ObjectId(post_id)

    # Add the comment to the post's comments array
    result = posts_collection.update_one(
        {"_id": post_id},
        {"$push": {"comments": comment}}
    )
    
    # Close the MongoDB connection
    mongo_conn.close()
    
    # Return True if the comment was added, otherwise False
    return result.modified_count > 0

def post_insert(userID, title, content):
    # Connect to MongoDB
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook

    # Insert the new post into the 'posts' collection along with the current time
    posts_collection = db.posts
    users_collection = db.userinfo

    # Insert the new post into the posts collection along with the current time
    post_document = {
        "userID": userID,
        "title": title,
        "content": content,
        "post_time": datetime.datetime.now()
    }
    post_result = posts_collection.insert_one(post_document)
    new_post_id = post_result.inserted_id

    # posts_collection.update_one({"_id": new_post_id}, {"$set": {"postID": str(new_post_id)}})
    
    # Update the timeline of the user and their followers
    # Assuming each user document has a 'timeline' field that stores post IDs
    # First, update the current user's timeline
    users_collection.update_one({"userID": userID}, {"$push": {"timeline": new_post_id}})
    
    # Now, update the timelines of followers
    followers = users_collection.find({"followingID": userID}, {"userID": 1})
    for follower in followers:
        users_collection.update_one({"userID": follower['userID']}, {"$push": {"timeline": new_post_id}})

    # Close the MongoDB connection
    mongo_conn.close()


def toggle_like(userID, post_id):
    # Connect to MongoDB
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    posts_collection = db.posts

    # MongoDB ObjectIds are typically used for document IDs
    # Convert post_id to ObjectId if it's not already one
    from bson import ObjectId
    if not isinstance(post_id, ObjectId):
        post_id = ObjectId(post_id)

    # Check if the like exists and toggle it
    post_document = posts_collection.find_one({"_id": post_id, "likes": userID})

    if post_document:
        # If the like exists, remove it
        result = posts_collection.update_one(
            {"_id": post_id},
            {"$pull": {"likes": userID}}
        )
    else:
        # Otherwise, add it
        result = posts_collection.update_one(
            {"_id": post_id},
            {"$addToSet": {"likes": userID}}
        )

    # Close the MongoDB connection
    mongo_conn.close()

    # Return True if the operation was successful, False otherwise
    return result.modified_count > 0


def get_timeline_for_user(userID):
    # Connect to MongoDB
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    users_collection = db.userinfo
    posts_collection = db.posts

    # Fetch the user's timeline posts
    user_document = users_collection.find_one({"userID": userID}, {"timeline": 1})

    if user_document is None:
        # User not found, return empty list or handle as needed
        return []

    timeline_post_ids = user_document.get('timeline', [])
    posts_output = []

    for post_id in timeline_post_ids:
        # Fetch post details
        post_document = posts_collection.find_one({"_id": post_id}, {"title": 1, "content": 1, "likes": 1, "comments": 1})
        
        if post_document:
            # Prepare comments with user display names
            comments = []
            for comment in post_document.get('comments', []):
                commenter_info = users_collection.find_one({"userID": comment['userID']}, {"display_name": 1})
                comment_username = commenter_info.get('display_name', 'Unknown') if commenter_info else 'Unknown'
                comments.append({"username": comment_username, "content": comment['content']})

            # Check if the user has liked the post (This can be modified based on your Redis structure for likes)
            is_liked = userID in post_document.get('likes', [])

            post_output = {
                "postID": str(post_id),  # Convert ObjectId to string
                "title": post_document['title'],
                "content": post_document['content'],
                "likes": len(post_document.get('likes', [])),
                "isLiked": is_liked,
                "comments": comments
            }

            posts_output.append(post_output)

    # Close the MongoDB connection
    mongo_conn.close()

    return posts_output