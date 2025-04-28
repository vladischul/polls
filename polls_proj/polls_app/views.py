from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.db.models import F, Q, Value, Max, Avg
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import requests 

from .models import Question, Choice, Poll, PollResult, Institute, Party

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "polls"
    
    def get(self, request, *args, **kwargs):
        latest_polls = Poll.objects.values('institute').annotate(latest_date=Max('pub_date')).order_by('-latest_date')
        polls = Poll.objects.filter(pub_date__in=[poll['latest_date'] for poll in latest_polls]).order_by('-pub_date').prefetch_related('pollresult_set')

        latest_question_list = Question.objects.order_by('-pub_date')[:5]

        return render(request, self.template_name, {
            'latest_question_list': latest_question_list,
            'polls': polls,
        })
    def get_queryset(self):
        return Poll.objects.order_by("-pub_date")

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

class PollDetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/poll_detail.html'
    context_object_name = 'poll'

    def get_context_data(self, **kwargs):
        """
        Fügt die Ergebnisse für die Poll zum Kontext hinzu.
        """
        context = super().get_context_data(**kwargs)
        poll = self.get_object()
        
        poll_results = PollResult.objects.filter(poll=poll)
        context['poll_results'] = poll_results
        
        return context

class InstituteView(generic.ListView):
    template_name = "polls/institute.html"
    context_object_name = "polls"

    def get_queryset(self):
        institute_id = self.kwargs['institute_id']
        return Poll.objects.filter(institute_id=institute_id).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['institute'] = get_object_or_404(Institute, pk=self.kwargs['institute_id'])
        return context

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls_app:results", args=(question.id,)))

