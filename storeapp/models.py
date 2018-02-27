from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class game(models.Model):
    name = models.CharField(max_length = 255)
    maker = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    price = models.FloatField()
    description = models.TextField()

    def get_absolute_url(self):
        return reverse('game-detail', args=[str(self.id)])

    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]
        
class player_game(models.Model):
    userID = models.IntegerField()
    gameID = models.ForeignKey(game, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.userID)
    class Meta:
        ordering = ["userID"]

class highscore(models.Model):
    playerID = models.IntegerField()
    gameID = models.IntegerField()
    score = models.IntegerField()

    def __str__(self):
        return "player: " + str(self.playerID) + " game: " + str(self.gameID) + " s: " + str(self.score)
    class Meta:
        ordering = ["playerID"]

class saved_game(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(game, on_delete=models.CASCADE)
    saveData = models.TextField()
    saveName = models.CharField(max_length = 255, null=True)

    def __str__(self):
        return str(self.player) + " " + str(self.game)

class payment(models.Model):
    developer = models.IntegerField()
    buyer = models.IntegerField()
    amount = models.FloatField()
    pid = models.IntegerField()
    checksum = models.CharField(max_length = 255)
