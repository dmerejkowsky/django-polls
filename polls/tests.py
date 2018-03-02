import datetime

from django.utils import timezone
from django.urls import reverse
import pytest

from .models import Question


def n_days_ago(n):
    return timezone.now() - datetime.timedelta(days=n)


def n_days_later(n):
    return timezone.now() + datetime.timedelta(days=n)


def test_was_published_recently_with_future_question():
    """
    was_published_recently() returns False for questions whose pub_date
    is in the future.
    """
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question('Back from the future', pub_date=time)
    assert not future_question.was_published_recently()


def test_was_published_recently_with_old_question():
    """
    was_published_recently() returns False for questions whose pub_date
    is older than 1 day.
    """
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    assert not old_question.was_published_recently()


def test_was_published_recently_with_recent_question():
    """
    was_published_recently() returns True for questions whose pub_date
    is within the last day.
    """
    time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    recent_question = Question(pub_date=time)
    assert recent_question.was_published_recently()


def create_question(question_text, *, pub_date=None):
    """
    Create a question with the given `question_text`.

    If `pub_date` is None, the question was published right, now.
    """
    if not pub_date:
        pub_date = timezone.now()
    res = Question.objects.create(question_text=question_text, pub_date=pub_date)
    return res


def get_latest_list(client):
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    return response.context['latest_question_list']


def assert_question_list_equals(actual_questions, expected_texts):
    assert len(actual_questions) == len(expected_texts)
    for actual_question, expected_text in zip(actual_questions, expected_texts):
        assert actual_question.question_text == expected_text


def assert_no_polls(text):
    assert "No polls are available." in text


def test_no_questions(client):
    """
    If no questions exist, an appropriate message is displayed.
    """
    response = client.get(reverse('polls:index'))
    assert_no_polls(response.rendered_content)

    latest_list = get_latest_list(client)
    assert not latest_list


@pytest.mark.django_db
def test_past_question(client):
    """
    Questions with a pub_date in the past are displayed on the
    index page.
    """
    create_question(question_text="Past question.", pub_date=n_days_ago(30))
    latest_list = get_latest_list(client)
    assert_question_list_equals(latest_list, ["Past question."])


@pytest.mark.django_db
def test_future_question(client):
    """
    Questions with a pub_date in the future aren't displayed on
    the index page.
    """
    create_question(question_text="Future question.", pub_date=n_days_later(30))
    response = client.get(reverse('polls:index'))
    assert_no_polls(response.rendered_content)
    latest_list = get_latest_list(client)
    assert not latest_list


@pytest.mark.django_db
def test_future_question_and_past_question(client):
    """
    Even if both past and future questions exist, only past questions
    are displayed.
    """
    create_question(question_text="Past question.", pub_date=n_days_ago(30))
    create_question(question_text="Future question.", pub_date=n_days_later(30))
    latest_list = get_latest_list(client)
    assert_question_list_equals(latest_list, ["Past question."])


@pytest.mark.django_db
def test_two_past_questions(client):
    """
    The questions index page may display multiple questions.
    """
    create_question(question_text="Past question 1.", pub_date=n_days_ago(30))
    create_question(question_text="Past question 2.", pub_date=n_days_ago(5))
    latest_list = get_latest_list(client)
    expected_texts = ["Past question 2.", "Past question 1."]
    assert_question_list_equals(latest_list, expected_texts)
