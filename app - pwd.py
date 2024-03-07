from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from function import error, login_required
from flask_session import Session
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import pymysql

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1111"
app.config["MYSQL_DB"] = "diarysys"

mysql = MySQL(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        button = request.form.get("button")
        if button == "login":
            return redirect("/login")
        elif button == "register":
            return redirect("/register")
    else:
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT * FROM user WHERE user_email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user["user_pwd"], password):
            session["user_email"] = email
            return redirect("/mypage")
        else:
            return error("로그인 실패, 아이디 또는 패스워드를 확인하세요.")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/mypage")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 회원 가입 양식에서 입력된 정보 가져오기
        email = request.form["email"]
        password = request.form["password"]
        password_confirm = request.form["password-confirm"]
        question_id = request.form["question"]
        answer = request.form["answer"]
        # agree = request.form.get("agree")

        # 개인정보 처리방침 동의 여부 확인
        # if not agree:
        #     return "개인정보 처리방침에 동의해야 가입할 수 있습니다."

        if question_id == "0":
            return error("질문을 선택해 주세요!")

        # 비밀번호 확인
        if password != password_confirm:
            return "비밀번호가 일치하지 않습니다."
        # 데이터베이스에 회원 정보 저장

        password_hash = generate_password_hash(
            password, method="pbkdf2", salt_length=16
        )

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO user (user_email, user_pwd, user_ans, question_id) VALUES (%s, %s, %s, %s)",
            (email, password_hash, answer, question_id),
        )
        mysql.connection.commit()
        cur.close()
        return redirect("/login")  # 가입 후 로그인 페이지로 리다이렉트
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM question")
        question_list = cur.fetchall()
        cur.close()
        return render_template("register.html", question_list=question_list)


@app.route("/deregister", methods=["GET", "POST"])
@login_required
def deregister():
    if request.method == "POST":
        if request.form.get("button") == "deregister":
            reason = request.form.get("reason")  # 탈퇴 사유를 가져옴

            cur = mysql.connection.cursor()
            # 사용자 정보를 why_secession 테이블에 저장
            cur.execute(
                "INSERT INTO why_secession (user_email, whysecession_cont) VALUES (%s, %s)",
                (session["user_email"], reason),
            )
            # 사용자 정보를 user 테이블에서 삭제
            cur.execute("DELETE FROM user WHERE id = %s", (session["user_email"],))
            mysql.connection.commit()
            cur.close()

            # 로그아웃 후 로그인 페이지로 리디렉션
            session.clear()
            return redirect("/login")
        else:
            return redirect("/mypage")
    else:
        return render_template("deregister.html")


@app.route("/mypage", methods=["GET"])
@login_required
def mypage():
    if session.get("pagenation") is None:
        session["pagenation"] = int(request.args.get("pagenation", 5))

    if request.args.get("pagenation") is not None:
        session["pagenation"] = int(request.args.get("pagenation"))

    pagenation_list = [5, 10, 15, 20]
    # pagenation_list.remove(session["pagenation"])
    pagenation_list.insert(0, session["pagenation"])

    pagenation = session["pagenation"]
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT diary_id, diary_title, diary_cont, diray_date FROM diary WHERE user_email = %s ORDER BY diary_id DESC",
        (session["user_email"],),
    )
    diary_list = cur.fetchall()
    cur.close()

    cur_page = int(request.args.get("page", 1))
    total_page = (len(diary_list) // pagenation) + 1
    pages = [page for page in range(1, total_page + 1) if abs(cur_page - page) <= 3]
    if not total_page == cur_page:
        cur_diary_list = diary_list[
            (cur_page - 1) * pagenation : (cur_page - 1) * pagenation + pagenation
        ]
    else:
        cur_diary_list = diary_list[(cur_page - 1) * pagenation :]

    return render_template(
        "mypage.html",
        cur_diary_list=cur_diary_list,
        cur_page=cur_page,
        pages=pages,
        pagenation_list=pagenation_list,
    )


@app.route("/email-find", methods=["GET", "POST"])
def email_find():
    if request.method == "POST":
        email = request.form.get("email")

        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT user_email FROM user WHERE user_email = %s;", (email,))
        user_email = cur.fetchone()
        cur.close()
    
        if email != user_email["user_email"]:
            return error("입력하신 아이디가 없습니다.")
        
        return render_template("password-find.html", email=email)         
    else:
        return render_template("index.html")


@app.route("/password-find", methods=["GET", "POST"])
def password_find():
    if request.method == "POST":
        answer = request.form.get("answer")

        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT user_ans FROM user WHERE user_ans = %s;", (answer,))
        user_answer = cur.fetchall()
        cur.close()

        if answer != user_answer["user_ans"]:
            return error("답변이 일치하지 않습니다.")
        else:
            return render_template("mypage.html")
    else:
        return render_template("index.html")


@app.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    if request.method == "POST":
        # db에 비밀번호 업데이트 후 재설정
        pwd_check = request.form.get("pwd_check")
        pwd_recheck = request.form.get("pwd_recheck")

        if pwd_check != pwd_recheck:
            error("비밀번호가 일치하지 않습니다.")
        else:
            pwd_new = generate_password_hash(pwd_check, method="pbkdf2", salt_length=16)
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE user SET user_pwd=%s WHERE user_email = %s;",
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
    # 데이터베이스 연결 설정
    connection = pymysql.connect(
        host="127.0.0.1",  # 데이터베이스 서버 주소
        user="root",  # 데이터베이스 접속 사용자명
        password="1111",  # 데이터베이스 접속 비밀번호
        db="diarysys",  # 데이터베이스 이름
        charset="utf8",
    )  # 문자 인코딩 설정

    try:
        # SQL 쿼리 실행을 위한 커서 생성
        with connection.cursor() as cursor:
            # 실행할 쿼리 작성
            sql = "SELECT feeling_date, feeling FROM feeling"
            cursor.execute(sql)

            # 결과를 가져와서 DataFrame 객체로 변환
            result = cursor.fetchall()
            df = pd.DataFrame(result, columns=["date", "feeling"])

            # 'date' 컬럼을 datetime 형식으로 변환
            # 날짜 형식이 'YYYYMMDDHH'인 경우 아래와 같이 format을 지정합니다.
            df["date"] = pd.to_datetime(df["date"], format="%Y%m%d%H")

        # 원본 데이터를 기반으로 보간 함수 생성
        f = interp1d(df["date"].astype(np.int64), df["feeling"], kind="cubic")

        # 더 많은 포인트를 생성하여 부드러운 곡선을 그리기 위한 x값 준비
        xnew = np.linspace(
            df["date"].astype(np.int64).min(), df["date"].astype(np.int64).max(), 1000
        )

        # 보간 함수를 사용하여 y값 생성
        ynew = f(xnew)

        # 그래프 그리기, 마커는 제거
        plt.plot(xnew.astype("datetime64[ns]"), ynew, "-")

        plt.xlabel("date")
        plt.ylabel("feeling")
        plt.title("Feeling", fontsize=16)

        # y축 눈금과 레이블을 사용자 정의 값으로 설정
        plt.yticks(
            [-2, -1, 0, 1, 2], ["very bad", "bad", "normal", "good", "very good"]
        )

        # 0을 기준으로 하는 x 축 표현
        plt.axhline(0, color="black", linewidth=0.8)

        # 그래프 테두리 제거
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        plt.gcf().autofmt_xdate()

        fig, ax = plt.subplots()
        ax.plot(...)  # 그래프 그리기 코드
        plt.tight_layout()
        image_path = "static/images/statistics.png"  # 저장할 경로와 파일명
        plt.savefig(image_path)
        plt.close(fig)

    finally:
        # 데이터베이스 연결 종료
        connection.close()

    return render_template("statistics.html", image_path=image_path)


@app.route("/read-post", methods=["GET"])
@login_required
def read_post():
    current_diary_id = int(request.args.get("diary_id"))

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT diary_id, diary_title, diary_cont, diray_date FROM diary WHERE user_email = %s ORDER BY diary_id;",
        (session["user_email"],),
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

        title = request.form.get("title")
        content = request.form.get("content")

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO diary (diary_title, diary_cont, user_email, diray_date) VALUES (%s, %s, %s, NOW())",
            (title, content, session["user_email"]),
        )
        mysql.connection.commit()
        cur.close()

        return redirect("/mypage")
    else:
        return render_template("write-post.html")


@app.route("/search", methods=["GET"])
@login_required
def search():
    # 글의 정보를 받아서 포스
    term = request.args.get("term")
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT diary_id, diary_title, diary_cont, diray_date FROM diary WHERE diary_title LIKE %s OR diary_cont LIKE %s ORDER BY diary_id",
        ("%" + term + "%", "%" + term + "%"),
    )
    diary_list = cur.fetchall()
    cur.close()

    return render_template(
        "search.html", diary_list=diary_list, term=term, number=len(diary_list)
    )
