import sqlite3
import hashlib
#import otpgen
import math
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

def hash_the_pass(password):
    hashed_password = generate_password_hash(password)
    return hashed_password

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))
# =========================
# INIT DATABASE
# =========================

conn = sqlite3.connect("datausers.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS like(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId TEXT,
    postId TEXT,
    UNIQUE(userId, postId)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS notification(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recvid TEXT,
    TYPEOF TEXT,
    FROMSENT TEXT,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId,
    PostId,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
               
    
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT UNIQUE,
    bio TEXT DEFAULT '',
    followers INTEGER DEFAULT 0,
    following INTEGER DEFAULT 0,
    tea_score INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    interest TEXT,
    score INTEGER DEFAULT 0,
    UNIQUE(username, interest)
)
""")

#followers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS follow_rel(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    BYSENT TEXT,
    TOSENT TEXT,
   status TEXT,
   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)

""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    title TEXT,
    content TEXT,
    tag1 TEXT,
    tag2 TEXT,
    tag3 TEXT,
    likes INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()




# =========================
# ADD LIKE
# =========================

def get_user_by_id(userId):
    conn = sqlite3.connect("datausers.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT username FROM users WHERE id=?",
        (userId,)
    )

    row = cur.fetchone()

    conn.close()

    return row[0] if row else None

def fetch_comment(postId):
    conn=sqlite3.connect("datausers.db")
    cur=conn.cursor()
    cur.execute("""SELECT comment,userId FROM comments WHERE postId=? ORDER BY timestamp DESC""" ,(postId,))
    result=cur.fetchall()
    conn.close()
    comments=[]
    
    for row in result:
        username=get_user_by_id(row[1])
        comments.append({"comment_text":row[0],"username":username})
    
    return comments


def get_like_count(postid):
    conn=sqlite3.connect("datausers.db")
    cur=conn.cursor()
    cur.execute("SELECT likes FROM posts WHERE id=?",(postid,))
    total_likes=cur.fetchone()
    conn.close()
    return total_likes
def add_comment(postid,userid,comment):
  conn=sqlite3.connect("datausers.db")
  cur=conn.cursor()
  cur.execute("""INSERT into comments(postId,userId,comment) values(?,?,?)""",(postid,userid,comment))
  conn.commit()
  conn.close()

    
    
def add_like(userId, postId):
    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    try:
        # Add like record
        cursor.execute("""
            INSERT INTO like (userId, postId)
            VALUES (?, ?)
        """, (userId, postId))

        # Increment like count only once
        cursor.execute("""
            UPDATE posts
            SET likes = likes + 1
            WHERE id = ?
        """, (postId,))

        conn.commit()
        print("LIKE ADDED")
        
        return "SUCCESS"

    except sqlite3.IntegrityError:
        
        cursor.execute("DELETE FROM like WHERE userId=?",(userId,))
        cursor.execute("UPDATE posts SET likes=likes-1 WHERE id=?",(postId,))
        conn.commit()
        print("ALREADY LIKED")
        
        return "ALREADY LIKED"

    except Exception as e:
        print("ERROR:", e)
        return "ERROR"

    finally:
        conn.close()
def get_user_profile_path(user_Id):
    conn=sqlite3.connect("datausers.db")
    cur=conn.cursor()
    cur.execute("""SELECT profile_pic FROM users WHERE id=?""",(user_Id,))
    result=cur.fetchone()
    conn.close()
    return result
# =========================
# SIGNUP
# =========================
def upload_pic(filename,user_id):
    conn = sqlite3.connect("datausers.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET profile_pic=?
        WHERE id=?
    """,(filename,user_id))

    conn.commit()
    conn.close()
    return True

def signup(name, username, password, email):
   
    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    hashed_password=hash_the_pass(password)
    try:

        cursor.execute("""
        INSERT INTO users
        (name, username, password, email)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            username,
            hashed_password,
            email
        ))

        conn.commit()
        conn.close()
        
        return "SIGNUP_SUCCESS"

    except:

        conn.close()
        
        return "USERNAME_OR_EMAIL_ALREADY_EXISTS"


# =========================
# LOGIN
# =========================
    
    

def login(username, password):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, password
        FROM users
        WHERE username = ?
    """, (username,))

    result = cursor.fetchone()

    conn.close()

    if not result:
        return "USER_NOT_FOUND"

    user_id = result[0]
    username = result[1]
    stored_hash = result[2]

    if check_password_hash(stored_hash, password):
        return [True, user_id, username]

    return "Wrong_Password"
# =========================
# UPDATE BIO
# =========================

def update_bio(user_Id,username, new_bio,name):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET bio=?,
    username=?,
    name=?
    WHERE id=?
    """,
    (new_bio, username,name,user_Id,))

    conn.commit()
    conn.close()

    return "BIO_UPDATED"


# =========================
# USER INTERESTS
# =========================

def update_interest(username, interest):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id FROM user_interests
    WHERE username=? AND interest=?
    """,
    (username, interest))

    result = cursor.fetchone()

    if result:

        cursor.execute("""
        UPDATE user_interests
        SET score = score + 1
        WHERE username=? AND interest=?
        """,
        (username, interest))

    else:

        cursor.execute("""
        INSERT INTO user_interests
        (username, interest, score)
        VALUES (?, ?, ?)
        """,
        (username, interest, 1))

    conn.commit()
    conn.close()

    return "INTEREST_UPDATED"


# =========================
# GET USER INTERESTS
# =========================

def get_interests(username):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT interest, score
    FROM user_interests
    WHERE username=?
    ORDER BY score DESC
    """,
    (username,))

    data = cursor.fetchall()

    conn.close()

    return data


# =========================
# CREATE POST
# =========================

def create_post(
    username,
    title,
    content,
    tag1='',
    tag2='',
    tag3=''):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO posts
    (username, title, content, tag1, tag2, tag3)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        username,
        title,
        content,
        tag1,
        tag2,
        tag3
    ))
    cursor.execute("""UPDATE users SET tea_score=tea_score+1 WHERE username=?""",(username,) )
    conn.commit()
    conn.close()

    return "POST_CREATED"


# =========================
# GET FEED
# =========================

def get_feed(limit, offset):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
    username,
    title,
    content,
    likes,
    timestamp,
    tag1,
    tag2,
    tag3,id
    FROM posts
    ORDER BY timestamp ASC
    LIMIT ? OFFSET ?
    """,
    (limit, offset))

    rows = cursor.fetchall()

    conn.close()

    posts = []

    for row in rows:

        posts.append({
            "username": row[0],
            "title": row[1],
            "content": row[2],
            "likes": row[3],
            "timestamp": row[4],
            "tag1": row[5],
            "tag2": row[6],
            "tag3": row[7],
            "id":row[8]
        })
    
    return posts


# =========================
# GET USER
# =========================

def otherprof_user(username):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
    name,
    bio,
    followers,
    following,
    tea_score,
    profile_pic
    FROM users
    WHERE username=?
    """,(username,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None
   
    return {
        "name": row[0],
        
        "bio": row[1],
        "followers": row[2],
        "following": row[3],
        "tea_score": row[4],
        "profile_pic":row[5]
        
    }



def get_user(user_Id):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
    name,
    username,
    email,
    bio,
    followers,
    following,
    tea_score,id,profile_pic
    FROM users
    WHERE id=?
    """,(user_Id,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "name": row[0],
        "username": row[1],
        "email": row[2],
        "bio": row[3],
        "followers": row[4],
        "following": row[5],
        "tea_score": row[6],
        "userid":row[7],
        "profile_pic":row[8]
    }

def username_exists(username):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None
    

def email_exists(email):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM users WHERE email = ?",
        (email,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None
    
    
def update_location(user_id, country, city, lat, lon):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users SET country=?, city=?, lat=?, lon=?
    WHERE id=?
    """, (country, city, lat, lon, user_id))
    conn.commit()
    conn.close()


def get_location(user_id):
    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT country, city, lat, lon 
        FROM users 
        WHERE username=?
    """, (user_id,))
    user = cursor.fetchone()
    conn.close()
    return(user)  
    
    
def search_users(query, searcher_username):
    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    # get searcher location
    cursor.execute("SELECT lat, lon FROM users WHERE username=?", (searcher_username,))
    searcher = cursor.fetchone()

    # find matching users
    cursor.execute("""
        SELECT username, name, city, country, lat, lon
        FROM users
        WHERE name LIKE ? OR username LIKE ?
    """, (f"{query}%", f"{query}%"))

    rows = cursor.fetchall()
    conn.close()

    users = []
    for row in rows:
        username, name, city, country, lat, lon = row

        if searcher and lat and lon:
            distance = haversine(searcher[0], searcher[1], lat, lon)
        else:
            distance = 99999

        users.append({
            "username": username,
            "name": name,
            "city": city,
            "country": country,
            "distance": distance
        })

    # sort nearest first
    users.sort(key=lambda x: x["distance"])

    
    for u in users:
        del u["distance"]

    return users
 
def find_user(offset,query):
    conn=sqlite3.connect("datausers.db")
    cur=conn.cursor()
    cur.execute("""SELECT username,id,name FROM users WHERE name LIKE ? OR username LIKE ? LIMIT 8 OFFSET ? """, (    f"%{query}%",f"%{query}%",offset))
    results = cur.fetchall()

    conn.close()
    users = []

    for row in results:
        users.append({
        "username": row[0],
        "id": row[1],
        "name": row[2]
        
    })

    return users


def get_user_id(username):
    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()

    if user:
        return user[0]
    return None


def username_exists1(username):

    conn = sqlite3.connect("datausers.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    return ("Username_Exists")
def follow_person(p1,p2):
    try:
        conn=sqlite3.connect("datausers.db")
        cur=conn.cursor()
        cur.execute("""INSERT INTO follow_rel(BYSENT,TOSENT,status) VALUES(?,?,?)""",(p1,p2,"pending",))
        cur.execute("""INSERT INTO notification(recvid,TYPEOF,FROMSENT,status) values(?,?,?,?)""",(p2,"follow",p1,"pending"))
        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(e)
        return ("failed")   
        
def get_follow_status(user1, user2):
    conn = sqlite3.connect("datausers.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT status
        FROM follow_rel
        WHERE BYSENT=? AND TOSENT=?
    """, (user1, user2))
    cur.execute("""INSERT INTO notification (recvid,TYPEOF,FROMSENT,status) VALUES(?,?,?,?)""",(user1,user2,"follow","unseen"))
    row = cur.fetchone()
    conn.close()

    if row:
        return row[0]      # "pending" or "accepted"

    return "follow"        
def get_notification(userId):
    conn=sqlite3.connect("datausers.db")
    cur=conn.cursor()
    cur.execute("""SELECT id,TYPEOF,FROMSENT,timestamp FROM notification WHERE recvid=? AND status !='seen'""",(userId,))
    data=cur.fetchall()
    conn.close()
    if data:
        return(data)
    else:
        return("NO")

def accept_follow(notification_id):

    conn = sqlite3.connect("datausers.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT FROMSENT, recvid
        FROM notification
        WHERE id=?
    """, (notification_id,))

    row = cur.fetchone()

    if not row:
        conn.close()
        return False
    from_user = row[0]
    to_user = row[1]

    cur.execute("""
        UPDATE follow_rel
        SET status='accepted'
        WHERE BYSENT=? AND TOSENT=?
    """, (from_user, to_user))
    cur.execute("""UPDATE users SET followers=followers+1 WHERE id=?""",(to_user))
    cur.execute("""UPDATE users SET following=following+1 WHERE id=?""",(from_user))
    cur.execute("""
        UPDATE notification
        SET status='accepted'
        WHERE id=?
    """, (notification_id,))

    
    
    conn.commit()
    conn.close()

    return True
def decline_follow(notification_id):

    conn = sqlite3.connect("datausers.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT FROMSENT, recvid
        FROM notification
        WHERE id=?
    """, (notification_id,))

    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    from_user = row[0]
    to_user = row[1]
    cur.execute("""
        DELETE FROM follow_rel
        WHERE BYSENT=? AND TOSENT=?
    """, (from_user, to_user))

    cur.execute("""
        DELETE FROM notification
        WHERE id=?
    """, (notification_id,))

    
    conn.commit()
    conn.close()

    return True


