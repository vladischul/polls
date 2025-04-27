from django.db import models
from django.utils import timezone
from django.contrib import admin
import datetime


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text
    
    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
    
class Institute(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

class Party(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    shortcut = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name
    

class Poll(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    pub_date = models.DateField()

    def __str__(self):
        return f"{self.institute.name} - {self.pub_date}"



class PollResult(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    percentage = models.FloatField()