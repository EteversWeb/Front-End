from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash
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
            username = request.form['user_id']
            password = request.form['user_pwd']
            password_hash = generate_password_hash(password, method="pbkdf2", salt_length=16)

            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM user WHERE user_id=? AND user_pwd=?', (username, password_hash))
            user = cur.fetchone()
            cur.close()

            if user:
                session["user_email"] = username
                return render_template("mypage.html")
            else:
                return render_template("error.html", message='로그인 실패, 아이디 또는 패스워드를 확인하세요.')
        elif request.form.get("회원가입버튼"):
            # 회원가입에 대한 기능
            redirect("/register")
        elif request.form.get("아이디_비밀번호버튼"):
            # 비밀번호 찾기에 대한 기능
            redirect("/password-find")
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
        user_email = request.form["email"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT user_ans FROM user WHERE user_id = ?;", user_email)
        user_ans = cur.fetchall()
        cur.close()

        if user_ans == None:
            error("그런사람없읍니다.")
        if user_ans != request.form["answer"]:
            error("답변이 틀렸습니다.")
        else:
            render_template("password-reset.html")
    else:
        return render_template("password-find.html")


@app.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    if request.method == "POST":
        # db에 비밀번호 업데이트 후 재설정
        pwd_check = request.form["pwd_check"]
        pwd_recheck = request.form["pwd_recheck"]

        if pwd_check != pwd_recheck:
            error("비밀번호가 일치하지 않습니다.")
        else:
            pwd_new = generate_password_hash(pwd_check, method="pbkdf2", salt_length=16)
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE user SET user_pwd=? WHERE user_id = ?;",
                pwd_new,
                session["user_email"],
            )
            mysql.connection.commit()
            cur.close()
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
        current_diary_id = request.form["button"]
    else:
        current_diary_id = request.form["diary_id"]

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT diary_id, diary_title, diary_cont, diray_date FROM diary WHERE user_id = ? ORDER BY diary_id;",
        session["user_email"],
    )
    diary_list = cur.fetchall()
    cur.close()
    diary = {}
    prev_diary_id, next_diary_id = 0, 0

    for diary_id, diary_title, diary_cont, diary_date in diary_list:
        if diary_id < current_diary_id:
            prev_diary_id = diary_id
        elif current_diary_id < diary_id:
            next_diary_id = diary_id
            break
        else:
            diary["title"] = diary_title
            diary["cont"] = diary_cont
            diary["date"] = diary_date

    return render_template(
        "read-post.html",
        prev_diary_id=prev_diary_id,
        next_diary_id=next_diary_id,
        diary=diary,
    )


@app.route("/write-post", methods=["GET", "POST"])
@login_required
def write_post():
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
