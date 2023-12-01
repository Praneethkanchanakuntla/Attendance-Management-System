import pymongo
from pymongo import MongoClient
import datetime
from flask import Flask,render_template,request,flash,redirect, url_for,session
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField,EmailField
from wtforms.validators import DataRequired, Length
app=Flask(__name__)
app.secret_key = 'mysecretkey'
bootstrap = Bootstrap5(app)

@app.route('/')
def home():
    return render_template("home.html")
@app.route('/login')
def login():
    return render_template("login.html")
cluster=MongoClient("mongodb+srv:/")
db=cluster["User"]
collection=db["User_details"]
login_details=db['login_details']
professor_collection=db['professor_login']
professor_details=db['professor_details']
student_enrollments=db['student_enrollments']
time_table=db['time_table']
code=db['seceret_code']
attendance=db['attendance']
message_collection=db['message_collection']

def insert_into_login_collection(x,y):
    if login_details.count_documents({'email':x,'password':y}) == 0:
        login_details.insert_one({'email':x,'password':y})
    else:
        print("already exists")
        print(x)

@app.route('/login/professor',methods=['GET', 'POST'])
def professor_login():
    return render_template('pro_login.html')
def is_exist_professor(x,y):
    if professor_collection.count_documents({'email':x,'password':y})!=0:
        return True
    else:
        return False
@app.route('/login/professor/dashboard',methods=['POST',"GET"])
def professor_dashboard():
    if request.method=='POST':
        password=request.form['password']
        email=request.form['email']
        is_exists=is_exist_professor(email,password)
        if is_exists==True:
            pf_details=list(professor_details.find({'professor_email':email},{'_id':0}))
            session['email_professor']=email
            return render_template("professor_dashboard.html",prof=pf_details)
        else:
            return render_template("pro_login.html")
@app.route('/login/student',methods=['GET', 'POST'])
def student_login():
    return render_template("stu_login.html")
@app.route('/login/student/dashboard',methods=['GET','POST'])
def student_dashboard():
    if request.method == 'POST':
        
        password=request.form.get('password')
        email=request.form.get('email')
        is_there=is_there_in_collection(email,password)
        if is_there==True:
           return student_display(email)
        else:
  
           return render_template("stu_login.html")
def student_display(email):
    user=collection.find({'user_email':email},{'_id':0})
    result=collection.aggregate([{
        '$lookup':{'from':'student_enrollments',
                     'localField':'user_id',
                     'foreignField':'student_id',
                     'as':"user_enrollments"}}])
    #output=result.find({'user_email':email},{'_id':0})
    session['email']=email
    user_enr = filter(lambda x: x['user_email'] == email, result)
    user_enr=list(user_enr)
    subject_ids = [j['subject_id'] for i in user_enr for j in i['user_enrollments']]
    subject_ids=str(subject_ids[0])
    tt_table=time_table.find({'subject_id':subject_ids},{'_id':0})
    tt_table=list(tt_table)
    return render_template('student_dashboard.html',user=user,student_enrollments=user_enr,tt_table=tt_table)

def is_there_in_collection(x,y):
    if login_details.count_documents({'email':x,'password':y})!=0:
        return True
    else:
        return False
insert_into_login_collection(x='dhruv1@gmail.com',y='Company@00')
def professor_login_collection(x,y):
    if professor_collection.count_documents({'email':x,'password':y})==0:
        professor_collection.insert_one({'email':x,'password':y})
    else:
        print("already user exists")
professor_login_collection('dumble@gmail.com','1234')

def professor_collection_entry(a,b,c,d):
    if professor_details.count_documents({'professor_id':a,'professor_email':b,'subject_taught':c,'name':d})==0:
        professor_details.insert_one({'professor_id':a,'professor_email':b,'subject_taught':c,'name':d})
    else:
        pass
professor_collection_entry('101','dumble@gmail.com',['ITCS1','ITCS2'],'Dumbledore')

def student_enrollments_entry(x,y):
    if student_enrollments.count_documents({'subject_id':x,'student_id':y})==0:
        student_enrollments.insert_one({'subject_id':x,'student_id':y})
    else:
        pass
student_enrollments_entry('ITCS1',12)

def time_table_entry(x,a,b,c):
    if time_table.count_documents({'day':x,'start_time':a,'end_time':b,'subject_id':c})==0:
        time_table.insert_one({'day':x,'start_time':a,'end_time':b,'subject_id':c})
    else:
        pass
time_table_entry('Wednesday','10:00','12:00','ITCS1')
def s_code(a,b,d):
    if code.count_documents({'date':a,'subject_id':b,'key':d})==0:
        code.insert_one({'date':a,'subject_id':b,'key':d})
    else:
        pass


def attendance_entry(x,y,z):
    if attendance.count_documents({'date':x,'subject_id':y,'student_id':z})==0:
        attendance.insert_one({'date':x,'subject_id':y,'student_id':z})
    else:
        pass

@app.route("/login/student/dashboard/attendance",methods=['POST','GET'])
def attendance_check():
    codes=request.form['code']
    email=session.get('email')
    course=request.form['course']
    get_time_table=time_table.find({'subject_id':course},{'_id':0})
    today = datetime.date.today()
    s = today.strftime('%Y-%m-%d')
    day_of_week = today.strftime('%A')
    for i in get_time_table:
        if i['day']==day_of_week:
            secret_code_coll=code.find({'subject_id':'ITCS2'},{'_id':0})
            for j in secret_code_coll:
                print(j['key'])
                if j['key']==codes and j['date']==s:
                    attendance_entry(s,course,email)
                    flash("Attendance is recorded")
                    return redirect(url_for('student_display'))
                else:
                    flash("Unsucessfull attendance, contact instructor")
                    return redirect(url_for('student_display'))
    return render_template("contact_professor.html",subject_id=course)
@app.route("/login/student/dashboard/attendance/message",methods=['POST','GET'])
def send_message_student():
    if request.method=='POST':
        msg=request.form['msg']
        subject_id=request.form['course']
        email=session.get('email')
        message_collection.insert_one({'subject_id':subject_id,'msg':msg,'student_email':email})
        flash("message send successfully")
    return render_template("contact_professor.html")
@app.route("/login/student/attendance/code",methods=['POST','GET'])
def code_entry():
    return """<h1> hello </h1>"""

@app.route("/login/professor/dashboard/setcode",methods=['POST','GET'])
def Set_attendance_code():
    course=request.form['course']
    date=request.form['date']
    codes=request.form['code']
    s_code(date,course,codes)
    return render_template("set_code.html",codes=codes)
@app.route("/login/student/dashboard/edit",methods=['POST','GET'])
def edit_profile():
    email=session.get('email')
    user=collection.find({'user_email':email},{'_id':0})
    form = UserForm()
    if form.validate_on_submit():
        user_name=form.name.data
        password=form.password.data
        collection.update_one({'user_email':email},{'$set':{'user_name':user_name}})
        login_details.update_one({'email':email},{'$set':{'password':password}})
        flash("updated Sucessfully")
    for i in user:
        form.name.data=i['user_name']
    return render_template("edit_profile.html",form=form,email=email)

@app.route('/login/professor/dashboard/viewMessages',methods=["Post","Get"])
def view_messages():
    email_professor=session.get('email_professor')
    professor=professor_details.find({'professor_email':email_professor},{'_id':0})
    for i in professor:
       for j in i['subject_taught']:
        message=list(message_collection.find({'subject_id':j},{'_id':0}))
    return render_template('message_view.html',data=message)
@app.route('/login/professor/dashboard/actions',methods=['Post','Get'])
def Action_center():
    return render_template('action_center.html')
@app.route('/login/professor/dashboard/actions/studentoverview/main',methods=['Post','Get'])
def student_properties():
    if request.method == 'POST':
        email_professor=session.get("email_professor")
        professor=list(professor_details.find({'professor_email':email_professor},{'_id':0}))
        course=request.form.get('course')
        enrollments=student_enrollments.find({'subject_id':course},{'_id':0})
        student_details=collection.find({'user_id':i.student_id for i in enrollments },{'_id':0})
        return render_template("student_overview.html",data=professor,enrol=enrollments,student=student_details)
    return render_template('student_overview.html')
   
@app.route('/login/professor/dashboard/actions/studentoverview',methods=['Post','Get'])
def student_overview():
    return redirect(url_for('student_properties'))

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password=StringField('Password',validators=[DataRequired()])
    submit=SubmitField('Edit')
if __name__=='__main__':
    app.run(debug=True)






