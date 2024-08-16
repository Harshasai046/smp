from flask import Flask,render_template,request,url_for,redirect,flash,session,send_file
from flask_session import Session
import mysql.connector
from otp import genotp
from cmail import sendmail
from key import secret_key
from stoken import token,dtoken
from io import BytesIO
import re
app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
Session(app)
mydb=mysql.connector.connect(host='localhost',user='root',password='Harshasai@046',db='spm')
app.secret_key=b'w\x9e\xe6u\x17'
@app.route('/')
def index():
    return render_template('welcome.html')
@app.route("/signin",methods=['GET','POST'])
def signin():
    if request.method=='POST':
        print(request.form)
        f_name=request.form['f_name']
        l_name=request.form['l_name']
        password=request.form['password']
        email=request.form['mail']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(email) from student where email=%s',[email])
        data=cursor.fetchone()[0]
        if data==0:
            otp=genotp()
            data={'otp':otp,'email':email,'f_name':f_name,'l_name':l_name,'password':password}
            subject='OTP has benn veified'
            body=f'Registration otp for SPM application {otp}'
            sendmail(to=email,subject=subject,body=body)
            return redirect(url_for('verifyotp',data1=token(data=data)))
        else:
            flash('Email aready existed')
            return redirect(url_for('signin'))
    return render_template("signin.html")
@app.route('/otp/<data1>',methods=['GET','POST'])
def verifyotp(data1):
    try:
        data1=dtoken(data=data1)
    except Exception as e:
        print(e)
        return 'time out of otp'
    else: 
        if request.method=='POST':
            uotp=request.form['otp']
            if uotp==data1['otp']:
                cursor=mydb.cursor(buffered=True)        
                cursor.execute('insert into student(email,student_fname,studet_lname,password) values(%s,%s,%s,%s)',[data1['email'],data1['f_name'],data1['l_name'],data1['password']])
                mydb.commit()
                cursor.close()
                flash('Registration sucessfull')
                return redirect(url_for('login'))
            else:
                return f'otp invalid pls check your mail.'
    finally:
        print('done')
    return render_template('otp.html')
@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        mail=request.form['mail']
        password=request.form['password']
        print(password.encode('utf-8'))
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select email,password from student where email=%s',[mail])
            data=cursor.fetchone()
            print(data[1])
        except Exception as e:
            print(e)
            return 'email is wrong'
        else:
            if data[1]==password.encode('utf-8'):
                session['email']=email
                if not session.get(email):
                    session[email1]={}
                    return redirect(url_for('panel'))
            else:
                flash('invalid password')
        return render_template('login.html')
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            added_by=session.get('email')
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into notes(title,note_content,added_by) values(%s,%s,%s)',[tittle,content,added_by])
            mydb.commit()
            cursor.close()
            flash(f'notes {tittle} added successfully')
            return redirect(url_for('panel'))
    return render_template('notes.html')
@app.route('/panel')
def panel():
    return render_template('panel.html')
@app.route('/fileupload',methods=['GET','POST'])
def fileupload():
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        if request.method=='POST':
            file=request.files['file']
            file_name=file.filename
            added_by=session.get('email')
            file_data=file.read()
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into files_data(file_name,file_data,added_by)values(%s,%s,%s))',[file_name,file_data,added_by])
            mydb.commit()
            cursor.close()
            flash(f'file{file,filename} added successfully')
            return redirect(url_for('panel'))
    return render_template('fileupload.html')
@app.route('/viewall_files',methods=['GET','POST'])
def viewall_files():
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        added_by=session.get('email')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select fid,file_name,created_at from files_data where added_by=%s',[added_by])
        data=cursor.fetchall()
        return render_template('allfiles.html',data=data)
@app.route('/view_file/<fid>')
def view_file(fid):
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select file_name,file_data from files_data where f_id=%s and added by=%s',[fid,session.get('email')])
            fname,fdata=cursor.fetchone()
            bytes_data=BytesIO(fdata)
            filename=fname
            return send_file(bytes_data,download_name=filename,as_attachment=False)
        except Exception as e:
            print(e)
            return 'file not found'
        finally:
            cursor.close()
@app.route('/download_file/<fid>')
def download_file(fid):
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select file_name,file_data from files_data where f_id=%s and added_by=%s',[fid,session.get('email')])
            fname,fdata=cursor.fetchone()
            bytes_data=BytesIO(fdata)
            filename=fname
            return send_file(bytes_data,download_name=filename,as_attachment=True)
        except Exception as e:
            print(e)
            return 'File not found...'
        finally:
            cursor.close()
@app.route('/delete_file/<fid>')
def delete_file(fid):
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('delete from files_data where f_id=%s',[fid])
            mydb.commit()
            cursor.close()
            flash('File deleted successfully...')
            return redirect(url_for('panel'))
        except Exception as e:
            print(e)
            return 'File not found'
@app.route('/forgot_password',methods=['GET','POST'])
def forgotpassword():
    if session.get('email'):
        return redirect(url_for('login'))
    else:
        if request.method=='POST':
            email=request.form['email']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(email) from student where email=%s',[email])
            count=cursor.fetchone()[0]
            if count==0:
                flash('Email does not existed')
                return redirect(url_for('signin'))
            elif count==1:
                subject='Reset link for SPM Application'
                body=f"Reset : {url_for('reset',data=token(data=email),_external=True)}"
                sendmail(to=email,subject=subject,body=body)
                flash("Reset link has been sent to given mail")
            else:
                return 'something went wrong'
    return render_template('forgot.html')
@app.route('/reset/<data>',methods=['GET','POST'])
def reset(data):
    if request.method=='POST':
        email=dtoken(data)
        password=request.form['password']
        cpassword=request.form['cpassword']
        if password==cpassword:
            try:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('update student set password=%s where email=%s',[password,email])
                mydb.commit()
                cursor.close()
                flash("Password Updated Successfully...")
                return redirect(url_for('login'))
            except Exception as e:
                print(e)
                return "Error"
        else:
            return "Password doesn't match" 
    return render_template('reset.html')
@app.route('/search',methods=['GET','POST'])
def search():
    if session.get('email'):
        if request.method=='POST':
            name=request.form['sname']
            strg=['A-Za-z0-9']
            pattern=re.compile(f'^{strg}',re.IGNORECASE)
            if (pattern.match(name)):
                cursor=mydb.cursor(buffered=True)
                cursor.execute('select * from notes where email=%s and title like %s',[session.get('email'),name+'%'])
                sname=cursor.fetchall()
                sname=cursor.fetchall('select f_id,file_name,created_at from files_data where added_by=%s and file_name like=%s',[session.get('email'),name+'%'])
                fname=cursor.fetchall()
                cursor.close()
                return render_template('panel.html',sname=sname,fname=fname)
            else:
                flash('result not found')
                return redirect(url_for('panel'))
    else:
        return redirect(url_for('login'))
@app.route('/getexcel_data')
@app.route('/getexcel_data')
def getexcel_data():
    if not session.get('email'):
        return redirect(url_for('login'))
    else:
        user=session.get('email')
        columns=['Title','Content','Data']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select title,note_content,created_at from notes where added_by=%s',[user])j 
        data=cursor.fetchall()
        array_data=[list[1] for i in data]
        array_data.insert(0,columns)
        return excel.make_response_from_array(array_data,'xlsx',filename='notesdata')
app.run(debug=True,use_reloader=True)