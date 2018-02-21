from django.contrib import admin

from .models import player_game
from .models import game
from .models import highscore
from .models import saved_game
from .models import payment


class gamesAdmin(admin.ModelAdmin):
    list_display =('name', 'id', 'name', 'maker')

class paymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'pid', 'developer', 'checksum')

class player_gameAdmin(admin.ModelAdmin):
    list_display = ('userID', 'gameID')

admin.site.register(player_game, player_gameAdmin)
admin.site.register(game, gamesAdmin)
admin.site.register(highscore)
admin.site.register(saved_game)
admin.site.register(payment, paymentAdmin)





# Register your models here.
