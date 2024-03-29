from flask import Flask, request, url_for, redirect, render_template, abort, make_response
import datetime
import message.utils as utils
import os
import message.database as db
from message.roomclass import Room
from message.userclass import User
from flask_cors import CORS
app = Flask(__name__)
app.config['JWT_SECRET'] = os.urandom(64)
CORS(app, supports_credentials=True)
room = dict()


@app.before_first_request
def db_con():
    db.database_connect()


@app.route("/")
def home():
    return render_template("login_html.html")


@app.route("/signup")
def sign_up_o():
    return render_template("register.html")


@app.route("/login", methods=["GET"])
def login2():
    return render_template("login_html.html")


@app.route("/login", methods=["POST"])
def login():
    json = request.json
    username = json["username"]
    password = json["password"]
    password = utils.pass_to_md5(password)
    user_info = utils.verify_user(username, password)
    if user_info is not None:
        remote_addr = request.remote_addr
        payload = dict({"id": user_info[0], "username": username, "auth": user_info[1], "ip": remote_addr})
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        jwt_code = utils.generate_jwt(payload, expiry)
        resp = make_response("")
        resp.headers["Set-Cookie"] = "token=" + str(jwt_code, encoding='UTF-8') + ";Path=/;HttpOnly;"
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
    if len(username) > 16 or len(nickname) > 16 or len(password) > 64 or len(mailbox) > 64:
        return "Sorry"
    password = utils.pass_to_md5(password)
    if utils.verify_user(username, password) is None:
        utils.add_user(username, nickname, password, mailbox)
        return render_template("index.html")
    else:
        return "USER EXISTS"


@app.route("/create", methods=["GET"])
def create():
    return render_template("create_room.html")


@app.route("/create_room", methods=["POST"])
def create_room():
    token = request.cookies["token"]
    payload = utils.verify_jwt(token)
    if payload is not None and utils.verify_ip(payload["ip"], request.remote_addr):
        if utils.verify_auth(payload["auth"], "USER"):
            json = request.json
            room_name = json["room_name"]
            description = json["description"]
            auth_need = json["auth_need"]
            auth_need = "USER"
            if utils.create_room(room_name, description, payload["id"], auth_need):
                return "Success"  # 重定向到该房间
            else:
                return "Fail"
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@app.route("/join")
def join():
    return render_template("join_room.html")


@app.route("/room/<room_name>", methods=["GET", "POST"])
def join_room(room_name):
    token = request.cookies["token"]
    payload = utils.verify_jwt(token)
    if payload is None:
        return render_template("login_html.html")
    if utils.find_room_and_verify_auth(room_name, payload["username"], payload["auth"]):
        user = User(payload["id"], payload["username"], payload["auth"], room_name)
        if room_name not in room:
            room[room_name] = Room(room_name)
        if user not in room[room_name].list_users():
            room[room_name].add_user(user)
        info_list = utils.list_room_record(room_name)
        return render_template("index.html", room_name=room_name, infos=info_list)
    else:
        abort(404)


@app.route("/send", methods=["POST"])
def send_message():
    token = request.cookies["token"]
    payload = utils.verify_jwt(token)
    if payload is None:
        return render_template("login_html.html")
    json = request.json
    room_name = json["room_name"]
    if room_name not in room:
        return "Cant't find this room."
    if room[room_name].has_user(payload["username"]):
        message = json["message"]
        if message == "":
            return "Message can't be empty"
        if len(message) > 32:
            return "Sorry"
        utils.insert_one_message(message, room_name, payload["username"])
        return redirect("/room/" + room_name)


if __name__ == '__main__':
    app.run()
