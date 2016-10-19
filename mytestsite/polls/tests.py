from django.test import TestCase
import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from .models import Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


# Create your tests here.
class QuestionViewTests(TestCase):
    def test_index_view_with_no_question(self):
        """
        If no question exist an appropriate message should be displayed
        :return:
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question(self):
        create_question('Future', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.', status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_past_question(self):
        create_question('Past', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past>'])

    def test_index_view_with_future_and_past_question(self):
        create_question('Past', days=-30)
        create_question('Future', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past>'])

    def test_index_view_with_two_future_question(self):
        create_question('Future', days=30)
        create_question('Future', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.', status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_two_past_question(self):
        create_question('Past1', days=-30)
        create_question('Past2', days=-15)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past2>', '<Question: Past1>'])


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_past_question(self):
        past_question = create_question('Past', days=-15)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)

    def test_detail_view_with_future_question(self):
        future_question = create_question('Future', days=15)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)


class QuestionIndexResultTests(TestCase):
    def test_result_view_with_past_question(self):
        past_question = create_question('Past', days=-15)
        response = self.client.get(reverse('polls:result', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)

    def test_result_view_with_future_question(self):
        future_question = create_question('Future', days=15)
        response = self.client.get(reverse('polls:result', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)


class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than one day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose
        pub_date is within a last day .
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), True)
