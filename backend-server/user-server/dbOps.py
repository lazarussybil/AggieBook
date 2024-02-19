import datetime
import redis
from pymongo import MongoClient
import hashlib

def get_redis_connection():
    redis_host = "redis-10214.c11.us-east-1-3.ec2.cloud.redislabs.com"
    redis_port = 10214
    redis_password = "fLgoTDsKqVyfQbzXwqA7nvO2wvGGAx4S"
    # r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)
    # r.set('name', 'python_test'); 
    # print(r.get('name'))
    return redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)


# def get_mongodb_database():
def get_mongodb_connection():
    # Placeholder for actual connection creation to your MongoDB instance
    mongodbUri = 'mongodb+srv://dbUser:eAbpyKdugWtswBju@storedb.7vgpy9v.mongodb.net/?retryWrites=true&w=majority'
    # client = MongoClient(mongodbUri)
    return MongoClient(mongodbUri)


def get_followers(user_id):
    # Connect to Redis
    redis_conn = get_redis_connection()

    # Fetch all follower relationships for the given user
    follower_keys = redis_conn.keys(f"following:*:{user_id}")
    follower_ids = [key.decode('utf-8').split(':')[1] for key in follower_keys]
    # print(f"follower_ids {follower_ids}")

    # Connect to MongoDB
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    users_collection = db.userinfo

    # Fetch details of follower users from MongoDB
    followers_users = list(users_collection.find({"userID": {"$in": follower_ids}}, {"_id": 0, "userID": 1, "display_name": 1}))
    # print(f"followers_users {followers_users}")

    # Close the connections
    redis_conn.close()
    mongo_conn.close()

    # Convert the results to a list of dictionaries
    followers = [{'userID': user['userID'], 'display_name': user.get('display_name', '')} for user in followers_users]
    return followers


def get_following(user_id):
    # Connect to Redis
    redis_conn = get_redis_connection()

    # Fetch all following relationships for the given user
    following_keys = redis_conn.keys(f"following:{user_id}:*")
    following_ids = [key.decode('utf-8').split(':')[2] for key in following_keys]
    # print(f"following_ids {following_ids}")

    # Connect to MongoDB
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    users_collection = db.userinfo

    # Fetch details of following users from MongoDB
    following_users = list(users_collection.find({"userID": {"$in": following_ids}}, {"_id": 0, "userID": 1, "display_name": 1}))
    # print(f"following_users {following_users}")
    # Close the connections
    redis_conn.close()
    mongo_conn.close()

    # Convert the results to a list of dictionaries
    following = [{'userID': user['userID'], 'display_name': user.get('display_name', '')} for user in following_users]
    return following


def get_user_with_following_status(userID, token):
    # Connect to Redis
    redis_conn = get_redis_connection()
    
    # Connect to MongoDB to get user information
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    users_collection = db.userinfo
    
    print(f"user ID", userID)
    from bson import ObjectId
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)

    # Query to fetch users with display names containing the token and not the current user
    users_cursor = users_collection.find(
        {"_id": {"$ne": userID}, "display_name": {"$regex": token, "$options": "i"}},
        {"_id": 1, "display_name": 1}
    )
    users = list(users_cursor)
    
    # For each user, check if the current user follows them in Redis
    for user in users:
        # Assuming the Redis key for following is stored as "following:{userID}:{other_user_id}"
        following_key = f"following:{userID}:{user['_id']}"
        is_following = redis_conn.exists(following_key)
        user['is_following'] = bool(is_following)
        user['_id'] = str(user["_id"])
    
    # Close the Redis and MongoDB connections
    redis_conn.close()
    mongo_conn.close()
    
    return users

def user_insert(username, password, displayname):
    # Connect to Redis
    redis_conn = get_redis_connection()
    
    # Connect to MongoDB

    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    users_collection = db.userinfo

    # Insert the user information into MongoDB's userInfo collection
    user_document = {
        "display_name": displayname,
        # Add other relevant user fields as needed
    }
    user_result = users_collection.insert_one(user_document)
    user_id = user_result.inserted_id

    # Update the document with the userID (same as _id here)
    users_collection.update_one({"_id": user_id}, {"$set": {"userID": str(user_id)}})
    
    # Hash the password before storing it
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    # Insert the user account information into Redis with the fetched userID
    # The key will be the username, and the value will be a hash of the userID and password
    redis_conn.hset(f"user:{username}", mapping={
        "userID": str(user_id),
        "password": hashed_password
    })

    # Close the Redis and MongoDB connections
    redis_conn.close()
    mongo_conn.close()



def get_follow_counts(userID):
    # Connect to Redis
    redis_conn = get_redis_connection()
    
    # Count how many users the given user is following
    following_keys = redis_conn.keys(f"following:{userID}:*")
    following_count = len(following_keys)

    # Count how many users are following the given user
    followers_keys = redis_conn.keys(f"following:*:{userID}")
    followers_count = len(followers_keys)

    # Close the Redis connection
    redis_conn.close()

    return following_count, followers_count


def follow_insert(userID, target_user_id):
    # Connect to Redis
    redis_conn = get_redis_connection()
    
    # Add the following relationship in Redis
    # Assuming the key format for following is "following:{userID}:{target_user_id}"
    following_key = f"following:{userID}:{target_user_id}"
    redis_conn.set(following_key, 1)

    # # Add the follower count for target user and following count for user
    # redis_conn.incr(f"followers_count:{target_user_id}")
    # redis_conn.incr(f"following_count:{userID}")

    # Connect to MongoDB
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    posts_collection = db.posts

    # Add all the posts of the target user to the timeline of the user
    # Assuming each user has a 'timeline' field in their document in a 'users' collection
    target_user_posts = posts_collection.find({"userID": target_user_id}, {"_id": 1})
    db.userinfo.update_one(
        {"userID": userID},
        {"$addToSet": {"timeline": {"$each": [post['_id'] for post in target_user_posts]}}}
    )

    # Close the Redis and MongoDB connections
    redis_conn.close()
    mongo_conn.close()



def follow_delete(userID, target_user_id):
    # Connect to Redis
    redis_conn = get_redis_connection()
    
    # Remove the following relationship in Redis
    following_key = f"following:{userID}:{target_user_id}"
    redis_conn.delete(following_key)

    # # Decrease the follower count for target user and following count for user
    # redis_conn.decr(f"followers_count:{target_user_id}")
    # redis_conn.decr(f"following_count:{userID}")

    # Connect to MongoDB
    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    posts_collection = db.posts

    # Remove all the posts of the target user from the timeline of the user
    target_user_posts = posts_collection.find({"userID": target_user_id}, {"_id": 1})
    db.userinfo.update_one(
        {"userID": userID},
        {"$pull": {"timeline": {"$in": [post['_id'] for post in target_user_posts]}}}
    )

    # Close the Redis and MongoDB connections
    redis_conn.close()
    mongo_conn.close()


def get_userID(username, password_):
    # Connect to Redis
    redis_conn = get_redis_connection()
    # Hash the password to compare with the stored hash
    hashed_password = hashlib.sha256(password_.encode('utf-8')).hexdigest()

    # Retrieve the user information
    user_info = redis_conn.hgetall(f"user:{username}")

    # Close the Redis connection
    redis_conn.close()

    # Check if user exists and password matches
    if user_info and user_info.get(b'password') == hashed_password.encode('utf-8'):
        return user_info.get(b'userID').decode('utf-8')
    else:
        return None
    

def get_personal_info(userID):
    # Connect to MongoDB

    mongo_conn = get_mongodb_connection()
    db = mongo_conn.AggieBook
    users_collection = db.userinfo

    from bson import ObjectId
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)

    # Query the UserInfo collection for the user's personal information
    user_document = users_collection.find_one({"_id": userID}, { "display_name": 1, "gender": 1, "age": 1, "occupation": 1, "education": 1, "location_": 1})

    # Close the MongoDB connection
    mongo_conn.close()

    # Format the result into a dictionary
    if user_document:
        personal_info = {
            "DisplayName": user_document.get("display_name", ""),
            "Gender": user_document.get("gender", ""),
            "Age": str(user_document.get("age", "")),  # Convert age to string
            "Occupation": user_document.get("occupation", ""),
            "Education": user_document.get("education", ""),
            "Location": user_document.get("location_", "")
        }
    else:
        personal_info = {}

    return personal_info


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

if __name__ == "__main__":
    # get_redis_connection()
    # get_mongodb_connection()
    userID = get_userID("john.doe@example.com", "passwordForJohn")
    print(userID)