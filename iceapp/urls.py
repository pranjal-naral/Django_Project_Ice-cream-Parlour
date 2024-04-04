from django.urls import path
from iceapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home',views.home),
    path('pdetails/<pid>',views.product_details),
    path('abt',views.about),
    path('contact',views.contact),
    path('register',views.register),
    path('login',views.ulogin),
    path('logout',views.ulogout),
    path('catfilter/<cv>',views.catfilter),
    path('sort/<sv>',views.sort),
    path('range',views.range),
    path('addtocart/<pid>',views.addtocart),
    path('remove/<cid>',views.remove),
    path('updateqty/<qv>/<cid>',views.updateqty),
    path('cart',views.cart),
    path('placeorder',views.placeorder),
    path('makepayment',views.makepayment),
    path('forget',views.forgetpassword)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

