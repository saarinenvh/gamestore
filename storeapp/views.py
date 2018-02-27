from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden

from django.views.generic import View
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView

from django.db.models.functions import Lower
from django.db.models import Q
from django.db.models import Count, Sum

from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage

from django.urls import reverse_lazy, reverse

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token

from hashlib import md5
import json

from .forms import UserForm, manageGames
from . import models
from .models import game, player_game, highscore, saved_game, payment


#View for signup
class UserSignUpView(View):
    form_class = UserForm
    template_name = 'signup.html'

    #Renders signup form on get request
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    #Post messages signup information to database
    def post(self, request):
        form = self.form_class(request.POST)

        #Check if form is valid
        if form.is_valid() and form.cleaned_data['password'] == form.cleaned_data['confirm_password']:

            #Dont send data before its cleaned
            user = form.save(commit = False)

            #Disable user, active after email confirmation
            user.is_active = False

            #Check the form and save user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data.get("confirm_password")
            developer = form.cleaned_data['developer']
            user.set_password(password)
            user.save()

            #Add user to developer group, if box is checked
            if developer:
                my_group = Group.objects.get(name='developer')
                my_group.user_set.add(user)

            #Email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your Game Store -account.'

            #Render message to user
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

#View for email confirmation
def confirmEmail(request):
    return render(request, 'email/confirm_email.html')

#View for succesfully confirmed eamil
def successEmail(request):
    return render(request, 'email/email_success.html')

#Activates account after email confirmation
def activate(request, uidb64, token):

    #Check if uid is correct
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    #Activate user, if token checks
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
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
            player_game = models.player_game(userID = maker.id, gameID = entry)
            player_game.save()
            return redirect('/dev/games')

        return render(request, self.template_name, {'form': form })

#View for updating game information
class GameUpdate(UpdateView):
    model = game
    fields = ['name', 'url', 'price', 'description']
    template_name = 'manageGames.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Shows in template save-mode
        context['method'] = 'Save'
        context['developer'] = self.get_object().maker
        return context

    def get_success_url(self):
        view_name = 'developer_games'
        return reverse_lazy(view_name)

#View for deleting games
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

#Lists games that developer has added
def developerGames(request):
    game_list = game.objects.filter(maker = request.user.id).order_by(Lower('name'))

    #Queryset for every individual game
    sales = payment.objects.values('developer', 'amount', 'pid').annotate(count = Count('pid')).annotate(profit = Sum('amount'))

    #Total sales
    totalProfit = payment.objects.filter(developer = request.user.id ).aggregate(Sum('amount'))

    #Total payments
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
def userTopScores(request):
    gameIDlist = ownedGamesList(request.user.pk)
    games = []
    for gameID in gameIDlist:
        obj = {}
        obj['name'] = game.objects.get(pk = gameID).name
        obj['gameID'] = gameID
        scoreset = highscore.objects.filter(gameID = gameID).order_by('-score', 'playerID')
        try:
            obj['topscore'] = scoreset.first().score
        except AttributeError:
            obj['topscore'] = None
        try:
            obj['ownbest'] = scoreset.filter(playerID = request.user.pk).first().score
        except AttributeError:
            obj['ownbest'] = None
        games.append(obj)
    return render(request, 'usertopscores.html', {'games': games})

class TopTenView(generic.ListView):
    model = highscore
    template_name = 'topten.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scoreset = highscore.objects.filter(gameID = self.kwargs['gameID']).order_by('-score', 'playerID')
        topranks = 10
        if self.request.user.is_authenticated:
            owntop = scoreset.filter(playerID = self.request.user.pk).first()
            if (owntop != None):
                context['hasScores'] = True
                Qcheck = Q(score__gt = owntop.score) | (Q(score = owntop.score) & Q(playerID__lt = self.request.user.pk))
                ownrank = scoreset.filter(Qcheck).count() + 1
                if ownrank > 10 and ownrank <= 13:
                    topranks = ownrank
                if ownrank > 13:
                    context['competitors'] = scoreset[ownrank - 3:ownrank].values()
                    i = -2
                    for score in context['competitors']:
                        score['rank'] = i + ownrank
                        i += 1
                        score['player'] = User.objects.get(pk = score['playerID']).username
        j = 1
        context['topscores'] = scoreset[:topranks].values()
        for score in context['topscores']:
            score['rank'] = j
            j += 1
            score['player'] = User.objects.get(pk = score['playerID']).username
        context['gamename'] = game.objects.get(pk = self.kwargs['gameID']).name
        return context

#View that renders games in alphabetical order
class GameListView(generic.ListView):
    model = game
    template_name = 'buygames.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        gameIDlist = ownedGamesList(user.pk)
        allGames = game.objects.all().exclude(pk__in = gameIDlist).order_by(Lower('name'))
        context['gameslist'] = allGames
        return context

#Detail view for individual game, purchase can be done in this view
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


#Payment was successfully, payment object is created
@login_required
def succesfullPayment(request):
    gameID = request.GET.get('pid')
    checksumGet = request.GET.get('checksum')
    buyedGame = game.objects.get(pk = gameID)
    user = request.user
    if len(payment.objects.filter(checksum = checksumGet)) == 0:
        newPayment = models.payment(developer = buyedGame.maker.id, buyer = user.id, amount = buyedGame.price, pid = gameID, checksum = checksumGet)
        newPayment.save()
        saveGame = models.player_game(userID = request.user.id, gameID = buyedGame)
        saveGame.save()
    else:
        return redirect('paymentError')

    return render(request, 'payment/success.html')

#Render error pages if there where any errors during payment
def errorPayment(request):
    return render(request, 'payment/error.html')

#Render payment cancel page
def cancelPayment(request):
    return render(request, 'payment/cancel.html')

def ownsGame(playerID, gameID):
    try:
        player_game.objects.get(userID=playerID, gameID=gameID)
    except player_game.DoesNotExist:
        return False
    return True

def ownedGamesList(playerID):
    gameIDlist = player_game.objects.filter(userID = playerID)
    gameIDlist = gameIDlist.values_list('gameID')
    return list(map(lambda x: x[0], gameIDlist))

@login_required
def playGamesView(request, gameID):
    if ownsGame(request.user.pk, gameID):
        gameObj = game.objects.get(pk = gameID)
        return render(request, 'playgames.html', {'game': gameObj})
    else:
        raise PermissionDenied

@login_required
def ownedGamesView(request):
    gameIDlist = ownedGamesList(request.user.pk)
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
