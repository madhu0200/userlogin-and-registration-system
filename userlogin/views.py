from django.shortcuts import render

# Create your views here.
import smtplib
import ssl

from Tools.scripts import generate_token
from django.shortcuts import render,redirect
from django.http import HttpResponse
# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from .models import *
from django.contrib.sites.shortcuts import get_current_site


class usersession:
    def getuser(self,request):

        if request.session.has_key('email') :
            email=request.session['email']
            print('------email---------',email)
            if email is not None:
                myuser=customer.objects.filter(email=email).first()
                print(myuser)
                if myuser is not None:
                    return myuser
        return None

class register(View,usersession):

    def getOTP(self,email):
        import random
        otp=random.randint(100000,999999)
        userotp.objects.create(email=email,otp=otp)
        return otp

    def getdate(self):
        from datetime import date
        today = date.today()
        d1 = today.strftime("%d%m%Y")
        return d1

    def get(self,request):
        u=usersession()
        user=u.getuser(request)
        print(user)
        if user:
            messages.success(request,'you are already signed in')
            return render(request,'dashboard.html',{'user':user})
        else:
            return render(request,'register.html')
    def post(self,request):
        first_name=request.POST.get('first name')
        first_name=first_name.strip()
        last_name=request.POST.get('last name')
        last_name=last_name.strip()
        phone=request.POST.get('mobile_no')
        #print('phone',phone,first_name,last_name)
        email=request.POST.get('email')
        dob=request.POST.get('dob')
        password=request.POST.get('password')
        password2=request.POST.get('password2')
        username=first_name.lower()+last_name.lower()+phone[:5]+self.getdate()
        #messages.warning()
        #myuser = User.objects.create_user(username,email,password)
        # myuser.first_name=first_name
        # myuser.last_name=last_name
        # myuser.email=email
        # myuser.is_active=False
        myuser=customer.objects.create(username=username,first_name=first_name,last_name=last_name,mobile=phone,is_active=False,dob=dob,password=password,email=email)



        ###################################################################################################
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        sender_email = "djangoprojects7@gmail.com"
        password = "mkicixgcxifwrrnq"
        receiver_email = email
        current_site = get_current_site(request)
        message2 = render_to_string('email_confirmation.html',{
            'username':myuser.username,
            'name': myuser.first_name,
            'domain': current_site.domain,
            'otp': self.getOTP(email),

        })
        # Create a secure SSL context
        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            # TODO: Send email here
            server.sendmail(sender_email, receiver_email, message2)
            myuser.save()
        except Exception as e:
            print(e)
        finally:
            server.quit()


        if myuser:
            return render(request,'emailsend.html',{'email':email})
        else:
            return HttpResponse('error')

class signin(View,usersession):

    def get(self,request):
        user = usersession().getuser(request)
        if user:
            return render(request, 'dashboard.html', {'user': user})
        else:
            return render(request,'signin.html')
    def post(self,request):
        myuser = usersession().getuser(request)
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password,myuser)
        if myuser is not None:
            u=customer.objects.filter(email=email).first()
            request.session['email']=email
            usersession().getuser(request)
            print(myuser)
            return render(request,'dashboard.html',{'user':myuser})


        #exist_user=authenticate(request,email=email,password=password)
        exist_user=customer.objects.filter(email=email).first()
        print(exist_user)
        if exist_user is not None:
            #login(request,myuser)
            request.session['email'] = email
            return render(request, 'dashboard.html', {'user': exist_user})
        else:
            return HttpResponse("hiii")


class signout(View):
    def get(self,request):

        if request.session.has_key('email'):
            del request.session['email']
        return redirect('signin')
    def post(self,request):
        if request.session.has_key('username'):
            del request.session['username']
        return redirect('signin')


class otp(View):
    def post(self,request):
        email=request.POST.get('email')
        otp=request.POST.get('otp')
        print(email,otp)
        otpuser=userotp.objects.filter(email=email).first()
        print(otpuser.otp)
        if otpuser.otp==int(otp):
            otpuser.delete()
            myuser=customer.objects.filter(email=email).first()
            myuser.is_active=True
            myuser.save()
            request.session['email']=email
            return redirect('/signin')
        else:
            messages.warning(request,'enter correct otp')
            return render(request,'emailsend.html',{'email':email})

class changepassword(View):
    def get(self,request):
        return render(request,'changepassword.html')

    def post(self,request):
        myuser = usersession().getuser(request)
        if myuser is not None:
            email=myuser.email
            password=request.POST.get('password')
            password2=request.POST.get('password2')
            print(password,password2)
            if password==password2:
                myuser=customer.objects.filter(email=email).first()
                myuser.password=password
                myuser.save()
                messages.success(request,'your password is success fully updated')
                return render(request, 'dashboard.html', {'user': myuser})
            else:
                messages.warning(request,'passwords are not matching ')
                return render(request,'signin.html',{'user':myuser})
        else:
            messages.warning(request,'some error occured ! login again to continue')
            return HttpResponse("no")





