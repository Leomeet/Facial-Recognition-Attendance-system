from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpResponse
from django.views.generic import ListView,CreateView,UpdateView
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout,get_user_model
from django.contrib.auth.decorators import login_required
from .models import Person, City,Attendance,TrainingData
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password,check_password
from .forms import FacultyRegisteration,FacultyEdit,FacultyEditEmail
from .filters import AttendenceFilter
from datetime import date,datetime
import random
import string
import pickle
import base64
from playsound import playsound
from django.conf import settings 
from django.core.mail import send_mail ,EmailMessage
from ipware import get_client_ip
import smtplib
import re
import cv2
import os
import csv
import math
from PIL import Image
from threading import Thread
import numpy as np
import pandas as pd
import time,datetime
import face_recognition
from collections import defaultdict
import openpyxl
import xlsxwriter
import collections
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Sum
# Create your views here.

# known_face_names=[]
# known_face_encodings=[]
dates_lis=[]
ids_lis=[]

def home(request):
    ip, is_routable = get_client_ip(request)
    print("ip of client is : ",ip)
    return render(request,'main.html')

# faculty registration
def admin_page(request,id=None):
    msg=None
    username=str(request.session['fetch_username'])
    form=FacultyRegisteration()
    details=Person.objects.all()

    return render(request,'admin_login.html',{'form':form, 'id':0, 'details':details,'username':username})

def admin_home(request):
    
    username=request.session['fetch_username']
    return render(request,'admin_menu.html',{'username':username})

def admin_login(request,id=None):
    msg=None

    if request.method=='POST':
        user=authenticate(request,username=request.POST.get('username'),password=request.POST.get('password'))
        if user is not None:
            request.session['fetch_username']=request.POST.get('username')
            return render(request,'admin_menu.html',{'username':request.POST.get('username')})
        else:
            msg='Username or Password is Invalid'
        
    
    return render(request,'main.html',{'msg':msg})

def faculty_edit(request,id):
    username=request.session['fetch_username']
    #print("username in admin_page is : ",username)
    details=Person.objects.all()
    form=Person.objects.get(pk=id)
    # print("PK : ",form)
    form=FacultyEditEmail(instance=form)
    # print("Form : ",form)

    return render(request,'admin_login.html',{'form':form, 'id':id, 'details':details,'username':username})



def faculty_add(request,id=0):
    username=request.session['fetch_username']
    details=Person.objects.all()
    
    #print("username in admin_page is : ",username)
    msg=None
    er_msg=None
    regex_1 = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}\w+[.]\w{2,3}$'
    regex_2='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    
    if request.method=='POST':
        faculty_page_var=request.POST['faculty_page']
        print("value of faculty_page_var is : ",faculty_page_var)
        if id is 0:
            form=FacultyRegisteration(request.POST)
        else:
            form=FacultyEditEmail(request.POST)
        print("Form is : ",form.is_valid())
        print("Form errors : ",form.errors)
        print("Value of id is : ",id)
        inst=form.cleaned_data['inst']
        dept=form.cleaned_data['dept']
        reg_id=form.cleaned_data['reg_id']
        if form.is_valid() and (inst is not None) and (dept is not None) and (reg_id is not None):
            #if fac exist
            if Person.objects.filter(reg_id=reg_id).exists() and (id is 0):
                er_msg="This Register ID is already in use."
                return render(request,'admin_login.html',{'form':form,'er_msg':er_msg,'id':0,'details':details,'username':username})
            else:
                fname=form.cleaned_data['fname']
                lname=form.cleaned_data['lname']
                email=form.cleaned_data['email']
                if not (re.search(regex_1,email) or re.search(regex_2,email) ):
                    er_msg="Email is not written in proper manner."
                    return render(request,'admin_login.html',{'form':form,'er_msg':er_msg,'id':0,'details':details,'username':username})
                if Person.objects.filter(email=email).exists() and (id is 0):
                    er_msg="This Email is already in use."
                    return render(request,'admin_login.html',{'form':form,'er_msg':er_msg,'id':0,'details':details,'username':username})
                print("reg_id is :",reg_id)
                print("inst is :",inst)
                print("dept is :",dept)

                if id is not 0 and faculty_page_var!='1':
                    pk_=request.POST['id']
                    password=str(form.cleaned_data['password'])
                    print("pk : ", request.POST['id'])
                    pi=Person.objects.get(pk=pk_)
                    pi_str=str(pi)
                    values=[]
                    for word in set(pi_str.split()):
                        indexes = [w.start() for w in re.finditer("value", pi_str)]
                    indexes= [n+6 for n in indexes]
                    quote_index=[]
                    for index in indexes:
                        quote_index.append(pi_str.find('"',index+1))
                    
                    for i in range(len(indexes)):
                        values.append(pi_str[indexes[i]+1:quote_index[i]])
                    
                    if values[2]!=str(email):
                        if Person.objects.filter(email=email).exists():
                            er_msg="This Email is already in use."
                            return render(request,'admin_login.html',{'form':form,'er_msg':er_msg,'id':id,'details':details,'username':username})

                        letters = string.ascii_lowercase
                        result_str = ''.join(random.choice(letters) for i in range(6))
                        print("Random password is : ",result_str)  
                        
                        subject = 'Welcome to CHARUSAT Facial based Attendance System'
                        text = 'Hi '+fname+', Please keep your password : "'+result_str+'" remember for access your profile page.'
                        
                        #email
                        to=email
                        gmail_user='jp739709@gmail.com'
                        gmail_pwd='Indian02'
                        message='Subject : {}\n\n{}'.format(subject,text)
                        smtpserver=smtplib.SMTP('smtp.gmail.com',587)
                        smtpserver.ehlo()
                        smtpserver.starttls()
                        smtpserver.ehlo
                        smtpserver.login(gmail_user, gmail_pwd)
                        smtpserver.sendmail(gmail_user,to,message)
                        print("Done...")
                        smtpserver.close()

                        password=make_password(result_str,"a")
                    id=id+1
                    pi.delete()

                else:
                    if faculty_page_var!='1':
                        pass
                    letters = string.ascii_lowercase
                    result_str = ''.join(random.choice(letters) for i in range(6))
                    print("Random password is : ",result_str)  
                    
                    subject = 'Welcome to CHARUSAT Facial based Attendance System'
                    text = 'Hi '+fname+', Please keep your password : "'+result_str+'" remember for access your profile page.'
                  
                    #for email genration

                    to=email
                    gmail_user='jp739709@gmail.com'
                    gmail_pwd='Indian02'
                    message='Subject : {}\n\n{}'.format(subject,text)
                    smtpserver=smtplib.SMTP('smtp.gmail.com',587)
                    smtpserver.ehlo()
                    smtpserver.starttls()
                    smtpserver.ehlo
                    smtpserver.login(gmail_user, gmail_pwd)
                    smtpserver.sendmail(gmail_user,to,message)
                    print("Done...")
                    smtpserver.close()

                    password=make_password(result_str,"a")
                    # password=result_str

            if faculty_page_var!='1' and id is 0:
                reg=Person(fname=fname,lname=lname,email=email,password=password,inst=inst,dept=dept,reg_id=reg_id)
                reg.save()
                msg= 'Details of Faculty Saved Succesfully '
            #form=FacultyRegisteration()
            if faculty_page_var!='1' and id is not 0:
                reg=Person(fname=fname,lname=lname,email=email,password=password,inst=inst,dept=dept,reg_id=reg_id,is_pass_change=0)
                reg.save()
                msg= 'Details of Faculty Saved Succesfully '


            if faculty_page_var=='1':
                pk_=str(int(request.POST['id']))
                print("pk_ is : ",pk_)
                 
                attend=Attendance.objects.filter(reg_id=reg_id).filter(inst=inst).filter(dept=dept)
                fet_obj=Person.objects.get(pk=pk_)
                fet_obj.is_pass_change=False
                fet_obj.fname=fname
                fet_obj.lname=lname
                fet_obj.inst=inst
                fet_obj.dept=dept

                fet_obj.save()
                msg="Faculty Updated Successfully"
                name=str(fet_obj.fname)+" "+str(fet_obj.lname)
                return render(request,'faculty_update.html',{'form':form, 'id':pk_,'msg':msg,'name':name,'attend':attend,'username':username})

        else:
            er_msg="Some fields are need to fill up to save details"
            return render(request,'admin_login.html',{'form':form,'details':details,'er_msg':er_msg,'id':0,'username':username})
        


    return render(request,'admin_login.html',{'form':form,'msg':msg,'details':details,'id':id,'username':username})



def faculty_update(request,id):
    msg=None
    username=request.session['fetch_username']
    #print("username in admin_page is : ",username)
    print("Faculty updation is ongoing...")
    pi=Person.objects.get(pk=id)
    pi.is_pass_change=False
    details=Person.objects.all()
    fm=FacultyEdit(request.POST,instance=pi)
    if request.method=='POST':
        # print("Updated form is : ",fm.is_valid())
        # print("Update Form error is : ",fm.errors)
        if fm.is_valid():
            fm.save()
            msg='Faculty Updated Successfully'
            

        else:
            pi=Person.objects.get(pk=id)
            pi.is_pass_change=False
            fm=FacultyEdit(instance=pi)
            return render(request,'faculty_update.html',{'form':fm})
    return render(request,'admin_login.html',{'form':fm,'msg':msg,'details':details,'username':username})


def faculty_delete(request,id):
    username=request.session['fetch_username']
    #print("username in admin_page is : ",username)
    if request.method=='POST':
        pi=Person.objects.get(pk=id)
        pi_str=str(Person.objects.get(pk=id))
        values=[]
        for word in set(pi_str.split()):
            indexes = [w.start() for w in re.finditer("value", pi_str)]
        indexes= [n+6 for n in indexes]
        quote_index=[]
        for index in indexes:
            quote_index.append(pi_str.find('"',index+1))
        
        for i in range(len(indexes)):
            values.append(pi_str[indexes[i]+1:quote_index[i]])
        
        print("values[3] is inside faculty delete is : ",values[3])
        training_data_obj=TrainingData.objects.filter(reg_id=values[3])
        if training_data_obj:
            training_data_obj.delete()
            print("Deletion in faculty also delte training data as well.")
        attaendance_obj=Attendance.objects.filter(reg_id=values[3])
        if attaendance_obj:
            attaendance_obj.delete()
            print("Deletion in faculty also delete attendance data as well.")

        pi.delete()
        form=FacultyRegisteration()
        msg= 'Faculty Deleted Succesfully '
        details=Person.objects.all()
        return render(request,'admin_login.html',{'form':form,'del_msg':msg,'details':details,'id':0,'username':username})

def take_pic(request,det_msg=None):
    username=request.session['fetch_username']
    #print("username in admin_page is : ",username)
    form=FacultyRegisteration()
    details=Person.objects.all()
    str_msg=None
    reg_id=request.POST['reg_list']
    print(reg_id)  
    pi=str(Person.objects.get(reg_id=reg_id))
    values=[]
    for word in set(pi.split()):
        indexes = [w.start() for w in re.finditer("value", pi)]
    indexes= [n+6 for n in indexes]
    quote_index=[]
    for index in indexes:
        quote_index.append(pi.find('"',index+1))
    
    for i in range(len(indexes)):
        values.append(pi[indexes[i]+1:quote_index[i]])
    
    print("Value is : ",values)

    video = cv2.VideoCapture(0)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(base_dir,"{}\{}\{}\{}".format('static','TrainingImage',values[4],values[8] ))
    xml_dir=os.path.join(base_dir,"{}".format('static'))
    print("IMage path :",image_dir)
    print("XML path :",xml_dir)
    harcascadePath = xml_dir+"\haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    sampleNum = 0
    while True:	
        ret, img = video.read()
        small_frame = cv2.resize(img, (0,0), fx=0.5, fy= 0.5)
        rgb_small_frame = small_frame[:,:,::-1]
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(30,30),flags = cv2.CASCADE_SCALE_IMAGE)
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (10, 159, 255), 2)
            
            if sampleNum<=9:
                cv2.imwrite(image_dir+"\\" +reg_id + '.0' + str(sampleNum) + ".jpg", gray[y:y+h, x:x+w])
                
            else:
                cv2.imwrite(image_dir+"\\" +reg_id + '.' + str(sampleNum) + ".jpg", gray[y:y+h, x:x+w])
            
            
            #incrementing sample number
            sampleNum = sampleNum+1
        if sampleNum>99:
            str_msg="Images are stored..."
            break
        cv2.imshow("Face Training Panel",img)
        if cv2.waitKey(1) == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()
    TrainImages(request,reg_id)
    return render(request,'face_train.html',{'str_msg':str_msg,'det_msg':det_msg,'details':details,'username':username})




def TrainImages(request,reg_id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pi=str(Person.objects.get(reg_id=reg_id))
    values=[]
    for word in set(pi.split()):
        indexes = [w.start() for w in re.finditer("value", pi)]
    indexes= [n+6 for n in indexes]
    quote_index=[]
    for index in indexes:
        quote_index.append(pi.find('"',index+1))
    
    for i in range(len(indexes)):
        values.append(pi[indexes[i]+1:quote_index[i]])

    image_dir = os.path.join(base_dir,"{}\{}\{}\{}".format('static','TrainingImage',values[4],values[8]))
    fields=['ID','Array']
    known_face_names=[]
    known_face_encodings=[]
    for root,dirs,files in os.walk(image_dir):
        for file in files:
            if re.findall( ( "^"+str(reg_id)+".10.jpg" ),file):
                path = os.path.join(root, file)
                print("path is : ",path)
                img = face_recognition.load_image_file(path)
                print("img is : ",img)
                label = file[:len(file)-4]
                print("label is : ",label)
                try:
                    img_encoding = face_recognition.face_encodings(img)[0]
                    print("Training img is : ",img_encoding)
                    # rows=[[label,img_encoding]]
                    # with open('TrainingData.csv','a') as csvfile:
                    #     csvwriter=csv.writer(csvfile)
                    #     csvwriter.writerow(fields)
                    #     csvwriter.writerows(rows)
                    fet_train_obj=TrainingData.objects.filter(reg_id=reg_id)
                    fet_train_obj_str=" ".join([str(x) for x in fet_train_obj])
                    fet_train_obj_str_lis=fet_train_obj_str.split(' ')
                    
                    print("Fet_train id is : ",fet_train_obj_str_lis," with length : ",len(fet_train_obj_str_lis))
                    if len(fet_train_obj_str_lis)>1:
                        train_obj=TrainingData.objects.get(pk=fet_train_obj_str_lis[0])
                        train_obj.array=base64.b64encode(pickle.dumps(img_encoding))
                        train_obj.save()
                        print("Database row is updated.....")
                    else:
                        train_obj=TrainingData(reg_id=reg_id,array=base64.b64encode(pickle.dumps(img_encoding)))
                        train_obj.save()
                        print("Database row is inserted....")
                    known_face_names.append(label)
                    known_face_encodings.append(img_encoding)
                except IndexError as e:
                    take_pic(request,det_msg='Face Detection is not done succesfully, please try again')

                
    

def recognize(request):
    face_locations = []
    face_encodings = []
    values=[]
    names = []

    # fetch_face_names=[]
    # fetch_face_encodings=[]
    known_face_names=[]
    known_face_encodings=[]

    fet_train_obj=TrainingData.objects.all()
    # for obj in fet_train_obj:
    #     fetch_face_names.append(obj.reg_id)
    #     fetch_face_encodings.append(pickle.loads(base64.b64decode(obj.array)))

    for obj in fet_train_obj:
        known_face_names.append(obj.reg_id)
        known_face_encodings.append(pickle.loads(base64.b64decode(obj.array)))
    
    # for i in range(len(known_face_encodings)):
    #     print("known_face_encoding is : ",known_face_encodings[i])
    #     print("-------------------------------------")
    #     print("fetch_face_encoding is : ",fetch_face_encodings[i])
    #     temp1=np.array(known_face_encodings[i])
    #     temp2=np.array(fetch_face_encodings[i])
    #     comp=temp1==temp2
    #     print("Both arrays are equal :: ",comp.all())
    # rows=[]
    # with open('TrainingData.csv','r') as csvfile:
    #     csvreader=csv.reader(csvfile)
    #     fields=next(csvreader)
    #     for row in csvreader:
    #         rows.append(row)
        
                
        
    #     print("Excel Rows are : ",rows)
    ip, is_routable = get_client_ip(request)
    print("ip of client is in recognize : ",ip)
    video = cv2.VideoCapture(0)
    Timer_var=int(10)
    print("knonwn face names : ",known_face_names)
    print("known face encoding : ",known_face_encodings)
    while True and Timer_var>0:	
        check, frame = video.read()
        small_frame = cv2.resize(frame, (0,0), fx=0.5, fy= 0.5)
        rgb_small_frame = small_frame[:,:,::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        if len(face_locations)==0:
            prev=time.time()
            time.sleep(1)
            curr=time.time()
            # print("for timer, prev is : ",prev)
            # print("for timer, curr is : ",curr)
            if curr-prev>=1:
                prev=curr
                Timer_var=Timer_var-1
                print("Timer left to close is ",Timer_var," seconds...")
        else:
            Timer_var=10
        # print("Face location is : ",face_locations)
        print("Face encoding is : ",face_encodings)
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, np.array(face_encoding), tolerance = 0.6)
            face_distances = face_recognition.face_distance(known_face_encodings,face_encoding)	
            try:
                matches = face_recognition.compare_faces(known_face_encodings, np.array(face_encoding), tolerance = 0.6)
                face_distances = face_recognition.face_distance(known_face_encodings,face_encoding)
                print("matches is : ",matches)
                print("face_distances : ",face_distances[0])
                #to get accuracy
                if face_distances[0]>0.6:
                    # print("inside if of face_distances.....")
                    rg=0.4
                    linear_val=(1-face_distances[0])/(rg * 2)
                    answer=round(linear_val*100,2)
                    
                    if answer<40:
                        answer=round(answer*2.5,2)
                        

                    print("accuracy is in if: ",answer," with type : ",type(answer))
                else:
                    # print("inside else of face_distances......")
                    rg=0.6
                    linear_val=(1.0-face_distances[0])/(rg * 2.0)
                    answer= (round(linear_val + ( (1 - round(linear_val,2) ) * math.pow( abs(round(linear_val -0.5,2))* 2, 0.2 ) ),2) * 100 )+10
                    if answer>95:
                        answer-=6

                    print("answer value inside else : ",answer," with type : ",type(answer))


                best_match_index = np.argmin(face_distances[0])
                # print("Inside try, best_match_index is : ",best_match_index)
                for i in range(len(matches)):
                    if matches[i]:
                        name = known_face_names[i]
                        
                        name=str(name)
                        face_names.append(name)
                        if name not in names:
                            names.append(name)
            except:
                pass
        if len(face_names) == 0:
            for (top,right,bottom,left) in face_locations:
                top*=2
                right*=2
                bottom*=2
                left*=2
                cv2.rectangle(frame, (left,top),(right,bottom), (0,0,255), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, 'Unknown', (left, top), font, 0.8, (255,255,255),1)
        else:
            pi=str(Person.objects.get(reg_id=name))
                # print("Recognized Person object is : ",pi)
            for word in set(pi.split()):
                indexes = [w.start() for w in re.finditer("value", pi)]
            indexes= [n+6 for n in indexes]
            quote_index=[]
            for index in indexes:
                quote_index.append(pi.find('"',index+1))
            
            values=[]
            if name not in values:        
                for i in range(len(indexes)):
                    values.append(pi[indexes[i]+1:quote_index[i]])

            for (top,right,bottom,left), name in zip(face_locations, face_names):
                top*=2
                right*=2
                bottom*=2
                left*=2
                cv2.rectangle(frame, (left,top),(right,bottom), (0,255,0), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name+'-'+values[0]+' '+values[1]+' ('+str(answer)+'%)', (left, top), font, 0.8, (255,255,255),1)
            
                
                print("After recognizing data : ",values)
                final_value=[]
                ts=time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

                subject = 'Welcome to CHARUSAT Facial based Attendance System'
                to=values[2]
                gmail_user='jp739709@gmail.com'
                gmail_pwd='Indian02'
                attendance_obj=Attendance.objects.all()
                try:
                    in_time_obj=Attendance.objects.filter(reg_id=values[3]).filter(date=date)
                except:
                    in_time_obj=None

                
               
                if in_time_obj:
                    in_time_obj_str=" ".join([str(x) for x in in_time_obj])
                    in_time_obj_str_lis=in_time_obj_str.split(' ')
                    print("in time object is : ",in_time_obj," with length : ",len(in_time_obj))
                    print("int_time object pk is : ",in_time_obj_str_lis[0])
                    print("is_status variable value is : ",in_time_obj_str_lis[-4])
                    print("in_time column value is : ",in_time_obj_str_lis[5], " with type : ",type(in_time_obj_str_lis[5]))


                    if (str(in_time_obj_str_lis[-4]) == 'False'): 
                        fetch_obj=Attendance.objects.get(pk=in_time_obj_str_lis[0])
                        
                        tmp_intime_str=str(fetch_obj.in_time)
                        tmp_outtime_str=str(timeStamp)
                        tmp_date=str(fetch_obj.date)
                        if fetch_obj.is_leave and (str(in_time_obj_str_lis[5])=='None'):
                            print("inside if leave and in-punch...")
                            print("inside the in-punch if leave statements...")
                            fetch_obj.in_time=timeStamp
                            fetch_obj.is_status=1
                            fetch_obj.save()
                            text = 'Hi '+values[0]+' '+values[1]+' from Institue of '+values[4]+' and Department '+values[8]+' on Date '+date+', Your In-Time punch is taken at "'+timeStamp+'" .'

                            message='Subject : {}\n\n{}'.format(subject,text)
                            smtpserver=smtplib.SMTP('smtp.gmail.com',587)
                            smtpserver.ehlo()
                            smtpserver.starttls()
                            smtpserver.ehlo
                            smtpserver.login(gmail_user, gmail_pwd)
                            smtpserver.sendmail(gmail_user,to,message)
                            print("In punch email of leave is Done...")
                            smtpserver.close()

                        else:
                            fetch_obj.out_time=timeStamp
                            tdelta=datetime.datetime.strptime(tmp_outtime_str,'%H:%M:%S')-datetime.datetime.strptime(tmp_intime_str,'%H:%M:%S')
                            tdelta=str(tdelta)
                            ddetlta_in=tmp_date.split('-')
                            ddelta_today=date.split('-')
                            print("in_time is : ",tmp_intime_str, " and date is : ",fetch_obj.date," with type : ",type(fetch_obj.date))
                            print("out_time is : ",tmp_outtime_str, " and date is : ",date," with type : ",type(date))
                            print("difference between times is : ",tdelta," and class is : ",type(tdelta))
                            tdelta_lis=tdelta.split(':')
                            total_min=int(tdelta_lis[0])*60+int(tdelta_lis[1])
                            total_min=round(total_min/60,2)
                            print("difference between times in minutes is : ",total_min)
                            if fetch_obj.is_leave:
                                if fetch_obj.shift_leave=='2':
                                    total_min=7.50
                                else:
                                    total_min+=3.5
                        
                            if ddetlta_in[2]==ddelta_today[2]:
                                fetch_obj.total_hour=total_min
                            fetch_obj.is_status=1
                            fetch_obj.save()
                            text = 'Hi '+values[0]+' '+values[1]+' from Institue of '+in_time_obj_str_lis[2]+' and Department '+in_time_obj_str_lis[3]+' on Date '+in_time_obj_str_lis[4]+' having In-Time punch of '+in_time_obj_str_lis[5]+', Your Out-Time punch is taken at "'+timeStamp+'" with Total Working Hours is : '+str(total_min)+' .'

                            message='Subject : {}\n\n{}'.format(subject,text)
                            smtpserver=smtplib.SMTP('smtp.gmail.com',587)
                            smtpserver.ehlo()
                            smtpserver.starttls()
                            smtpserver.ehlo
                            smtpserver.login(gmail_user, gmail_pwd)
                            smtpserver.sendmail(gmail_user,to,message)
                            print("Out Punch email is Done...")
                            smtpserver.close()

                    else:
                        pass
                else:
                    print("inside the in-punch else statements...")
                    att_obj=Attendance(reg_id=values[3], inst=values[4], dept=values[8],date=date,in_time=timeStamp,is_status=1)
                    att_obj.save()
                    text = 'Hi '+values[0]+' '+values[1]+' from Institue of '+values[4]+' and Department '+values[8]+' on Date '+date+', Your In-Time punch is taken at "'+timeStamp+'" .'

                    message='Subject : {}\n\n{}'.format(subject,text)
                    smtpserver=smtplib.SMTP('smtp.gmail.com',587)
                    smtpserver.ehlo()
                    smtpserver.starttls()
                    smtpserver.ehlo
                    smtpserver.login(gmail_user, gmail_pwd)
                    smtpserver.sendmail(gmail_user,to,message)
                    print("In punch email is Done...")
                    smtpserver.close()



        cv2.imshow("Face Recognition Panel",frame)
        if cv2.waitKey(1) == ord('s'):
            break
    
    video.release()
    cv2.destroyAllWindows()
    qs_obj=Attendance.objects.all().update(is_status=0)
    print("status changed to 0 ...")
    
    return render(request,'main.html')


def logout(request):
    if request.session.get('fetch_username'):
        del request.session['fetch_username']
    return render(request,'main.html')

def faculty_login(request):
    message=None
    values=[]
    if request.method=='POST':
        rid=request.POST['fe_id']
        password=request.POST['fe_password']
        form=Person.objects.filter(reg_id=rid)
        key=Person.objects.values('id').get(reg_id=rid)['id']
        
        
        if len(form) is 0:
            message="No matching ID is found."
            return render(request,'main.html',{'message':message})
        pi=str(form)
        for word in set(pi.split()):
            indexes = [w.start() for w in re.finditer("value", pi)]
        indexes= [n+6 for n in indexes]
        quote_index=[]
        for index in indexes:
            quote_index.append(pi.find('"',index+1))

        if rid not in values:        
            for i in range(len(indexes)):
                values.append(pi[indexes[i]+1:quote_index[i]])

        print("inside faculty_login values is : ",values)
        request.session['fetch_username']=values[0]+" "+values[1]
        try:
            attend=Attendance.objects.filter(reg_id=rid).filter(inst=values[4]).filter(dept=values[8])
        except:
            attend=None
        

        pk=Person.objects.filter(reg_id=rid).filter(password=make_password(password,"a")).values('id')
       
        key=Person.objects.values('id').get(reg_id=rid)['id']
        
        first_pass_change=Person.objects.get(pk=key)
        
        if len(pk) is 1 and ( str(first_pass_change.is_pass_change) == 'True'):
            return render(request,"password_change.html",{'rid':rid,'id':key})
        if len(pk) is 1:
            form=Person.objects.get(pk=key)
            pi=str(Person.objects.get(pk=key))
            values=[]
            for word in set(pi.split()):
                indexes = [w.start() for w in re.finditer("value", pi)]
            indexes= [n+6 for n in indexes]
            quote_index=[]
            for index in indexes:
                quote_index.append(pi.find('"',index+1))
            
            for i in range(len(indexes)):
                values.append(pi[indexes[i]+1:quote_index[i]])

            print("values in faculty login is : ",values)
            name_str=values[0]+" "+values[1]
            form=FacultyEdit(instance=form)

            return render(request,'faculty_update.html',{'form':form, 'id':key,'attend':attend,'name':name_str})
        else:
            message='Username or Password is Invalid'
        
    
    return render(request,'main.html',{'message':message})

def pass_change(request,id):
    message=None
    form=None
    attend=None
    name_str=None
    rid=None
    if request.method=='POST':
        rid=request.POST['fe_id']
        password=request.POST['fe_password']
        key=request.POST['id']

        print("value of key in pass_change is : ",key)
        form=Person.objects.filter(reg_id=rid)
        
       
        pk=Person.objects.filter(reg_id=rid).values('id')
        key=Person.objects.values('id').get(reg_id=rid)['id']
        pi=str(Person.objects.get(pk=key))
        values=[]
        for word in set(pi.split()):
            indexes = [w.start() for w in re.finditer("value", pi)]
        indexes= [n+6 for n in indexes]
        quote_index=[]
        for index in indexes:
            quote_index.append(pi.find('"',index+1))
        
        for i in range(len(indexes)):
            values.append(pi[indexes[i]+1:quote_index[i]])

        print("values in faculty login is : ",values)
        name_str=values[0]+" "+values[1]
        try:
            attend=Attendance.objects.filter(reg_id=rid).filter(inst=values[4]).filter(dept=values[8])
        except:
            attend=None
        first_pass_change=Person.objects.get(pk=key)
        first_pass_change.password=make_password(password,"a")
        first_pass_change.is_pass_change=0
        first_pass_change.save()
        print("new password is saved inside database...")
        form=Person.objects.get(pk=key)
        form=FacultyRegisteration(instance=form)
    return render(request,'faculty_update.html',{'form':form,'attend':attend,'name':name_str,'rid':rid,'id':key})

def forget_pass_admin(request):
    message=None
    return render(request,'forget_pass_admin.html',{'message':message})

def forget_pass_admin_view(request):
    if request.method=='POST':
        email=request.POST['fe_email']
        Admin=get_user_model()
        try:
            admin=Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            admin=None
        print("fetched admin details is : ",admin)
        if admin:
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(6))
            print("Random password is : ",result_str)

            subject = 'Admin Side Password Request'
            text = 'Hey Admin, Please note down this code : "'+result_str+'" to create new password.'
           

            to=email
            gmail_user='jp739709@gmail.com'
            gmail_pwd='Indian02'
            message='Subject : {}\n\n{}'.format(subject,text)
            smtpserver=smtplib.SMTP('smtp.gmail.com',587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo
            smtpserver.login(gmail_user, gmail_pwd)
            smtpserver.sendmail(gmail_user,to,message)
            smtpserver.close()

            return render(request,'change_admin_pass.html',{'result_str':result_str,'email':email})
        else:
            message="This email address is not stored in Admin Database."
            return render(request,'forget_pass_admin.html',{'message':message})

def change_admin_pass(request):
    if request.method=='POST':
        email=request.POST['fe_email']
        code_enter=request.POST['fe_code']
        code_fetch=request.POST['email_code']
        password=request.POST['fe_password']
        print("Fetched code is : ",code_fetch," Enter code is : ",code_enter)
        if code_enter==code_fetch:
            Admin=get_user_model()
            admin=Admin.objects.get(email=email)
            admin.set_password(password)
            admin.save()
            print("Admin password is changed successfully...")
            msg="Admin password is changed successfully..."

        else:
            message="Entered Code is not matched with the emailed one."
            return render(request,'change_admin_pass.html',{'message':message,'email':email,'result_str':code_fetch})

    return render(request,"main.html",{'msg':msg})



def forget_pass(request):
    return render(request,'forget_pass.html')        

def forget_change_pass(request):
    message=None
    if request.method=='POST':
        email=request.POST['fe_email']
        regex_1 = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}\w+[.]\w{2,3}$'
        regex_2='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        print("fetched email for forget is :",email," and validation is : ",re.search(regex_1,email),re.search(regex_2,email))
        if re.search(regex_1,email) or re.search(regex_2,email):
            pi=Person.objects.filter(email=email).values('id')
            print("length of found pi is : ",len(pi)==0)
            if len(pi)==0:
                message="This Email address is not found in database."
                return render(request,'forget_pass.html',{'message':message})

            key=Person.objects.values('id').get(email=email)['id']
            pi=str(Person.objects.get(pk=key))
            values=[]
            for word in set(pi.split()):
                indexes = [w.start() for w in re.finditer("value", pi)]
            indexes= [n+6 for n in indexes]
            quote_index=[]
            for index in indexes:
                quote_index.append(pi.find('"',index+1))
            
            for i in range(len(indexes)):
                values.append(pi[indexes[i]+1:quote_index[i]])

            print("values in faculty login is : ",values)
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(6))
            print("Random password is : ",result_str)

            forget_pass_change=Person.objects.get(pk=key)
            forget_pass_change.password=make_password(result_str,"a")
            forget_pass_change.is_pass_change=1
            forget_pass_change.save()
            print("forgotten new password is saved inside database...")

            subject = 'Welcome to CHARUSAT Facial based Attendance System'
            text = 'Hi '+values[0]+', Please keep your password : "'+result_str+'" remember for access your profile page.'
            
            #for email
            to=email
            gmail_user='jp739709@gmail.com'
            gmail_pwd='Indian02'
            message='Subject : {}\n\n{}'.format(subject,text)
            smtpserver=smtplib.SMTP('smtp.gmail.com',587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo
            smtpserver.login(gmail_user, gmail_pwd)
            smtpserver.sendmail(gmail_user,to,message)
            smtpserver.close()

            message="New Password is sent in the Email."
            return render(request,'main.html',{'message':message})
        else:
            message="Email is not written in proper manner."
            return render(request,'forget_pass.html',{'message':message})
            

def search(request):
    # form=FacultyRegisteration()
    # details=Person.objects.all()
    username=request.session['fetch_username']
    #print("username in admin_page is : ",username)
    attendances = Attendance.objects.all()
    query_id=request.GET['reg_id']
    query_date=request.GET['f_date']
    query_inst=request.GET['f_inst']
    query_dept=request.GET['f_dept']
    month_name=[]
    if query_id is '' and query_date is '' and query_inst is '' and query_dept is '':
        print("1")
        pass
    if query_id is '' and query_date is '' and query_inst is '' and query_dept is not '':
        print("2")
        pass
    if query_id is '' and query_date is '' and query_inst is not '' and query_dept is '':
        print("3")
        attendances=Attendance.objects.filter(inst=query_inst)
    if query_id is '' and query_date is '' and query_inst is not '' and query_dept is not '':
        print("4")
        attendances=Attendance.objects.filter(inst=query_inst).filter(dept=query_dept)

        month_lis=attendances.values_list('date')
        id_lis=attendances.values_list('reg_id')
        total_hour_lis=attendances.values_list('total_hour')
        months=[]
        dates_lis=[]
        month_name=[]
        id_name=[]
        year_list=[]
        total_hour_list=[]
        ids_lis=[]
        
        for i in range(len(month_lis)):
            
            temp_str=''.join(str(month_lis[i]))
            index=temp_str.find(',',21)
            months.append(temp_str[21:index])

            temp_id=''.join(str(id_lis[i]))
            index=temp_id.find(',')
            id_name.append(int(temp_id[1:index]))

            index=temp_str.find(')')
            
            dates_lis.append(int(temp_str[23:index]))

            b_index=temp_str.find('(',1)+1
            e_index=temp_str.find(',',1)
            year_list.append(int(temp_str[b_index:e_index]))

            temp_total_hour=''.join(str(total_hour_lis[i]))
            b_index=temp_total_hour.find('(')+1
            e_index=temp_total_hour.find(',',1)
            if temp_total_hour[b_index:e_index]=='None':
                total_hour_list.append(temp_total_hour[b_index:e_index])
            else:
                total_hour_list.append(float(temp_total_hour[b_index:e_index]))

            
        ids_lis=id_name
        month_record_freq=collections.Counter(months)
        print("month counter record is : ",month_record_freq)
        print("Dates list is : ",dates_lis)
        print("months list is : ",months)
        print("Ids list is : ",ids_lis)
        print("Year list is : ",year_list)
        print("Total_hour list is : ",total_hour_list)
        merged_list = tuple(zip(ids_lis, dates_lis,total_hour_list))
        print("\n\nMereged List is : ",merged_list)
        months_set=[]
        [months_set.append(x) for x in months if x not in months_set]
        print("month is : ",months_set)
        id_name=set(id_name)
        id_name=list(id_name)
        month_dict={'1':'January','2':'February','3':'March','4':'April','5':'May','6':'June','7':'July','8':'August','9':'September','10':'October','11':'November','12':'December'}
        temp_key=list(month_dict.keys())
        temp_values=list(month_dict.values())
        month_counter_values=list(month_record_freq.values())
        for i in range(len(months_set)):
            month_name.append(temp_values[int(months_set[i])-1])
        
        res = defaultdict(list)

        for key,value,hour in merged_list:
            try:
                if hour=='None':
                    
                    pass
                elif hour>7.00:
                    
                    res[key].append(value)
                else:
                    
                    pass
            except KeyError:
                
                if hour>7.00:
                    res[key]=value
                else:
                    pass

        print("Dictinoary is : ",str(res))

        print("month counter values list is : ",month_counter_values)
        print("Month list is : ",months_set)
        print("Month Name list is : ",month_name)
        print("Id list is : ",id_name)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        excel_dir = os.path.join(base_dir,"{}\{}".format('static','Excel'))
        for i in range(len(month_name)):
            excel_path=excel_dir+"\\"+query_inst+"_"+query_dept+"_"+month_name[i]+".xlsx"
            print("Excel file worked is : ",excel_path)
            workbook=xlsxwriter.Workbook(excel_path)   
            ws=workbook.add_worksheet()
            ws.write('A1','Dates/Reg_ID',workbook.add_format({'bold': 1}))
            format1=workbook.add_format({'bg_color':'#FF0000'})
            format2=workbook.add_format({'bg_color':'#00FF00'})
            g_font=workbook.add_format({'font_color':'green'})
            r_font=workbook.add_format({'font_color':'red'})
            if month_name[i]=='January' or month_name[i]=='March' or month_name[i]=='May' or month_name[i]=='July' or month_name[i]=='August' or month_name[i]=='October' or month_name[i]=='December':
                ws.write_column('A2',(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31))
                ws.write('A34','Percentage (%)')
                if i==0:
                    for m in range(0,month_counter_values[i]):
                        id__name=ids_lis[0:month_counter_values[i]]
                        id__set=list(set(id__name))
                        print("id_name after dividing in months inside i=0 if for 31: ",id__set)
                        ids__lis=ids_lis[0:month_counter_values[i]]
                        dates__lis=dates_lis[0:month_counter_values[i]]
                        hours__lis=total_hour_list[0:month_counter_values[i]]
                        merged__list = tuple(zip(ids__lis, dates__lis,hours__lis))

                        print("\nids__lis is : ",ids__lis)
                        print("\ndates__lis is : ",dates__lis)
                        print("\nhours__lis is : ",hours__lis)
                        res_ = defaultdict(list)
                        for key,value,hour in merged__list:
                            try:
                                if hour=='None':
                                    
                                    pass
                                elif (hour)>7.00:
                                    
                                    res_[key].append(value)
                                else:
                                    
                                    pass
                        
                            except KeyError:
                                if hour>7.00:
                                    res_[key]=value
                                else:
                                    pass
                        print("Dictinoary after dividing in months inside i=0 if for 31: ",str(res_))
                        ws.write_row('B1',id__set,workbook.add_format({'bold': 1}))
                        for k in range(len(id__set)):
                            ws.write_column(chr(ord('B')+k)+'2',('A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A'),r_font)
                            present_lis=res_.get(id__set[k])
                            print("values after dividing in months inside i=0 if for 31: ",present_lis)
                            if present_lis is not None:
                                for j in range(len(present_lis)):
                                    ws.write(chr(ord('B')+k)+str(present_lis[j]+1),'P',g_font)
                                    ws.conditional_format(chr(ord('B')+k)+str(present_lis[j]+1), {'type':'icon_set','icon_style':'4_red_to_black'} )
                                
                                ws.write(chr(ord('B')+k)+str(34),round( (len(present_lis)/31) * 100 ,2))
                                
                            else:
                                ws.write(chr(ord('B')+k)+str(34),0)
                            ws.conditional_format( chr(ord('B')+k)+str(34), {'type':'cell','criteria':'>=','value':80,'format':format2} )
                            ws.conditional_format( chr(ord('B')+k)+str(34), {'type':'cell','criteria':'<','value':80,'format':format1} )


                else:
                    for m in range(month_counter_values[i-1],month_counter_values[i-1]+month_counter_values[i]):
                        id__name=ids_lis[month_counter_values[i-1]:month_counter_values[i-1]+month_counter_values[i]]
                        id__set=list(set(id__name))
                        print("id_name after dividing in months inside i!=0 else for 31: ",id__name)
                        ids__lis=ids_lis[month_counter_values[i-1]:month_counter_values[i-1]+month_counter_values[i]]
                        dates__lis=dates_lis[month_counter_values[i-1]:month_counter_values[i-1]+month_counter_values[i]]
                        hours__lis=total_hour_list[month_counter_values[i-1]:month_counter_values[i-1]+month_counter_values[i]]
                        merged__list = tuple(zip(ids__lis, dates__lis,hours__lis))
                        res_ = defaultdict(list)
                        for key,value,hour in merged__list:
                            try:
                                if hour=='None':
                                    pass
                                elif (hour)>7.00:
                                    res_[key].append(value)
                                else:
                                    pass

                            except KeyError:
                                if hour>7.00:
                                    res_[key]=value
                                else:
                                    pass
                        print("Dictinoary after dividing in months inside i!=0 else for 31: ",str(res_))
                        ws.write_row('B1',id__set,workbook.add_format({'bold': 1}))
                        for k in range(len(id__set)):
                            ws.write_column(chr(ord('B')+k)+'2',('A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A'),r_font)
                            present_lis=res_.get(id__set[k])
                            print("values after dividing in months inside i!=0 else for 31: ",present_lis)
                            if present_lis is not None:
                                for j in range(len(present_lis)):
                                    ws.write(chr(ord('B')+k)+str(present_lis[j]+1),'P',g_font)
                                
                                ws.write(chr(ord('B')+k)+str(34),round( (len(present_lis)/31) * 100 ,2))
                                
                            else:
                                ws.write(chr(ord('B')+k)+str(34),0)
                            ws.conditional_format( chr(ord('B')+k)+str(34), {'type':'cell','criteria':'>=','value':80,'format':format2} )
                            ws.conditional_format( chr(ord('B')+k)+str(34), {'type':'cell','criteria':'<','value':80,'format':format1} )

            if month_name[i]=='April' or month_name[i]=='June' or month_name[i]=='September' or month_name[i]=='November':
                ws.write_column('A2',(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30))
                ws.write('A33','Percentage (%)')
                if i==0:
                    for m in range(0,month_counter_values[i]):
                        ids__lis=ids_lis[0:month_counter_values[i]]
                        id__name=ids__lis[0:month_counter_values[i]]
                        id__set=list(set(id__name))
                        print("id_name after dividing in months inside i=0 if for 30: ",id__set)
                        dates__lis=dates_lis[0:month_counter_values[i]]
                        hours__lis=total_hour_list[0:month_counter_values[i]]
                        merged__list = tuple(zip(ids__lis, dates__lis,hours__lis))
                        res_ = defaultdict(list)
                        for key,value,hour in merged__list:
                            try:
                                if hour=='None':
                                    pass
                                elif (hour)>7.00:
                                    res_[key].append(value)
                                else:
                                    pass
                                
                            except KeyError:
                                if hour>7.00:
                                    res_[key]=value
                                else:
                                    pass
                        print("Dictinoary after dividing in months inside i=0 if for 30: ",str(res_))
                        ws.write_row('B1',id__set,workbook.add_format({'bold': 1}))
                        for k in range(len(id__set)):
                            ws.write_column(chr(ord('B')+k)+'2',('A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A'),r_font)
                            present_lis=res_.get(id__set[k])
                            print("values after dividing in months inside i=0 if for 30: ",present_lis)
                            if present_lis is not None:
                                for j in range(len(present_lis)):
                                    ws.write(chr(ord('B')+k)+str(present_lis[j]+1),'P',g_font)
                                
                                ws.write(chr(ord('B')+k)+str(33),round( (len(present_lis)/31) * 100 ,2))
                                
                            else:
                                ws.write(chr(ord('B')+k)+str(33),0)
                            
                            ws.conditional_format( chr(ord('B')+k)+str(33), {'type':'cell','criteria':'>=','value':80,'format':format2} )
                            ws.conditional_format( chr(ord('B')+k)+str(33), {'type':'cell','criteria':'<','value':80,'format':format1} )

                else:
                    for m in range(month_counter_values[i-1],month_counter_values[i-1]+month_counter_values[i]):
                        id__name=ids_lis[month_counter_values[i-1]:month_counter_values[i-1]+month_counter_values[i]]
                        id__set=list(set(id__name))
                        print("id_name after dividing in months inside i!=0 else for 30: ",id__set)
                        ids__lis=ids_lis[month_counter_values[i-1]:month_counter_values[i-1]+month_counter_values[i]]
                        dates__lis=dates_lis[month_counter_values[i-1]:month_counter_values[i-1]+month_counter_values[i]]
                        hours__lis=total_hour_list[month_counter_values[i-1]:month_counter_values[i-1]+month_counter_values[i]]
                        merged__list = tuple(zip(ids__lis, dates__lis,hours__lis))
                        res_ = defaultdict(list)
                        for key,value,hour in merged__list:
                            try:
                                if hour=='None':
                                    pass
                                elif (hour)>7.00:
                                    res_[key].append(value)
                                else:
                                    pass

                            except KeyError:
                                if hour>7.00:
                                    res_[key]=value
                                else:
                                    pass

                        print("Dictinoary after dividing in months inside i!=0 else for 30: ",str(res_))
                        ws.write_row('B1',id__set,workbook.add_format({'bold': 1}))
                        for k in range(len(id__set)):
                            ws.write_column(chr(ord('B')+k)+'2',('A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A'),r_font)
                            present_lis=res_.get(id__set[k])
                            print("values after dividing in months inside i!=0 else for 30: ",present_lis)
                            if present_lis is not None:
                                for j in range(len(present_lis)):
                                    ws.write(chr(ord('B')+k)+str(present_lis[j]+1),'P',g_font)
                                
                                ws.write(chr(ord('B')+k)+str(33),round( (len(present_lis)/31) * 100 ,2))
                                
                            else:
                                ws.write(chr(ord('B')+k)+str(33),0)
                            
                            ws.conditional_format( chr(ord('B')+k)+str(33), {'type':'cell','criteria':'>=','value':80,'format':format2} )
                            ws.conditional_format( chr(ord('B')+k)+str(33), {'type':'cell','criteria':'<','value':80,'format':format1} )

        
            workbook.close()






    if query_id is '' and query_date is not '' and query_inst is '' and query_dept is '':
        print("5")
        attendances=Attendance.objects.filter(date=query_date)
    if query_id is '' and query_date is not '' and query_inst is '' and query_dept is not '':
        print("6")
        attendances=Attendance.objects.filter(date=query_date)
    if query_id is '' and query_date is not '' and query_inst is not '' and query_dept is'':
        print("7")
        attendances=Attendance.objects.filter(date=query_date).filter(inst=query_inst)
    if query_id is  '' and query_date is not '' and query_inst is not '' and query_dept is not  '':
        print("8")
        attendances=Attendance.objects.filter(date=query_date).filter(inst=query_inst).filter(dept=query_dept)
    if query_id is not '' and query_date is '' and query_inst is '' and query_dept is  '':
        print("9")
        attendances=Attendance.objects.filter(reg_id=query_id)
    if query_id is not '' and query_date is '' and query_inst is '' and query_dept is not '':
        print("10")
        attendances=Attendance.objects.filter(reg_id=query_id)
    if query_id is not '' and query_date is '' and query_inst is not '' and query_dept is '':
        print("11")
        attendances=Attendance.objects.filter(reg_id=query_id).filter(inst=query_inst)
    if query_id is not '' and query_date is '' and query_inst is not '' and query_dept is not '':
        print("12")
        attendances=Attendance.objects.filter(reg_id=query_id).filter(inst=query_inst).filter(dept=query_dept)
    if query_id is not '' and query_date is not '' and query_inst is '' and query_dept is '':
        print("13")
        attendances=Attendance.objects.filter(reg_id=query_id).filter(date=query_date)
    if query_id is not '' and query_date is not '' and query_inst is '' and query_dept is not '':
        print("14")
        attendances=Attendance.objects.filter(reg_id=query_id).filter(date=query_date)
    if query_id is not '' and query_date is not '' and query_inst is not '' and query_dept is '':
        print("15")
        attendances=Attendance.objects.filter(reg_id=query_id).filter(date=query_date).filter(inst=query_inst)
    if query_id is not '' and query_date is not '' and query_inst is not '' and query_dept is not '':
        print("16")
        attendances=Attendance.objects.filter(reg_id=query_id).filter(date=query_date).filter(inst=query_inst).filter(dept=query_dept)

    # context = {'attend': attendances,'details':details,'form':form }
    return render(request, 'attendance.html',{'attend':attendances,'username':username,'month':month_name,'inst':query_inst,'dept':query_dept})

def search_faculty(request):
    form=FacultyRegisteration()
    details=Person.objects.all()
    attendances = Attendance.objects.all()
    query_date=request.GET['f_date']
    print("QueryDate is : ",query_date)
    if query_date is not '':
        attendances=Attendance.objects.filter(date=query_date)
    else:
        pass

    context = {'attend': attendances,'details':details,'form':form }
    return render(request, 'faculty_update.html', context)

def attendance(request):
    username=request.session['fetch_username']
    #print("username in admin_page is : ",username)
    attend=Attendance.objects.all()
     
    return render(request,'attendance.html',{'attend':attend,'username':username})


def pdf_report(request):

    if request.method == 'POST':
        base_dir = os.path.dirname(os.path.abspath(__file__))
        excel_dir = os.path.join(base_dir, "{}\{}".format('static', 'Excel'))

        month_name = request.POST["month_name_pdf"]
        month = month_name

        query_inst = request.POST ['f_inst']
        query_dept = request.POST ['f_dept']
        print("\n\n\n\n\n\n\nall that matters" + month_name + "\n\n\n\n\n\n\n")
        month_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7 :'July',
                      8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        for key, value in month_dict.items():
            if month_name == value:
                month_name = key



        attendances = Attendance.objects.filter(inst=query_inst).filter(dept=query_dept).filter(date__month=month_name)

        filename = excel_dir + "\\" + query_inst + "" + query_dept + "" + str(month) + ".pdf"

        response = HttpResponse(content_type='application/pdf')
        response ['Content-Disposition'] = 'attechment; filename=AttendanceReport'+ str(
            datetime.datetime.now()) + '.pdf'
        response ['Content-Transfer-Encoding'] = 'binary'
        html_string = render_to_string(
            'report_pdf.html', {'attend': attendances,'month_name':month,'dept':query_dept,'inst':query_inst , 'total': len(attendances)}
        )

        html = HTML(string=html_string)

        result = html.write_pdf()
        print("result is printed",result)

        with open(filename,'wb') as output:
            output.write(result)
            output.flush()

            output = open(output.name, 'rb')
            response.write(output.read())
            return response


def goto_chart_js(request):
    if request.method=='POST':
        # id_f=Attendance.objects.filter(reg_id=11).aggregate(Sum('total_hour'))
        this_month = request.POST["month_name_chart"]
        month_list = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July',
                      8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

        for key, value in month_list.items():
            if this_month == value:
                this_month = key

        print(this_month)
        labels = []
        data = []

        queryset = Attendance.objects.values('reg_id').annotate(total_hour=Sum('total_hour')).order_by(
            '-total_hour').filter(date__month=this_month)
        for entry in queryset:
            labels.append(entry ['reg_id'])
            data.append(entry ['total_hour'])

        # return JsonResponse(data={'labels': labels,'data': data,})

        # print(data)
        return render(request, 'chart.html', {'labels': labels, 'data': data, 'this_month': this_month})


def report(request):
    if request.method=='POST':
        base_dir = os.path.dirname(os.path.abspath(__file__))
        excel_dir = os.path.join(base_dir,"{}\{}".format('static','Excel'))
        month_name=request.POST['month_list']
        query_inst=request.POST['f_inst']
        query_dept=request.POST['f_dept']
        print("in report function inst and dept are : ",query_inst,query_dept) 
        print("fetched month_name is : ",month_name)
        filename=excel_dir+"\\"+query_inst+"_"+query_dept+"_"+month_name+".xlsx"
        print("filename is : ",filename)
        if os.path.exists(filename):
            print("inside if of exist...")
            with open(filename,'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' +query_inst+"_"+query_dept+"_"+ month_name+".xlsx"
                return response

def face_train(request):
    details=Person.objects.all()
    username=request.session['fetch_username']
    #print("username in admin_page is : ",username)
    return render(request,'face_train.html',{'details':details,'username':username})

def leave_page(request):
    details=Person.objects.all()
    username=request.session['fetch_username']
    return render(request,'leave_page.html',{'details':details})

def leave_grant(request):
    if request.method=='POST':
        details=Person.objects.all()
        fet_id=request.POST['reg_list']
        fet_date=datetime.datetime.strptime( str(request.POST['datefield']),'%Y-%m-%d' )
        fet_date=fet_date.date()
        
        fet_type=request.POST['type_leave']
        fet_shift=request.POST['type_shift']
        obj=str(Person.objects.filter(reg_id=fet_id))
        print("Date is : ",fet_date," with the type : ",type(fet_date))

        values=[]
        for word in set(obj.split()):
            indexes = [w.start() for w in re.finditer("value", obj)]
        indexes= [n+6 for n in indexes]
        quote_index=[]
        for index in indexes:
            quote_index.append(obj.find('"',index+1))
            
        for i in range(len(indexes)):
            values.append(obj[indexes[i]+1:quote_index[i]])
        
        attend_filter=Attendance.objects.filter(reg_id=fet_id).filter(date=fet_date)
        attend_filter_lis=str(attend_filter).split(" ")
        if attend_filter:
            print("first thing is : ",attend_filter_lis[2])
            attend_obj=Attendance.objects.get(pk=attend_filter_lis[2])
            if fet_shift=='2':
                attend_obj.total_hour=7.50
            else:
                attend_obj.total_hour=None
            attend_obj.is_leave=1
            attend_obj.type_leave=fet_type
            attend_obj.shift_leave=fet_shift
            attend_obj.save()
        else:
            if fet_shift=='2':
                attend=Attendance(reg_id=fet_id,inst=values[4],dept=values[8],date=fet_date,total_hour=7.50,is_leave=1,type_leave=fet_type,shift_leave=fet_shift)
                attend.save()
            else:
                attend=Attendance(reg_id=fet_id,inst=values[4],dept=values[8],date=fet_date,is_leave=1,type_leave=fet_type,shift_leave=fet_shift)
                attend.save()


        msg="Leave Granted to Faculty..."
    return render(request,'leave_page.html',{'details':details,'msg':msg})



class PersonListView(ListView):
    model = Person
    context_object_name = 'people'


class PersonCreateView(CreateView):
    model = Person
    form_class = FacultyRegisteration
    success_url = reverse_lazy('person_changelist')


class PersonUpdateView(UpdateView):
    model = Person
    form_class = FacultyRegisteration
    success_url = reverse_lazy('person_changelist')


def load_cities(request):
    country_id = request.GET.get('inst')
    cities = City.objects.filter(inst_id=country_id)
    return render(request, 'city_dropdown_list_options.html', {'cities': cities})