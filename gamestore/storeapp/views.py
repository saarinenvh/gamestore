from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.views.generic import View
from .forms import UserForm
from .forms import manageGames
import json
from django.db.models.functions import Lower

# Imports for authentication
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

#Imports for SignUp
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView
from . import models
from hashlib import md5

from .models import game, player_game, highscore, saved_game, payment
#Imports for password change
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

from django.contrib.auth.models import Group
from django.db.models import Count, Sum

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


class UserSignUpView(View):
    form_class = UserForm
    template_name = 'signup.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid() and form.cleaned_data['password'] == form.cleaned_data['confirm_password']:
            user = form.save(commit = False)
            user.is_active = False
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data.get("confirm_password")
            developer = form.cleaned_data['developer']
            user.set_password(password)
            user.save()
            if developer:
                my_group = Group.objects.get(name='developer')
                my_group.user_set.add(user)

            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('email/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode,
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()

            return redirect('confirmEmail')

        elif form.data['password'] != form.data['confirm_password']:
            form.add_error('confirm_password', 'The passwords do not match')

        return render(request, self.template_name, {'form': form})

def confirmEmail(request):
    return render(request, 'email/confirm_email.html')

def successEmail(request):
    return render(request, 'email/email_success.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return redirect('successEmail')
    else:
        return HttpResponse('Activation link is invalid!')

class manageGamesView(View):
    form_class = manageGames
    template_name = 'manageGames.html'


    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form, 'method': 'Add'})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            maker = request.user
            url = form.cleaned_data['url']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            entry = models.game(name = name, maker = maker, url = url, price = price, description = description)
            entry.save()
            player_game = models.player_game(userID = maker.id, gameID = entry.id)
            player_game.save()
            return redirect('/dev/games')


        return render(request, self.template_name, {'form': form })



class GameUpdate(UpdateView):
    model = game
    fields = ['name', 'url', 'price', 'description']
    template_name = 'manageGames.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['method'] = 'Save'
        context['developer'] = self.get_object().maker
        return context


    def get_success_url(self):
        view_name = 'developer_games'
        return reverse_lazy(view_name)

class GameDelete(DeleteView):
    model = game
    success_url = reverse_lazy('developer_games')
    template_name = "_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        game = self.get_object()
        context['game'] = game
        context['user'] = user
        return context

def developerGames(request):
    game_list = game.objects.filter(maker = request.user.id).order_by(Lower('name'))
    sales = payment.objects.values('developer', 'amount', 'pid').annotate(count = Count('pid')).annotate(profit = Sum('amount'))
    totalProfit = payment.objects.filter(developer = request.user.id ).aggregate(Sum('amount'))
    count = total = payment.objects.filter(developer = request.user.id ).count
    return render(request, 'developergames.html', {'game_list': game_list, 'sales': sales, 'total': totalProfit, 'count': count})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/password/success')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        for field in form.fields.values():
            field.help_text = None
    return render(request, 'change_password.html', {
        'form': form
    })

def change_password_success(request):
    return render(request, 'change_psw_success.html')

#These generate different views.

def highscoreView(request):
    return render(request, 'highscore.html')

class GameListView(generic.ListView):
    model = game
    template_name = 'buygames.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        gameIDlist = player_game.objects.filter(userID = user.pk)
        gameIDlist = gameIDlist.values_list('gameID')
        allGames = game.objects.all().exclude(pk__in = gameIDlist).order_by(Lower('name'))
        context['gameslist'] = allGames
        return context

class GameDetailView(generic.DetailView):
    model = game
    template_name = 'game.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #data for purchase
        sid = "GameStore"
        pid = self.get_object().id
        amount = self.get_object().price
        secret_key = "58b7cd1de0e1a01b5bb90a8ccc82f651"
        checksumstr = "pid={}&sid={}&amount={}&token={}".format(pid, sid, amount, secret_key)
        m = md5(checksumstr.encode("ascii"))
        context['pid'] = pid
        context['sid'] = sid
        context['checksum'] = m.hexdigest()

        #data for playing
        context['owns'] = ownsGame(self.request.user.id, pid)
        return context

@login_required
def succesfullPayment(request):
    gameID = request.GET.get('pid')
    checksum = request.GET.get('checksum')
    buyedGame = game.objects.get(pk = gameID)
    user = request.user
    newPayment = models.payment(developer = buyedGame.maker.id, buyer = user.id, amount = buyedGame.price, pid = gameID, checksum = checksum)
    newPayment.save()
    saveGame = models.player_game(userID = request.user.id, gameID = gameID)
    saveGame.save()
    return render(request, 'payment/success.html')

def errorPayment(request):
    return render(request, 'payment/error.html')

def cancelPayment(request):

    return render(request, 'payment/cancel.html')


def ownsGame(playerID, gameID):
    try:
        player_game.objects.get(userID=playerID, gameID=gameID)
    except player_game.DoesNotExist:
        return False
    return True


@login_required
def playGamesView(request, gameID):
    if ownsGame(request.user.pk, gameID):
        gameObj = game.objects.get(pk = gameID)
        return render(request, 'playgames.html', {'game': gameObj})
    else:
        raise PermissionDenied

@login_required
def ownedGamesView(request):
    gameIDlist = player_game.objects.filter(userID = request.user.pk)
    gameIDlist = gameIDlist.values_list('gameID')
    games = game.objects.filter(pk__in=gameIDlist).order_by(Lower('name'))
    return render(request, 'owned_games.html', {'games': games})

@login_required
def gameMsgView(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
    elif request.method == 'GET':
        body = request.GET
    if not ownsGame(request.user.id, body['gameID']):
        raise PermissionDenied
    elif body['messageType'] == 'SCORE':
        newScore = highscore(playerID=request.user.pk, gameID=body['gameID'],
            score=body['score'])
        newScore.save()
        return HttpResponse('score received')
    elif body['messageType'] == 'SAVE':
        newSave = saved_game(player=request.user, game=game.objects.get(id=body['gameID']),
            saveData=json.dumps(body['gameState']), saveName=body['saveName'])
        newSave.save()
        return HttpResponse('game saved')
    elif body['messageType'] == 'LOAD_REQUEST':
        saves = game.objects.get(id=body['gameID']).saved_game_set.filter(player=request.user)
        return render(request, 'savepicker.html', {'saves': saves})
    elif body['messageType'] == 'LOAD_CHOSEN':
        gameState = saved_game.objects.get(id=body['saveID'], player=request.user,
            game=game.objects.get(id=body['gameID'])).saveData
        return HttpResponse(json.dumps(gameState))

def frontpage(request):
    return render(request, 'index.html')
