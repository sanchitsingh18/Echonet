#importing Libraries
from datetime import datetime
import json 
from flask import Flask,request
from flask import render_template,jsonify,session,redirect

import requests
import users_database as dp
import os
import otpgen
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


#intitialise
app=Flask(__name__)

app.secret_key=os.environ["SECRET_KEY"]
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)
@app.route("/addcomment/<int:post_id>", methods=["POST"])
@limiter.limit("10 per minute")
def add_comment(post_id):
    data = request.get_json()

    user_id = session["user_Id"]
    content = data.get("content")

    dp.add_comment(post_id, user_id, content)

    return jsonify({
        "success": True
    })
@app.route("/like/<int:post_id>",methods=["POST"])
@limiter.limit("10 per minute")
def like_post(post_id):
    print("hit like route")
    user_Id=session["user_Id"]
    result=dp.add_like(user_Id,post_id)
    

    if result == "ALREADY LIKED":
        r=dp.get_like_count(post_id)
        return jsonify({
        "likes":r[0]
    })

    if result == "SUCCESS":
        r=dp.get_like_count(post_id)
        return jsonify({
        "likes":r[0]
    })

    return {"status": "ERROR"}
    
    
    
@app.route("/comments/<int:post_id>")
@limiter.limit("10 per minute")
def comments(post_id):

    comments = dp.fetch_comment(post_id)

    return jsonify({
        "comments": comments
    })
@app.route("/update_bio",methods=["POST"])
@limiter.limit("4 per minute")
def update_bio():
    data=request.get_json()
    username=data.get("username")
    bio=data.get("bio")
    name=data.get("name")
    user_Id=session["user_Id"]
    result=dp.update_bio(user_Id,username,bio,name)
    return jsonify({"status":result})
@app.route("/check_username",methods=["POST"])
def checkusername():
    data=request.get_json()
    username=data.get("username")
    result=dp.username_exists1(username)
    if result=="Username_Exists":
        return jsonify({"status":"USERNAME_EXIST"})
    
    return({"status":result})
    
#render first page

@app.route("/")
def home():

    return render_template(
        "login.html"
    )

#PostContent
@app.route("/PostContent")
@limiter.limit("20 per minute")
def PostContent():
    return render_template("post_creation.html") 
    
#loads Mainscreen    
@app.route("/MainPage")
def MainScreen():
    return render_template("MainPage.html")
    
#Display_Profile_layout    
@app.route("/Profile",methods=["GET"])
@limiter.limit("20 per minute")
def Profile():
        
        if request.method=="GET":
            return render_template("profile.html")
        
@app.route("/verify",methods=["GET"])
@limiter.limit("20 per minute")
def verify_route():
            if request.method=="GET":
                return render_template("verify.html")
                
                
@app.route("/verify-otp", methods=["POST"])
@limiter.limit("10 per minute")
def verify_otp():
    data = request.get_json()
    
    otp_entered = data.get("otp")

    saved_otp = session.get("pending_otp")
    user = session.get("pending_user")
    
    if not saved_otp or not user:
        return jsonify({"status": "SESSION_EXPIRED"})

    if otp_entered == saved_otp:
        # otp verified then save into database
        
        result=dp.signup(user["name"], user["username"], user["password"], user["email"])
        
        session.pop("pending_otp", None)
        session.pop("pending_user", None)
        
        return jsonify({"status": "VERIFIED"})
    else:
        return jsonify({"status": "WRONG_OTP"})
        

          
             
#Fetches_data_for_profile        
@app.route("/get_profile")
@limiter.limit("10 per minute")
def get_profile():
  user_Id=session["user_Id"]
  server_response=dp.get_user(user_Id)
  return jsonify(server_response)

@app.route("/search")
@limiter.limit("30 per minute")
def search():

    query = request.args.get("q","")
    offset = int(request.args.get("offset",0))

    users = dp.find_user(offset, query)

    return jsonify({
    "results": users
})
            
#Login Authentication                                                                                                     
@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login_route():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = dp.login(username, password)
    print(user)
    
    if user[0]==True:

        session["user_Id"] = user[1]
        print("user id is ",user[1])
        return jsonify({
            "status": "Login_Success"
        })

    return jsonify({
        "status": user
    })
@app.route("/terms",methods=["GET"])
def terms():
    if request.method=="GET":
        return render_template("terms.html")    
        
UPLOAD_FOLDER = "static/profile_pic"        
@app.route("/upload_profile_pic", methods=["POST"])
@limiter.limit("2 per minute")
def upload_profile():

    file = request.files.get("profile_pic")

    extension = os.path.splitext(file.filename)[1]

    filename = f"{session['user_Id']}{extension}"   # e.g. 1.jpg

    file.save(os.path.join(UPLOAD_FOLDER, filename))

    result = dp.upload_pic(filename, session["user_Id"])

    if result:
        return "updated"
@app.route("/notification")
@limiter.limit("20 per minute")
def fetch_notification():
    userId = session["user_Id"]

    result = dp.get_notification(userId)

    if result == "NO":
        return jsonify([])

    notifications = []
    
    
    for row in result:
        username=dp.get_user_by_id(row[2])
        notifications.append({
            "id": row[0],
            "TYPEOF": row[1],
            "FROMSENT": username,
            "timestamp": row[3]
        })

    return jsonify(notifications)
@app.route("/accept-follow/<int:notification_id>", methods=["POST"])
def accept_follow(notification_id):

    dp.accept_follow(notification_id)

    return jsonify({
        "success": True
    })
@app.route("/decline-follow/<int:notification_id>", methods=["POST"])
def decline_follow(notification_id):

    dp.decline_follow(notification_id)

    return jsonify({
        "success": True
    })
@app.route("/signup",methods=["GET","POST"])
@limiter.limit("5 per minute")
def signup():

    if request.method=="GET":

        return render_template(
            "signuppage.html"
        )

    data = request.get_json()

    name = data.get("name")
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if dp.username_exists(username):
        return jsonify({
        "status": "USERNAME_EXISTS"
    })

    if dp.email_exists(email):
        return jsonify({
        "status": "EMAIL_EXISTS"
    })
    otp=otpgen.otpgensignup(email)
    
    session["pending_otp"] = str(otp)
    session["pending_user"] = {
        "name": name,
        "username": username,
        "password": password,
        "email": email
    }
    
    return jsonify({"status": "SIGNUP_SUCCESS"})
    
    
#Posting_Content_Route          
@app.route("/Post_Content", methods=["POST"])
@limiter.limit("2 per minute")
def post_content():

    data=request.get_json() #post data fetch

    title=data.get("title")
    content=data.get("content")
    username=data.get("username")
    tag1=data.get("tag1")
    tag2=data.get("tag2")
    tag3=data.get("tag3")
    userid=session["user_Id"]
    username=dp.get_user_by_id(userid)
    

    timestamp=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    status = dp.create_post(username,title, content,tag1,tag2,tag3)
    print(status)
    return jsonify({"status": status})

    

    
@app.route("/otherprof/<username>")
@limiter.limit("10 per minute")
def showprof(username):

    result = dp.otherprof_user(username)

    if result is None:
        return "User not found", 404
    user1 = session.get("user_Id")
    user2 = dp.get_user_id(username)

    follow_status = dp.get_follow_status(user1, user2)
    return render_template(
        "otherprof.html",
        username=username,
        name=result["name"],
        bio=result["bio"],
        followers=result["followers"],
        following=result["following"],
        tea_score=result["tea_score"],
        profile_pic=result["profile_pic"],
        follow_status=follow_status
    )
     
       #Load_Feed_related_Post   
@app.route("/posts")
@limiter.limit("10 per minute")
def get_posts():

    limit = int(request.args.get("limit", 5))
    offset = int(request.args.get("offset", 0))

    posts = dp.get_feed(limit,offset)

    return {
        "posts": posts
    }    
    return jsonify(
        server_response
    )    
@app.route("/follow_profile/<username>", methods=["POST"])
@limiter.limit("10 per minute")
def follow_person(username):
    print("Route reached")

    user_Id1 = session.get("user_Id")
    user_Id2 = dp.get_user_id(username)

    print(user_Id1, user_Id2)

    result = dp.follow_person(user_Id1, user_Id2)

    print(result)

    if result:
        return jsonify({"status": "sent"}) 
@app.route("/editbio")
def editbio():
    return render_template("editbio.html")
@app.route("/logout")
def logout():
    session.clear()

    return render_template(
        "login.html"
    )
if __name__=="__main__":

    app.run(
        debug=True
    )
