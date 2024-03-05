from flask import Flask, render_template, request, session, redirect
from function import error, login_required
from flask_session import Session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1111"
app.config["MYSQL_DB"] = "new"

mysql = MySQL(app)

# @app.route('/')
# def index():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM example_table")
#     data = cur.fetchall()
#     cur.close()
#     return render_template('index.html', data=data)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        button = request.form["button"]
        if button == "login":
            redirect("/login")
        elif button == "register":
            redirect("register")
        else:
            error("idk")
    else:
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if request.form.get("button"):
            # 로그인에 대한 기능
            pass
        if request.form.get("회원가입버튼"):
            # 회원가입에 대한 기능
            pass
        if request.form.get("아이디_비밀번호버튼"):
            # 비밀번호 찾기에 대한 기능
            pass
        return redirect("/mypage")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # db에 업데이트 하는 로직
        # 아이디 중복여부
        # 비밀번호 두개가 일치하는지 여부
        # 전부 확인되면 db에 입력
        pass
    else:
        return render_template("register.html")


@app.route("/deregister", methods=["GET", "POST"])
@login_required
def deregister():
    if request.method == "POST":
        # db에 탈퇴사유 업데이트 하는 로직

        return redirect("/")
    else:
        return render_template("deregister.html")


@app.route("/mypage", methods=["GET", "POST"])
@login_required
def mypage():
    if request.method == "POST":
        if request.form.get("일기작성"):

            pass
    else:
        딕셔너리 = {}
        # db에서 받은 글을 딕셔너리 형태로 저장해서? 올리는 로직
        return render_template("mypage.html", 딕셔너리=딕셔너리)


@app.route("/password-find", methods=["GET", "POST"])
def password_find():
    if request.method == "POST":
        # 폼에서 받는 정보와 db에 있는 정보가 일치하는지 확인 후
        return render_template("password-reset.html")
    else:
        return render_template("password-find.html")


@app.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    if request.method == "POST":
        # db에 비밀번호 업데이트 후 재설정

        return redirect("/")
    else:
        return render_template("password-reset.html")


@app.route("/statistics")
@login_required
def statistics():
    # db에서 데이터를 딕셔너리로 입수
    딕셔너리 = {}
    return render_template("statistics.html", 딕셔너리=딕셔너리)


@app.route("/read-post", methods=["GET", "POST"])
@login_required
def read_post():
    if request.method == "POST":

        cur = mysql.connection.cursor()
        cur.execute("SELECT diary_id, diary_title, diary_cont, diray_date")
        data = cur.fetchall()
        cur.close()

        return render_template(
            "read-post.html", 딕셔너리1=딕셔너리1, 딕셔너리2=딕셔너리2
        )
    else:
        diary_id = request.form["diary_id"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT diary_id ")
        data = cur.fetchall()
        cur.close()
        return render_template(
            "read-post.html", is_there_prev=is_there_prev, is_there_next=is_there_next
        )

@app.route("/write-post", methods=["GET", "POST"])
@login_required
def read_post():
    # 글의 정보를 받아서 포스
    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO 'diary' (diary_title, diary_cont, user_id, diray_date) VALUES (?, ?, ?, NOW())",
            title,
            content,
            session["user_email"],
        )
        mysql.connection.commit()
        cur.close()

        return redirect("/mypage")
    else:
        return render_template("write-post.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def read_post():
    # 글의 정보를 글의 id 기반으로 딕셔너리 형태로 두개를 받아온다.
    딕셔너리리스트 = [{}]
    키워드 = ""
    리스트길이 = len(딕셔너리리스트)
    if request.method == "POST":
        # 클릭한 글의 아이디를 받아와서
        return render_template(
            "read-post.html", 딕셔너리1=딕셔너리1, 딕셔너리2=딕셔너리2
        )
    else:
        return render_template(
            "search.html",
            딕셔너리리스트=딕셔너리리스트,
            키워드=키워드,
            리스트길이=리스트길이,
        )
