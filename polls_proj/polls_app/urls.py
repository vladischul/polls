from django.urls import path

from . import views

app_name = "polls_app"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path("polls/<int:pk>/", views.PollDetailView.as_view(), name="poll_detail"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('institute/<int:institute_id>/', views.InstituteView.as_view(), name='institute'),
]