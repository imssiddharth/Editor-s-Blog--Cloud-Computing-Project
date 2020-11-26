from flask import Flask, render_template, request, url_for, redirect
from google.cloud import datastore
from google.auth.transport import requests
import google.oauth2.id_token

firebase_request_adapter = requests.Request()
app = Flask(__name__)

datastore_client = datastore.Client()
@app.route('/',methods = ['POST', 'GET'])
def root():
    id_token = request.cookies.get("token")
    if request.method == 'POST':
        result = request.form
        kind = 'article'
        task_key = datastore_client.key(result["kind"],result["name"])
        task = datastore_client.get(task_key)
        task['seen'] = True
        datastore_client.put(task)
    error_message = None
    claims = None
    articles = []
    query = datastore_client.query(kind='article').add_filter('seen', '=', False)
    articles = list(query.fetch())
    print(articles)

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            print(claims)

        except ValueError as exc:
            error_message = str(exc)
    else:
        return redirect(url_for("login"))

    return render_template(
        'index.html',
        user_data=claims, error_message=error_message, id_token=id_token, articles=articles)

@app.route('/login')
def login():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        print("12345")
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

        except ValueError as exc:
            error_message = str(exc)
    print("1234532323")
    return render_template(
        'login.html',
        user_data=claims, error_message=error_message, id_token=id_token)

# @app.route('/participants')
# def participants():
#     # Verify Firebase auth.
#     id_token = request.cookies.get("token")
#     error_message = None
#     claims = None

#     if id_token:
#         try:
#             claims = google.oauth2.id_token.verify_firebase_token(
#                 id_token, firebase_request_adapter)

#         except ValueError as exc:
#             error_message = str(exc)

#     return render_template(
#         'participants.html',
#         user_data=claims, error_message=error_message, id_token=id_token)

@app.route('/pastarticles',methods = ['POST', 'GET'])
def pastarticles():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    if request.method == 'POST':
        result = request.form
        kind = 'article'
        task_key = datastore_client.key(result["kind"],result["name"])
        task = datastore_client.get(task_key)
        task['seen'] = False
        datastore_client.put(task)
    error_message = None
    claims = None
    query = datastore_client.query(kind='article').add_filter('seen', '=', True)
    articles = list(query.fetch())

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

        except ValueError as exc:
            error_message = str(exc)

    return render_template(
        'pastarticles.html',
        user_data=claims, error_message=error_message, id_token=id_token,articles=articles)
@app.route('/postarticles',methods = ['POST', 'GET'])
def postarticles():
    id_token = request.cookies.get("token")
    if request.method == 'POST':
        result = request.form
        kind = 'article'
        name = result["title"].replace(" ","")
        task_key = datastore_client.key(kind, name)
        task = datastore.Entity(key=task_key)
        task['title'] = result["title"]
        task['genre'] = result["genre"]
        task['plot'] = result["plot"]
        task['suggested_by'] = result["suggested_by"]
        task['seen'] = False
        datastore_client.put(task)
    error_message = None
    claims = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

        except ValueError as exc:
            error_message = str(exc)

    return render_template(
        'postarticles.html',
        user_data=claims, error_message=error_message, id_token=id_token)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

