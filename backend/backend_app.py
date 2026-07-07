from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

data = {
    'next_id' : 3
}

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

def fetch_all():
    """
    Returns a list of all posts
    :return posts: List of all posts:
    """
    return POSTS

def get_post_by_id(post_id: int) -> dict | None:
    """
    Returns a post, if it exists.
    :param post_id:
    :return post: Dictionary of the post or None:
    """
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None

def set_posts(posts_list: list[dict]):
    """
    Sets a list of posts
    :param posts_list:
    """
    POSTS.clear()
    for post in posts_list:
        POSTS.append(post)

def is_valid_post(post_title: str, post_content: str) -> bool:
    """
    Checks if the post title and the content is valid
    :param post_title: String of the post title
    :param post_content: String of the post content
    :return: Boolean value of the check
    """
    if post_title is not None and post_content is not None:
        correct_title_len = 50 >= len(post_title) > 0
        correct_content_len = 500 > len(post_content) > 0
        return correct_title_len and correct_content_len
    else:
        return False

def get_next_id():
    """
    Returns the next id available
    :return next_id: Integer value of the next id
    """
    return  data["next_id"]


def create_post(post_title: str, post_content: str) -> None:
    """
    Creates a new post
    :param post_title: String of the post title
    :param post_content: String of the post content
    """
    POSTS.append({
        "id": get_next_id(),
         "title": post_title,
         "content": post_content
    })
    data['next_id'] += 1
    return

def update_existing_post(new_post: dict) -> bool:
    """
    Updates an existing post and returns True, otherwise False.
    :param new_post: Entire post containing the id, title and content.
    """
    for post in POSTS:
        if post["id"] == new_post["id"]:
            post["title"] = new_post["title"]
            post["content"] = new_post["content"]
            return True
    return False

def remove_post(post_id: int) -> int | None:
    """
    Deletes a post
    :param post_id: int id of the post
    """
    found_post = get_post_by_id(post_id)
    if found_post:
        POSTS.remove(found_post)
        return post_id
    return None

def get_posts_by_title(search_title) -> list:
    """
    Returns a list of all posts matching the search_title
    :param search_title:
    :return posts: List of all matching posts:
    """
    findings = []
    for post in POSTS:
        if post["title"].upper() == search_title.upper():
            findings.append(post)
    return findings

def get_posts_by_content(search_content) -> list:
    """
    Returns a list of all posts matching the search_content
    :param search_content:
    :return posts: List of all matching posts:
    """
    findings = []
    for post in POSTS:
        if post["content"].upper() == search_content.upper():
            findings.append(post)
    return findings

@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """
    If GET-request: Returns a list of all posts
    If POST request: Creates a new post
    """
    if request.method == 'POST':
        try:
            title = request.json.get("title")
            content = request.json.get("content")
            if is_valid_post(title, content):
                create_post(title, content)
                return f"Post {title} created", 201
            else:
                return "The title and/or content of the post must not be empty!", 400
        except TypeError as e:
            print(e)
            return "Fields must not be empty!", 400

    return jsonify(POSTS)

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Searches for posts matching either a given 'search_title' or 'search_content' parameter.
    :return found_posts: List of all matching posts if any, otherwise empty list:
    """
    search_title = request.args.get('title')
    search_content = request.args.get('content')
    if search_title:
        found_posts = get_posts_by_title(search_title)
    elif search_content:
        found_posts = get_posts_by_content(search_content)
    else:
        return "No search parameters provided", 400

    return jsonify(found_posts), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id: int):
    """
    Updates a post
    :param post_id:
    """
    try:
        new_title = request.json.get("title")
        new_content = request.json.get("content")
        new_post = {"id": post_id,
                    "title": new_title,
                    "content": new_content}
        if is_valid_post(new_title, new_content):
            post_updated = update_existing_post(new_post)
            if post_updated:
                return get_post_by_id(post_id), 200
            return f"Post with id <{post_id}> does not exist.", 404
        return "The title and/or content of the post must not be empty!", 400
    except TypeError as e:
        print(e)
        return "Fields must not be empty!", 400


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id: int):
    """
    Deletes a post
    :param post_id:
    """
    deleted_id = remove_post(post_id)
    if deleted_id:
        return f"Post with id <{post_id}> has been deleted successfully.", 200
    return f"Post with id <{post_id}> does not exist.", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
