import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.utils.formats import date_format

from .models import Poll, Institute, Party, PollResult

# Tests ausführen mit: py manage.py test

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
        institute = Institute.objects.create(id=1, name="Test Institute")
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


class PollDetailViewTests(TestCase):
    def setUp(self):
        self.institute = Institute.objects.create(id=1, name="Test Institute")
        self.poll = Poll.objects.create(
            institute=self.institute,
            pub_date=(timezone.now() - datetime.timedelta(days=1)).date()
        )
        self.party1 = Party.objects.create(id=1, name="AfD", shortcut="AfD", color="#000000")
        self.party2 = Party.objects.create(id=2, name="SPD", shortcut="SPD", color="#DC0000")
        PollResult.objects.create(poll=self.poll, party=self.party1, percentage=30)
        PollResult.objects.create(poll=self.poll, party=self.party2, percentage=25)

    def test_poll_detail_view_status_code(self):
        url = reverse("polls_app:poll_detail", args=[self.poll.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_poll_detail_view_context(self):
        url = reverse("polls_app:poll_detail", args=[self.poll.id])
        response = self.client.get(url)
        self.assertEqual(response.context["poll"], self.poll)
        poll_results = response.context["poll_results"]
        self.assertEqual(poll_results.count(), 2)
        self.assertQuerySetEqual(
            poll_results.order_by("party__name"),
            PollResult.objects.filter(poll=self.poll).order_by("party__name"),
            transform=lambda x: x
        )

    def test_poll_detail_view_content(self):
        url = reverse("polls_app:poll_detail", args=[self.poll.id])
        response = self.client.get(url)
        self.assertContains(response, self.institute.name)
        formatted_date = date_format(self.poll.pub_date, format='DATE_FORMAT', use_l10n=True)
        self.assertContains(response, f"veröffentlicht: {formatted_date}")
        self.assertContains(response, "AfD: 30,0%")
        self.assertContains(response, "SPD: 25,0%")

    def test_poll_detail_view_404(self):
        url = reverse("polls_app:poll_detail", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)