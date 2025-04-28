import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.utils.formats import date_format

from .models import Poll, Institute


class IndexPageTests(TestCase):
    def test_index_page_no_polls(self):
        """
        If no polls exist, an appropriate message is displayed on the index page.
        """
        response = self.client.get(reverse("polls_app:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls found.")
        self.assertQuerySetEqual(response.context["polls"], [])

    def test_index_page_with_polls(self):
        """
        The index page displays polls when they exist.
        """
        institute = Institute.objects.create(id=1, name="Test Institute")  # Provide an explicit ID
        poll = Poll.objects.create(
            institute=institute,
            pub_date=(timezone.now() - datetime.timedelta(days=1)).date()
        )
        response = self.client.get(reverse("polls_app:index"))
        formatted_date = date_format(poll.pub_date, "DATE_FORMAT")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"<strong>{poll.institute.name}</strong>")
        self.assertContains(response, f"Poll Date: {formatted_date}")

    def test_index_page_polls_order(self):
        """
        The index page displays the most recent poll for each institute in descending order of publication date.
        """
        institute1 = Institute.objects.create(id=1, name="Institute 1")
        institute2 = Institute.objects.create(id=2, name="Institute 2")
        poll1 = Poll.objects.create(
            institute=institute1,
            pub_date=(timezone.now() - datetime.timedelta(days=5)).date()
        )
        poll2 = Poll.objects.create(
            institute=institute1,
            pub_date=(timezone.now() - datetime.timedelta(days=1)).date()
        )
        poll3 = Poll.objects.create(
            institute=institute2,
            pub_date=(timezone.now() - datetime.timedelta(days=3)).date()
        )
        response = self.client.get(reverse("polls_app:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["polls"],
            [poll2, poll3],
            transform=lambda x: x
        )

    def test_index_page_carousel(self):
        """
        The index page includes a carousel for displaying polls.
        """
        institute = Institute.objects.create(id=1, name="Test Institute")
        poll = Poll.objects.create(
            institute=institute,
            pub_date=(timezone.now() - datetime.timedelta(days=1)).date()
        )
        response = self.client.get(reverse("polls_app:index"))
        formatted_date = date_format(poll.pub_date, "DATE_FORMAT")
        self.assertContains(response, 'id="pollCarousel"')
        self.assertContains(response, f"<h3 style=\"margin: 1%;\">{poll.institute.name} - Poll Date: {formatted_date}</h3>")