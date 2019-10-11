from flask import Flask, request, url_for, render_template, abort, make_response
import message.database
import datetime
import message.utils as utils
import os
import message.database as db
import hashlib
import sqlite3
app = Flask(__name__)
app.config['JWT_SECRET'] = os.urandom(24)


@app.before_first_request
def db_con():
    db.database_connect()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    json = request.json
    username = json["username"]
    password = json["password"]
    password = utils.pass_to_md5(password)
    user_id = utils.verify_user(username, password)
    if user_id is not None:
        payload = dict({"id": user_id, "username:": username})
        expiry = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        jwt_code = utils.generate_jwt(payload, expiry)
        resp = make_response("")
        resp.headers["Set-Cookie"] = "token=" + str(jwt_code)
        return resp
    else:
        abort(401)


@app.route("/sign", methods=["POST"])
def sign():
    json = request.json
    username = json["username"]
    nickname = json["nickname"]
    password = json["password"]
    mailbox = json["mailbox"]
    password = utils.pass_to_md5(password)
    if utils.verify_user(username, password) is None:
        utils.add_user(username, nickname, password, mailbox)
        return "Success"  # 后期换成成功页面
    else:
        return "USER EXISTS"  # 同上





@app.route("/create_room")
def create_room():
    r = request.json["s"]


if __name__ == '__main__':
    app.run(debug=True)
