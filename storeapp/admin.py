from django.contrib import admin
from .models import player_game, game, highscore, saved_game, payment

#Admin site tools for testing

class gamesAdmin(admin.ModelAdmin):
    list_display =('name', 'id', 'name', 'maker')

class paymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'pid', 'developer', 'checksum')

admin.site.register(player_game)
admin.site.register(game, gamesAdmin)
admin.site.register(highscore)
admin.site.register(saved_game)
admin.site.register(payment, paymentAdmin)
