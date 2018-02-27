"""gamestore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from storeapp import views

urlpatterns = [
    #Index
    path('', views.frontpage, name="index"),

    #Auth urls
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('signup/', views.UserSignUpView.as_view(), name='signup'),

    #Urls for managing and listing games
    path('games/', views.GameListView.as_view(), name='game-list'),
    path('games/<int:pk>', views.GameDetailView.as_view(), name='game-detail'),
    path('games/add/', views.manageGamesView.as_view(), name="add_game"),
    re_path('games/edit/(?P<pk>[0-9]+)/$', views.GameUpdate.as_view(), name = "update_game"),
    re_path('games/delete/(?P<pk>[0-9]+)/$', views.GameDelete.as_view(), name = "delete_game"),

    #Highscore view
    path('highscore/', views.userTopScores, name='highscore'),
    path('highscore/<int:gameID>', views.TopTenView.as_view(), name='topten'),

    #Play games view
    path('playgames/', views.ownedGamesView, name="ownedgames"),
    path('playgames/<int:gameID>', views.playGamesView, name="playgames"),

    #Lists developer games
    path('dev/games/', views.developerGames, name = 'developer_games'),

    #Game message view
    path('msg/', views.gameMsgView, name="gamemsg"),

    #Urls for changing password
    path('password/', views.change_password, name='change_password'),
    path('password/success', views.change_password_success, name='change_password_success'),

    #Urls for handling payments
    path('payment/success', views.succesfullPayment, name="paymentSuccess"),
    path('payment/error', views.errorPayment, name="paymentError"),
    path('payment/cancel', views.cancelPayment, name="paymentCancel"),

    #Urls for email confirmation
    path('email/confirm_email', views.confirmEmail, name="confirmEmail"),
    path('email/email_success', views.successEmail, name="successEmail"),
    re_path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    ]
