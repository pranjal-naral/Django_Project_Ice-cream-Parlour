from django.shortcuts import render,HttpResponse,redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from iceapp.models import Product,Cart,Order
from django.db.models import Q
import random
import razorpay
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

# Create your views here.
def home(request):
    #userid=request.user.id
    #print(userid)
    #print("result:",request.user.is_authenticated)
    context={}
    p=Product.objects.filter(is_active=True)
    print(p)
    context['products']=p
    return render(request,'index.html',context)
    
def product_details(request):
    return render(request,'product_details.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

def register(request):
    context={}
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        upsc=request.POST['upsc']
        if uname=="" or upass=="" or upsc=="":
            context['errormsg']="Field cannot be empty"
            return render(request,'register.html',context)
        elif upass != upsc:
            context['errormsg']="password is incorrect"
            return render(request,'register.html',context)

        else:
            try:
                u=User.objects.create(username=uname,password=upass)
                u.set_password(upass)
                u.save()
                context['success']="account created"
                return render(request,'register.html',context)
            except Exception:
                context['errormsg']="User name already exist"
                return render(request,'register.html',context)
            #return HttpResponse("user created successfully")
    else:
        return render(request,'register.html')
    
def ulogin(request):
    context={}
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        if uname=="" or upass=="":
            context['errormsg']="Field cannot be empty"
            return render(request,'login.html',context)  
        else:
            u=authenticate(username=uname,password=upass)  
            if u is not None:
                login(request,u)
                return redirect("/home")
            else:
                context['errormsg']="Invalid username and password"
                return render(request,'logon.html',context)
    else:
        return render(request,'login.html',context)
    
def ulogout(request):
    logout(request)
    return redirect('/home')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=Product.objects.filter(q1 & q2)
    print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def sort(request,sv):
    if sv == '0':
        col = 'price'
    else:
        col = '-price'    
    p=Product.objects.filter(is_active=True).order_by(col)
   # print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['umin']
    max=request.GET['umax']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=Product.objects.filter(q1 & q2 & q3)
   # print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        u=User.objects.filter(id=userid)
        print(u[0])
        p=Product.objects.filter(id=pid)
        print(p[0])
        c=Cart.objects.create(uid=u[0],pid=p[0])
        c.save()
        return HttpResponse("id fetched")
        # print(userid)
        # print(pid)
    else:
        return redirect('/register')
    
def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    oid=random.randrange(1000,9999)
    print("order",oid)
    for x in c:
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    order=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(c)
    for x in c:
        # print(x)
        # print(x.pid.price)
        s=s+x.pid.price * x.qty
        context={}
        context['n']=np
        context['products']=c
        context['total']=s
    return render(request,'placeorder.html',context)
    # return HttpResponse("in placeorder")
    return render(request,'placeorder.html')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    if qv=='1':
        t=c[0].qty+1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty-1
            c.update(qty=t)
    return redirect('/cart')

def cart(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    s=0
    np=len(c)
    for x in c:
        # print(x)
        # print(x.pid.price)
        s=s+x.pid.price * x.qty
        context={}
        context['n']=np
        context['products']=c
        context['total']=s
    return render(request,'cart.html',context)


def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/cart')

def product_details(request,pid):
    context={}
    context['products']=Product.objects.filter(id=pid)
    return render(request,'product_details.html',context)

    #return HttpResponse('value fetched')

def makepayment(request):
    order=Order.objects.filter(uid=request.user.id)
    s=0
    for x in order:
        s=s+x.pid.price * x.qty
        oid=x.order_id
    
    client = razorpay.Client(auth=("rzp_test_Oj35p5VVY0WGz0", "Xyj0kbVQ0JGB3AFYAJZzwtSv"))
    data = { "amount": s*100, "currency": "INR", "receipt": "oid" }
    payment = client.order.create(data=data)
    print(payment)
    context={}
    context['data']=payment
    return render(request,'pay.html',context)

def forgetpassword(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        new_password = request.POST.get('upass')
        confirm_password = request.POST.get('upsc')

        user = User.objects.filter(username=username).first()

        if user:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()

                # Update the session to avoid automatic logout
                update_session_auth_hash(request, user)

                messages.success(request, 'Password reset successfully!')
                return redirect('/login')  # Redirect to login page after successful password reset
            else:
                messages.error(request, 'Passwords do not match.')
        else:
            messages.error(request, 'User not found.')
    return render(request,'forget.html')
        



