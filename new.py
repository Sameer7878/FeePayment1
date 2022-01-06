from flask import Flask, url_for, render_template, request, redirect, session, abort
import sqlite3 as sql
import os
from datetime import date
from werkzeug.utils import secure_filename
from flask_login import login_required

app = Flask(__name__)
from .auth import auth as auth_blueprint
app.debug = True
app.register_blueprint(auth_blueprint)
app.secret_key = '27009e15fbad776cfb3cf6fe174790e42574c8af5be4eb884f76acc874b4c0a9'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = '/static/uploadeddata'
UPLOAD_FOLDER = APP_ROOT + UPLOAD_FOLD
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(404)
def handle_404(e):
    return redirect('/')


@app.errorhandler(500)
def handle_500(e):
    session.pop('name')
    return redirect('/')


@app.route('/signout/')
def signout():
    session.pop('name')
    return redirect('/')


@app.route('/')
def hello_world():
    if not session.get('name'):
        return redirect('login')
    return redirect(url_for('index'))


@app.route('/forgot/')
def forgot():
    return 'sameer'


@app.route('/loginverify', methods=['POST', 'GET'])
def verify():
    if request.method == "POST":
        username = request.form['username']
        username = username.upper()
        username=username+'@NBKRIST.ORG'
        password = request.form['password']
        try:
            con = sql.connect('logins', check_same_thread=False)
            cur = con.cursor()
            cur.execute('SELECT * FROM LOGIN WHERE USERNAME=? AND PASSWORD=?', (username, password))
            login_data = cur.fetchone()
            con.close()

            if login_data is None:
                msg = 'Invalid login details'
                return render_template('login.html', msg=msg)
            elif login_data[1] == 'ADMIN@NBKRIST.ORG' and login_data[2] == 'admin123':
                session['name'] = login_data[1]
                return redirect('/admin')
            else:
                verify.roll_no = login_data[0]
                session['name'] = username
                if login_data[2] == '':
                    return render_template('register.html')


                con = sql.connect('logins', check_same_thread=False)
                cur = con.cursor()
                cur.execute('SELECT LOGIN.ROLLNO,STUDENT_INFO.NAME,STUDENT_INFO.ACADEMIC,'
                            'STUDENT_INFO.CLASS,STUDENT_INFO.SECTION,STUDENT_INFO.GENDER '
                            'FROM LOGIN INNER JOIN STUDENT_INFO ON LOGIN.ROLLNO = STUDENT_INFO.ROLLNO WHERE '
                            'LOGIN.ROLLNO= ?',
                            (verify.roll_no,))
                basic_data = cur.fetchone()
                verify.name = basic_data[1]
                verify.academic = basic_data[2]
                verify.class1 = basic_data[3]
                verify.section = basic_data[4]
                verify.gender = basic_data[5]
                con.close()
                msg = 'Login Successfully'
                return redirect('/')

        except:
            return abort(401)
    return abort(404)


@app.route('/login/')
def login():
    return render_template('login.html')


@app.route('/index/')
def index():
    if not session.get('name'):
        return redirect('login')
    return render_template('PayFee.html', name=verify.name)

@app.route('/register',methods=["POST","GET"])
def register():
    if not session.get('name'):
        return redirect('login')
    if request.method == 'POST':
        name=request.form['name']
        password=request.form['password']
        gender=request.form['gender']
        profile_link=f'images/{verify.roll_no}.jpg'
        filesz = request.files['file'].read()
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename=file.filename
            filename=filename.split('.')

            filename = secure_filename(verify.roll_no+ filename[1])
            UPLOAD_FOLD = '/static/images'
            UPLOAD_FOLDER = APP_ROOT + UPLOAD_FOLD
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                con = sql.connect('logins')
                cur = con.cursor()
                cur.execute("INSERT INTO STUDENT_INFO(rollno, name, academic, class, section, gender, profile_link) VALUES(?,?,?,?,?,?,?)",(verify.roll_no,name,3,'INFORMATION TECHNOLOGY',"A",gender,profile_link))
                cur.execute("UPDATE LOGIN SET PASSWORD=? where ROLLNO=?",(password,verify.roll_no))
                con.commit()
                con.close()
                return redirect('/login')
            except:
                return 'DATABASE ERROR'



@app.route('/college_fee', methods=['GET', 'POST'])
def college_fee():
    roll_no1 = verify.roll_no
    if not session.get('name'):
        return redirect('login')
    con = sql.connect('logins', check_same_thread=False)
    cur = con.cursor()
    cur.execute('SELECT LOGIN.ROLLNO,STUDENT_INFO.NAME,STUDENT_INFO.ACADEMIC,STUDENT_INFO.CLASS,'
                'STUDENT_INFO.SECTION,STUDENT_INFO.GENDER,STUDENT_INFO.profile_link,'
                ' COLLEGE_FEE.TOTAL_AMOUNT,COLLEGE_FEE.PAID_AMOUNT,'
                'COLLEGE_FEE.DUE_AMOUNT FROM LOGIN INNER JOIN STUDENT_INFO ON LOGIN.ROLLNO = STUDENT_INFO.ROLLNO '
                'INNER JOIN COLLEGE_FEE ON LOGIN.ROLLNO = COLLEGE_FEE.ROLLNO WHERE LOGIN.ROLLNO= ?', (roll_no1,))

    data = cur.fetchone()
    cur.execute("SELECT STATUS.STATUS,COLLEGE_FEE.DUE_AMOUNT FROM COLLEGE_FEE INNER JOIN STATUS ON STATUS.ROLLNO=COLLEGE_FEE.ROLLNO AND STATUS.CATEGORY='college_fee'")
    fee_details=cur.fetchall()
    con.close()
    if fee_details==[]:
        status1=''
        damount=''
    else:
        status1=fee_details[0][0]
        damount=fee_details[0][1]

    name = data[1]
    rollno = data[0]
    class1 = data[3]
    year = str(data[2])
    gender = data[5]
    section = data[4]
    profile_link = '../static/' + data[6]
    tamount = data[7]
    pamount = data[8]
    college_fee.ramount = tamount - pamount
    return render_template('clgfee.html', name=name, rollno=rollno, class1=class1, year=year, gender=gender,
                           section=section, tamount=tamount, pamount=pamount, ramount=college_fee.ramount,
                           profile_link=profile_link,status1=status1,damount=damount)


@app.route('/bus_fee', methods=['GET', 'POST'])
def bus_fee():
    roll_no1 = verify.roll_no
    if not session.get('name'):
        return redirect('login')
    con = sql.connect('logins', check_same_thread=False)
    cur = con.cursor()
    cur.execute('SELECT LOGIN.ROLLNO,STUDENT_INFO.NAME,STUDENT_INFO.ACADEMIC,STUDENT_INFO.CLASS,'
                'STUDENT_INFO.SECTION,STUDENT_INFO.GENDER,STUDENT_INFO.profile_link,'
                'BUS_FEE.TOTAL_AMOUNT,BUS_FEE.PAID_AMOUNT,'
                'BUS_FEE.DUE_AMOUNT FROM LOGIN INNER JOIN STUDENT_INFO ON LOGIN.ROLLNO = STUDENT_INFO.ROLLNO '
                'INNER JOIN BUS_FEE ON LOGIN.ROLLNO = BUS_FEE.ROLLNO WHERE LOGIN.ROLLNO= ?', (roll_no1,))
    data = cur.fetchone()
    cur.execute(
        "SELECT STATUS.STATUS,COLLEGE_FEE.DUE_AMOUNT FROM COLLEGE_FEE INNER JOIN STATUS ON STATUS.ROLLNO=COLLEGE_FEE.ROLLNO AND STATUS.CATEGORY='college_fee'")
    fee_details = cur.fetchall()
    con.close()
    if fee_details==[]:
        status1=''
        damount=''
    else:
        status1=fee_details[0][0]
        damount=fee_details[0][1]
    name = data[1]
    rollno = data[0]
    class1 = data[3]
    year = str(data[2])
    gender = data[5]
    section = data[4]
    profile_link = '../static/' + data[6]
    tamount = data[7]
    pamount = data[8]
    bus_fee.ramount = tamount - pamount
    return render_template('busfee.html', name=name, rollno=rollno, class1=class1, year=year, gender=gender,
                           section=section, tamount=tamount, pamount=pamount, ramount=bus_fee.ramount,
                           profile_link=profile_link,status1=status1,damount=damount)


@app.route('/exam_fee', methods=['GET', 'POST', 'PUT'])
def exam_fee():
    roll_no1 = verify.roll_no
    if not session.get('name'):
        return redirect('login')
    con = sql.connect('logins', check_same_thread=False)
    cur = con.cursor()
    cur.execute('SELECT LOGIN.ROLLNO,STUDENT_INFO.NAME,STUDENT_INFO.ACADEMIC,STUDENT_INFO.CLASS,'
                'STUDENT_INFO.SECTION,STUDENT_INFO.GENDER,STUDENT_INFO.profile_link,'
                ' EXAM_FEE.TOTAL_AMOUNT,EXAM_FEE.PAID_AMOUNT,'
                'EXAM_FEE.DUE_AMOUNT FROM LOGIN INNER JOIN STUDENT_INFO ON LOGIN.ROLLNO = STUDENT_INFO.ROLLNO '
                'INNER JOIN EXAM_FEE ON LOGIN.ROLLNO = EXAM_FEE.ROLLNO WHERE LOGIN.ROLLNO= ?', (roll_no1,))
    data = cur.fetchone()
    cur.execute(
        "SELECT STATUS.STATUS,COLLEGE_FEE.DUE_AMOUNT FROM COLLEGE_FEE INNER JOIN STATUS ON STATUS.ROLLNO=COLLEGE_FEE.ROLLNO AND STATUS.CATEGORY='college_fee'")
    fee_details = cur.fetchall()
    con.close()
    if fee_details==[]:
        status1=''
        damount=''
    else:
        status1=fee_details[0][0]
        damount=fee_details[0][1]
    name = data[1]
    rollno = data[0]
    class1 = data[3]
    year = str(data[2])
    gender = data[5]
    section = data[4]
    profile_link = '../static/' + data[6]
    tamount = data[7]
    pamount = data[8]
    exam_fee.ramount = tamount - pamount
    return render_template('examfee.html', name=name, rollno=rollno, class1=class1, year=year, gender=gender,
                           section=section, tamount=tamount, pamount=pamount, ramount=exam_fee.ramount,
                           profile_link=profile_link,status1=status1,damount=damount)


@app.route('/hostel_fee')
def hostel_fee():
    roll_no1 = verify.roll_no
    if not session.get('name'):
        return redirect('login')
    con = sql.connect('logins', check_same_thread=False)
    cur = con.cursor()
    cur.execute('SELECT LOGIN.ROLLNO,STUDENT_INFO.NAME,STUDENT_INFO.ACADEMIC,STUDENT_INFO.CLASS,'
                'STUDENT_INFO.SECTION,STUDENT_INFO.GENDER,STUDENT_INFO.profile_link,'
                ' HOSTEL_FEE.TOTAL_AMOUNT,HOSTEL_FEE.PAID_AMOUNT,'
                'HOSTEL_FEE.DUE_AMOUNT FROM LOGIN INNER JOIN STUDENT_INFO ON LOGIN.ROLLNO = STUDENT_INFO.ROLLNO '
                'INNER JOIN HOSTEL_FEE ON LOGIN.ROLLNO = HOSTEL_FEE.ROLLNO WHERE LOGIN.ROLLNO= ?', (roll_no1,))
    data = cur.fetchone()
    cur.execute(
        "SELECT STATUS.STATUS,COLLEGE_FEE.DUE_AMOUNT FROM COLLEGE_FEE INNER JOIN STATUS ON STATUS.ROLLNO=COLLEGE_FEE.ROLLNO AND STATUS.CATEGORY='college_fee'")
    fee_details = cur.fetchall()
    con.close()
    if fee_details==[]:
        status1=''
        damount=''
    else:
        status1=fee_details[0][0]
        damount=fee_details[0][1]
    name = data[1]
    rollno = data[0]
    class1 = data[3]
    year = str(data[2])
    gender = data[5]
    section = data[4]
    profile_link = '../static/' + data[6]
    tamount = data[7]
    pamount = data[8]
    hostel_fee.ramount = tamount - pamount
    return render_template('hostelfee.html', name=name, rollno=rollno, class1=class1, year=year, gender=gender,
                           section=section, tamount=tamount, pamount=pamount, ramount=hostel_fee.ramount,
                           profile_link=profile_link,status1=status1,damount=damount)


@app.route('/other_fee')
def other_fee():
    roll_no1 = verify.roll_no
    if not session.get('name'):
        return redirect('login')
    con = sql.connect('logins', check_same_thread=False)
    cur = con.cursor()
    cur.execute('SELECT LOGIN.ROLLNO,STUDENT_INFO.NAME,STUDENT_INFO.ACADEMIC,STUDENT_INFO.CLASS,'
                'STUDENT_INFO.SECTION,STUDENT_INFO.GENDER,STUDENT_INFO.profile_link,'
                ' OTHER_FEE.TOTAL_AMOUNT,OTHER_FEE.PAID_AMOUNT,'
                'OTHER_FEE.DUE_AMOUNT FROM LOGIN INNER JOIN STUDENT_INFO ON LOGIN.ROLLNO = STUDENT_INFO.ROLLNO '
                'INNER JOIN OTHER_FEE ON LOGIN.ROLLNO = OTHER_FEE.ROLLNO WHERE LOGIN.ROLLNO = ?', (roll_no1,))
    data = cur.fetchone()
    cur.execute(
        "SELECT STATUS.STATUS,COLLEGE_FEE.DUE_AMOUNT FROM COLLEGE_FEE INNER JOIN STATUS ON STATUS.ROLLNO=COLLEGE_FEE.ROLLNO AND STATUS.CATEGORY='college_fee'")
    fee_details = cur.fetchall()
    con.close()
    if fee_details==[]:
        status1=''
        damount=''
    else:
        status1=fee_details[0][0]
        damount=fee_details[0][1]
    name = data[1]
    rollno = data[0]
    class1 = data[3]
    year = str(data[2])
    gender = data[5]
    section = data[4]
    profile_link = '../static/' + data[6]
    tamount = data[7]
    pamount = data[8]
    other_fee.ramount = tamount - pamount
    return render_template('otherfee.html', name=name, rollno=rollno, class1=class1, year=year, gender=gender,
                           section=section, tamount=tamount, pamount=pamount, ramount=other_fee.ramount,
                           profile_link=profile_link,status1=status1,damount=damount)


@app.route('/college_fee/pay/',methods=["GET","POST"])
def pay():
    if not session.get('name'):
        return redirect('login')
    amount = college_fee.ramount
    date1 = date.today()
    return render_template('pay.html', amount=amount, date=date1, fee_name='College Fee')


@app.route('/bus_fee/pay/')
def pay1():
    if not session.get('name'):
        return redirect('login')
    amount = bus_fee.ramount
    date1 = date.today()
    return render_template('pay.html', amount=amount, date=date1, fee_name='Bus Fee')


@app.route('/exam_fee/pay/')
def pay2():
    if not session.get('name'):
        return redirect('login')
    amount = exam_fee.ramount
    date1 = date.today()
    return render_template('pay.html', amount=amount, date=date1, fee_name='Exam Fee')


@app.route('/hostel_fee/pay/')
def pay3():
    if not session.get('name'):
        return redirect('login')
    amount = hostel_fee.ramount
    date1 = date.today()
    return render_template('pay.html', amount=amount, date=date1, fee_name='Hostel Fee')


@app.route('/other_fee/pay/')
def pay4():
    if not session.get('name'):
        return redirect('login')
    amount = other_fee.ramount
    date1 = date.today()
    return render_template('pay.html', amount=amount, date=date1, fee_name='Other Fee')


@app.route('/updating', methods=['POST', 'GET'])
def updating():
    if not session.get('name'):
        return redirect('login')
    if request.method == 'POST':
        transaction_no = request.form['utrno']
        amount = request.form['amount']
        tr_date = request.form['date']
        filesz = request.files['file'].read()
        category = request.referrer
        category = category.split('/')
        category = category[3]

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            con = sql.connect('logins')
            cur = con.cursor()
            cur.execute(
                'INSERT INTO STATUS(ROLLNO, AMOUNT, CATEGORY, UTR_NO, DATE, PROOF_LINK,UDATE)  VALUES(?,?,?,?,?,?,?) ',
                (verify.roll_no, amount, category, transaction_no, tr_date, filename, date.today()))
            con.commit()
            con.close()
            return redirect(url_for('status'))
        else:
            return render_template('pay.html', amount=amount, date=tr_date, number=transaction_no,
                                   msg='upload jpg/pdf/jpeg only')


@app.route('/index/status/')
def status():
    if not session.get('name'):
        return redirect('login')
    con = sql.connect('logins')
    cur = con.cursor()
    cur.execute(
        "SELECT STATUS.ROWID, STUDENT_INFO.NAME,STUDENT_INFO.ROLLNO,STATUS.AMOUNT,STATUS.CATEGORY,STATUS.DATE,STATUS.STATUS FROM STATUS INNER JOIN STUDENT_INFO ON STATUS.ROLLNO=STUDENT_INFO.ROLLNO WHERE STATUS.ROLLNO= ? ",
        (verify.roll_no,))
    data = cur.fetchall()
    con.close()
    return render_template('status.html', status1=data)


@app.route('/admin/')
def admin():
    if session.get('name') == 'ADMIN@NBKRIST.ORG':
        con = sql.connect('logins')
        cur = con.cursor()
        cur.execute(
            "SELECT STATUS.ROWID, STUDENT_INFO.NAME,STUDENT_INFO.ROLLNO, STUDENT_INFO.CLASS ,STATUS.AMOUNT,STATUS.UTR_NO, STATUS.CATEGORY,STATUS.DATE,STATUS.STATUS FROM STATUS INNER JOIN STUDENT_INFO ON STATUS.ROLLNO=STUDENT_INFO.ROLLNO where STATUS.STATUS=0")
        admin_data = cur.fetchall()
        con.close()

        return render_template('admin.html', status1=admin_data)
    else:
        abort(404)


@app.route('/search/', methods=['POST', 'GET'])
def search():
    if not session.get('name') == 'ADMIN@NBKRIST.ORG':
        return redirect(url_for('login'))
    if request.method == 'POST':
        searchd = request.form['search']
        con = sql.connect('logins')
        cur = con.cursor()
        cur.execute("SELECT STATUS.ROWID, STUDENT_INFO.NAME,STUDENT_INFO.ROLLNO,STATUS.AMOUNT,STATUS.UTR_NO,"
                    " STATUS.CATEGORY,STATUS.DATE,STATUS.STATUS FROM STATUS INNER JOIN STUDENT_INFO ON "
                    "STATUS.ROLLNO=STUDENT_INFO.ROLLNO WHERE STATUS.UTR_NO=? OR STATUS.ROLLNO=? OR STATUS.ROWID=? OR STUDENT_INFO.NAME=?",
                    (searchd, searchd, searchd, searchd))
        admin_data = cur.fetchall()
        con.close()
        return render_template('admin.html', status1=admin_data)
    return redirect('/admin')


@app.route('/undo', methods=['POST', 'GET'])
def undo():
    if not session.get('name') == 'ADMIN@NBKRIST.ORG':
        return redirect(url_for('login'))
    if request.method == 'POST':
        utrno = request.form.get('utrno')
        con = sql.connect('logins')
        cur = con.cursor()
        cur.execute('SELECT AMOUNT,CATEGORY,ROLLNO FROM STATUS WHERE UTR_NO=?', (utrno,))
        amount = cur.fetchone()
        cur.execute(f'SELECT PAID_AMOUNT ,TOTAL_AMOUNT  FROM {amount[1]} WHERE ROLLNO=?', (amount[2],))
        pamount = cur.fetchone()

        tamount = pamount[0] - amount[0]
        damount = pamount[1] -tamount
        cur.execute(f'UPDATE {amount[1]} SET PAID_AMOUNT=? , DUE_AMOUNT=? WHERE ROLLNO=?',
                    (tamount, damount, amount[2]))

        cur.execute('UPDATE STATUS SET STATUS=0 WHERE UTR_NO=?', (utrno,))
        con.commit()
        con.close()
        return redirect('/admin')
    return abort(404)


@app.route('/deny', methods=['POST', 'GET'])
def deny():
    if not session.get('name') == 'ADMIN@NBKRIST.ORG':
        return redirect(url_for('login'))

    if request.method == 'POST':
        utrno = request.form.get('utrno')
        con = sql.connect('logins')
        cur = con.cursor()
        cur.execute('UPDATE STATUS SET STATUS=2 WHERE UTR_NO=?', (utrno,))
        con.commit()
        con.close()
        return redirect('/admin')
    return abort(404)


@app.route('/accept', methods=['POST', 'GET'])
def accept():
    if not session.get('name') == 'ADMIN@NBKRIST.ORG':
        return redirect(url_for('login'))
    if request.method == 'POST':
        utrno = request.form.get('utrno')
        con = sql.connect('logins',check_same_thread=False)
        cur = con.cursor()
        cur.execute('SELECT AMOUNT,CATEGORY,ROLLNO FROM STATUS WHERE UTR_NO=?', (utrno,))
        amount = cur.fetchone()
        cur.execute(f'SELECT PAID_AMOUNT ,TOTAL_AMOUNT  FROM {amount[1]} WHERE ROLLNO=?', (amount[2],))
        pamount = cur.fetchone()

        tamount=amount[0]+pamount[0]
        damount=pamount[1]-tamount
        cur.execute(f'UPDATE {amount[1]} SET PAID_AMOUNT=? , DUE_AMOUNT=? WHERE ROLLNO=?', (tamount,damount,amount[2]))
        cur.execute('UPDATE STATUS SET STATUS=1  WHERE UTR_NO=?', (utrno,))
        con.commit()
        con.close()
        return redirect('/admin')
    return abort(404)


@app.route('/admin/accepted')
def accepted():
    if not session.get('name'):
        return redirect('login')
    con = sql.connect('logins')
    cur = con.cursor()
    cur.execute("SELECT STATUS.ROWID, STUDENT_INFO.NAME,STUDENT_INFO.ROLLNO,STUDENT_INFO.CLASS,STATUS.AMOUNT,STATUS.UTR_NO, STATUS.CATEGORY,STATUS.DATE,STATUS.STATUS FROM STATUS INNER JOIN STUDENT_INFO ON STATUS.ROLLNO=STUDENT_INFO.ROLLNO WHERE STATUS.STATUS=1")
    data = cur.fetchall()
    con.close()
    return render_template('admin.html', status1=data)

@app.route('/admin/rejected')
def rejected():
    if not session.get('name'):
        return redirect('login')
    con = sql.connect('logins')
    cur = con.cursor()
    cur.execute("SELECT STATUS.ROWID, STUDENT_INFO.NAME,STUDENT_INFO.ROLLNO,STUDENT_INFO.CLASS,STATUS.AMOUNT,STATUS.UTR_NO, STATUS.CATEGORY,STATUS.DATE,STATUS.STATUS FROM STATUS INNER JOIN STUDENT_INFO ON STATUS.ROLLNO=STUDENT_INFO.ROLLNO WHERE STATUS.STATUS=2")
    data = cur.fetchall()
    con.close()
    return render_template('admin.html', status1=data)

@app.route('/admin/student_register/')
def stureg():
    if not session.get('name'):
        return redirect('login')
    con=sql.connect('logins')
    cur=con.cursor()
    cur.execute('SELECT STUDENT_REG.ROWID,STUDENT_INFO.NAME, STUDENT_REG.ROLLNO,STUDENT_INFO.CLASS,STUDENT_INFO.ACADEMIC,STUDENT_REG.STATUS FROM STUDENT_REG INNER JOIN STUDENT_INFO  on STUDENT_REG.ROLLNO = STUDENT_INFO.ROLLNO where STUDENT_REG.STATUS=0')
    data=cur.fetchall()
    con.close()
    return render_template('studentreg.html',stureg=data)


if __name__ == '__main__':
    context = ('local.crt', 'local.key')  # certificate and key files
    app.run(debug=True, ssl_context=context)
