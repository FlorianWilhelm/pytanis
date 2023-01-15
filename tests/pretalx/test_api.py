"""These tests will only run if you have set up an Pretalx Account"""
import os
from datetime import date

import pytest

EVENT_SLUG = "pyconde-pydata-berlin-2023"


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_me_endpoint(pretalx_api):
    me = pretalx_api.me()
    assert me.name == "Florian Wilhelm"


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_events_endpoint(pretalx_api):
    count, all_events = pretalx_api.events()
    assert count == len(list(all_events))


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_event_endpoint(pretalx_api):
    event = pretalx_api.event(EVENT_SLUG)
    assert event.date_from == date.fromisoformat('2023-04-17')


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_submissions_endpoint(pretalx_api):
    count, subs = pretalx_api.submissions(EVENT_SLUG)
    assert count == len(list(subs))


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_submission_endpoint(pretalx_api):
    sub = pretalx_api.submission(EVENT_SLUG, 'MD9SLQ')
    assert sub.submission_type.en == 'Talk'


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_talks_endpoint(pretalx_api):
    count, talks = pretalx_api.talks(EVENT_SLUG)
    assert count == len(list(talks))


# ToDo: Add check for single speaker too


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_speakers_endpoint(pretalx_api):
    count, speakers = pretalx_api.speakers(EVENT_SLUG)
    assert count == len(list(speakers))


# ToDo: Add check for single speaker too


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_reviews_endpoint(pretalx_api):
    count, reviews = pretalx_api.reviews(EVENT_SLUG)
    assert count == len(list(reviews))


# ToDo: Add check for single review too


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_rooms_endpoint(pretalx_api):
    count, rooms = pretalx_api.rooms(EVENT_SLUG)
    assert count == len(list(rooms))


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_room_endpoint(pretalx_api):
    room = pretalx_api.room(EVENT_SLUG, 1882)
    assert room.name.en == 'B09'


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_questions_endpoint(pretalx_api):
    count, questions = pretalx_api.questions(EVENT_SLUG)
    assert count == len(list(questions))


# ToDo: Add check for single question too


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_answers_endpoint(pretalx_api):
    count, answers = pretalx_api.answers(EVENT_SLUG)
    assert count == len(list(answers))


# ToDo: Add check for single answer too


@pytest.mark.skipif(os.getenv('GITHUB'), reason="on Github")
def test_tags_endpoint(pretalx_api):
    count, tags = pretalx_api.tags(EVENT_SLUG)
    assert count == len(list(tags))


# ToDo: Add check for single tag too
