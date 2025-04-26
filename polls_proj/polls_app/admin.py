from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ("question_text", "pub_date", "was_published_recently")
    list_filter = ["pub_date"]
    search_fields = ["question_text"]
    list_per_page = 10
    date_hierarchy = "pub_date"
    ordering = ["-pub_date"]
    
    actions_on_top = True
    actions_on_bottom = False
    save_on_top = True
    save_on_bottom = False
    list_editable = ["pub_date"]
    list_display_links = ["question_text"]


admin.site.register(Question, QuestionAdmin)