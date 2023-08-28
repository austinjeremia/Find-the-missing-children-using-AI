from flask import Flask,render_template,request
import mysql.connector
import face_recognition
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import imghdr

app = Flask(__name__)
mydb = mysql.connector.connect(host="localhost", user="root", password="", database="children")
mycursor = mydb.cursor(buffered=True)

@app.route('/')
def login():
    return render_template('UserLogin.html')


@app.route('/loginpost', methods=['POST', 'GET'])
def userloginpost():
    global data1
    if request.method == 'POST':
        data1 = request.form.get('uname')
        data2 = request.form.get('password')

        sql = "SELECT * FROM `users` WHERE `uname` = %s AND `password` = %s"
        val = (data1, data2)

        mycursor.execute(sql, val)

        account = mycursor.fetchone()


        mydb.commit()

        if account:
            return render_template('index1.html')
        else:
            return render_template('goback.html', msg='Invalid')

@app.route('/NewUser')
def newuser():
    return render_template('NewUser2.html')

@app.route('/reg',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        uname = request.form.get('uname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        password = request.form.get('psw')
        gender = request.form.get('gender')
        sql = "INSERT INTO users (name, uname, email , phone, age, password, gender) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (name, uname, email, phone, age, password, gender)
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('UserLogin.html')

@app.route('/admin')
def admin():
    return render_template('adminlogin1.html')

@app.route('/sv')
def svalue():
    mycursor.execute("select * from childinfo where pin = 620026 ")
    data = mycursor.fetchall()
    return render_template('index.html', data=data)

@app.route('/adminhome')
def adminhome():

    mycursor.execute("select * from users ")
    data = mycursor.fetchall()

    return render_template('AdminHome.html', data=data)

@app.route('/admindetect')
def admindetect():
    mycursor.execute("select * from login ")
    data = mycursor.fetchall()

    mycursor.execute("select * from detect ")
    datas = mycursor.fetchall()

    return render_template('detection1.html', data= data,datas=datas)






@app.route('/adminpost', methods = ['POST','GET'])
def uadminloginpost():
    global data1
    if request.method == 'POST':
        data1 = request.form.get('uname')
        data2 = request.form.get('password')
        sql = "SELECT * FROM `admin` WHERE `uname` = %s AND `password` = %s"
        val = (data1, data2)
        mycursor.execute(sql,val)
        account = mycursor.fetchone()


        mydb.commit()
        if account:
            mycursor.execute("select * from users ")
            data = mycursor.fetchall()


            return render_template('adminhome1.html', data=data)
        else:
            return render_template('goback.html', msg = 'Invalid')



@app.route('/index')
def index():
    return render_template('index1.html')

def report_send_mail(mailid1,message,image_path):
    '''
    This function sends mail
    '''
    #label = "Eye Close"
    with open(image_path, 'rb') as f:
        img_data = f.read()
    fromaddr = "sdprotrichy2k23@gmail.com"
    toaddr = mailid1
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Alert"
    body = message
    msg.attach(MIMEText(body, 'plain'))  # attach plain text
    image = MIMEImage(img_data, name=os.path.basename(image_path))
    msg.attach(image) # attach image
    s = smtplib.SMTP('smtp.gmail.com',587)
    s.starttls()
    s.login(fromaddr, "xwycjezbamzaroti")
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()

@app.route('/child',methods=['POST','GET'])
def child():
    if request.method == 'POST':
        file = request.files['fileupload']
        file.save("static/upload/" + file.filename)
        age1 = request.form.get('age')
        gender1 = request.form.get('gender')
        street1 = request.form.get('street')
        city1 = request.form.get('city')
        district1 = request.form.get('district')
        state1 = request.form.get('state')
        pin1 = request.form.get('pin')
        Image = file.filename
        ImageURL = "static/upload/" + file.filename
        sql = "INSERT INTO childinfo (age, gender, street , city, district, state, pin,image,imageurl) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)"
        val = (age1, gender1, street1, city1, district1, state1, pin1,Image,ImageURL)
        mycursor.execute(sql, val)
        mydb.commit()
        id1 = []
        mycursor.execute("select imageurl,email from casedetail")
        data = mycursor.fetchall()
        for sts in data:
            j = sts[0]
            k = sts[1]
            print(j)
            print(k)

            known_image = face_recognition.load_image_file(j)
            unknown_image = face_recognition.load_image_file(ImageURL)
            face_locations = face_recognition.face_locations(known_image, model="hog")
            face_locations1 = face_recognition.face_locations(unknown_image, model="hog")
            if len(face_locations) > 0 and  len(face_locations1) > 0:
                known_encoding = face_recognition.face_encodings(known_image, face_locations)[0]
                unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
                distance = face_recognition.face_distance([known_encoding], unknown_encoding)
                if distance < 0.6:
                    id1.append(k)
                    mailid = id1[0]
                    sql = """UPDATE casedetail SET status = "Match" where email = %s; """
                    val = (mailid,)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    message1 = 'your relation is found in ' + street1 + 'street ' + city1 + 'city ' + district1 + 'district ' + state1 + 'state ' + pin1
                    shw = ImageURL
                    report_send_mail(mailid, message1, shw)

                    print(" face match")
                else:
                    print(" does not match")
            else:
                print(" not found")


            # Preprocess the images
            #known_encoding = face_recognition.face_encodings(known_image)[0]
            #print(known_encoding)


            # Compute the Euclidean distance between the face encodings


            # Verify if the faces match

            print(id1)

        return render_template('index.html')

@app.route('/adminupload')
def adminupload():
    return render_template('adminupload.html')

@app.route('/childcase',methods=['POST','GET'])
def childcase():
    if request.method == 'POST':
        file = request.files['caseupload']
        file.save("static/casedetail/" + file.filename)
        child2 = request.form.get('child')
        age2 = request.form.get('age')
        gender2= request.form.get('gender')

        parent2 = request.form.get('parent')
        phone2 = request.form.get('phone')
        email2 = request.form.get('email')
        address2 = request.form.get('address')
        pin2 = request.form.get('pin')
        Image2 = file.filename
        ImageURL2 = "static/casedetail/" + file.filename
        sql = "INSERT INTO casedetail (child,age, gender, parent , phone, email, address, pin,image,imageurl) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s, %s)"
        val = (child2,age2, gender2,  parent2, phone2, email2, address2,pin2,Image2,ImageURL2)
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('adminhome1.html')
@app.route('/cased', methods = ['POST','GET'])
def cased():
    mycursor.execute("select * from casedetail ")
    data = mycursor.fetchall()


    return render_template('file.html', data=data)

'''@app.route('/match', methods = ['POST','GET'])
def match1():
    id1 = []
    mycursor.execute("select imageurl from casedetail ")
    data = mycursor.fetchall()
    id1.append(data)
    print(id1)
    m = len(id1)
    for f in range(m):
        print(f)
        p = id1[f]
        known_image = face_recognition.load_image_file(p)
        unknown_image = face_recognition.load_image_file(ImageURL)

        # Preprocess the images
        known_encoding = face_recognition.face_encodings(known_image)[0]
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

        # Compute the Euclidean distance between the face encodings
        distance = face_recognition.face_distance([known_encoding], unknown_encoding)

        # Verify if the faces match
        if distance < 0.6:
            print("The faces match.")
        else:
            print("The faces do not match.")

    return render_template('index.html', data=data)'''


if __name__ == '__main__':
    app.run(debug=True)
