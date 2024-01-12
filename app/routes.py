from flask import request
from app import app, db
from fake_data.posts import post_data
from app.models import User, Post, Comment
from app.auth import basic_auth, token_auth

# # We will setup DB later, for now we will store all new users in this list
# users = []

@app.route('/')
def index():
    first_name = 'Brian'
    last_name = 'Stanton'
    return f'Hello World!! - From {first_name} {last_name}'

# USER ENDPOINTS 
@app.route("/token")
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return {"token":token,
            "tokenExpiration":user.token_expiration}


# Create New User
@app.route('/users', methods=['POST'])
def create_user():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    
    # Get the data from the request body
    data = request.json

    # Validate that the data has all of the required fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get the values from the data
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check to see if any current users already have that username and/or email
    check_users = db.session.execute(db.select(User).where( (User.username==username) | (User.email==email) )).scalars().all()
    # If the list is not empty then someone already has that username or email
    if check_users:
        return {'error': 'A user with that username and/or email already exists'}, 400

    # Create a new user instance with the request data which will add it to the database
    new_user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
    return new_user.to_dict(), 201

#update
@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def edit_user(user_id):
    # check if they sent the data correctly
    if not request.is_json:
        return {"error": "your content type must be application/json !"}, 400
    # get user based off id
    user = db.session.get(User, user_id)
    # make sure it exists
    if user is None:
        return {"error": f"User with {user_id} does not exist"},404
    # get their token
    current_user = token_auth.current_user()
    # make sure they are the person logged in
    if user is not current_user:
        return {"error":"You cannot change this user as you are not them!"} ,403
    # then we update!
    data = request.json
    user.update(**data)
    return user.to_dict()


#delete
@app.route("/users/<int:user_id>", methods=["DELETE"])
@token_auth.login_required
def delete_user(user_id):
    # get the user based on the id
    user = db.session.get(User, user_id)
    #get token
    current_user = token_auth.current_user()
    # make sure its a real user
    if user is None:
        return {"error":f"User with {user_id} not found!"},404
    # make sure user to del is current user
    if user is not current_user:
        return {"error":"You cant do that, delete yourself only"}, 403
    # delete the user 
    user.delete()
    return{"success":f"{user.username} has been deleted!"}


#retrieve? 
@app.get("/users/<int:user_id>")
def get_user(user_id):
    #get the user
    user = db.session.get(User, user_id)
    #if no user let them know
    if user:
        return user.to_dict()
    else:
        return {"error":f" user with id:{user_id} not found"}, 404
    


# POST ENDPOINTS

# Get all posts
@app.route('/posts')
def get_posts():
    # Get the posts from the database
    posts = db.session.execute(db.select(Post)).scalars().all()
    # return a list of the dictionary version of each post in posts
    return [p.to_dict() for p in posts]

# Get single post by ID
@app.route('/posts/<int:post_id>')
def get_post(post_id):
    # Get the Post from the database based on the ID
    post = db.session.get(Post, post_id)
    if post:
        return post.to_dict()
    else:
        return {'error': f'Post with an ID of {post_id} does not exist'}, 404

# Create new Post route
@app.route('/posts', methods=['POST'])
@token_auth.login_required
def create_post():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate the incoming data
    required_fields = ['title', 'body']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get data from the body
    title = data.get('title')
    body = data.get('body')

    #get logged in user
    user = token_auth.current_user()

    # Create a new instance of Post which will add to our database
    new_post = Post(title=title, body=body, user_id=user.id)
    return new_post.to_dict(), 201

#update
#edit post
@app.route('/posts/<int:post_id>', methods=["PUT"])
@token_auth.login_required
def edit_post(post_id):
    # check if they sent a good request
    if not request.is_json:
        return {"error":"Your content-type is not application/json"}, 400
    # lets find the post in our db
    post = db.session.get(Post, post_id)
    # if we cant find it, let em know
    if post is None:
        return {"error":f"post with the id of {post_id} does not exist!"}, 404
    # get the token from current user 
    current_user = token_auth.current_user()
    # check and make sure they are the og author or they cant edit
    if post.author is not current_user:
        return {"error":"This is not your post, knock it off ya hacker"}, 403
    # then they can get the green light
    data = request.json
    post.update(**data)
    return post.to_dict()


#delete

@app.route("/posts/<int:post_id>", methods=["DELETE"])
@token_auth.login_required
def delete_post(post_id):
    # get the post
    post = db.session.get(Post,post_id)
    # check if it exists
    if post is None:
        return {"error":f"We cannot locate posts with the id of {post_id}"}, 404
    # get the logged in user token
    current_user = token_auth.current_user()
    # check to make sure the logged in user is post author
    if post.author is not current_user:
        return {"error":"You can do that, this sint your post! Get outta here!"}, 403
    # delete post
    post.delete()
    return {"success":f"{post.title} has been deleted!"}



#COMMENT ROUTES


#make a comment
@app.route("/posts/<int:post_id>/comments", methods=["POST"])
@token_auth.login_required
def create_comment(post_id):
    # check make sure its a valid request
    if not request.is_json:
        return {"error":"Your content-type is not application/json"}, 400
    # get the post they want to comment on
    post = db.session.get(Post, post_id)
    # make sure post exists
    if post is None:
        return {"error":f'post with the id of {post_id} cannot be found! Please try again'}, 404
    # get the data from the user to create the comment
    data = request.json
    # validate data
    required_fields = ["body"]
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields(field)
    if missing_fields:
        return {"error": f" {' '.join(missing_fields)} must be in the request body!"}, 400
    # pull body data
    body = data.get('body')
    # get the logged in users token so we know who commented
    current_user = token_auth.current_user()
    new_comment = Comment(body = body, user_id = current_user.id, post_id = post.id)
    return new_comment.to_dict(), 201



#delete a comment
@app.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@token_auth.login_required
def delete_comment(post_id, comment_id):
    #get the post based on post id
    post = db.session.get(Post,post_id)
    # check if the post exists
    if post is None:
        return {"error" :f"Post with the id {post_id} not found!"}, 404
    # get the comment based off comment id
    comment = db.session.get(Comment, comment_id)
    # check if comment exists
    if comment is None:
        return {"error":f"Comment with the id of {comment_id} does not exist!"},404
    # get the logged in user based on the token
    current_user = token_auth.current_user()
    # check to see if the comment belongs to the logged in user
    if comment.user is not current_user:
        return {"error":"You cannot delete what isn't yours! "}, 403
    # Delete the comment
    comment.delete()
    return {"success":"comment deleted!"}