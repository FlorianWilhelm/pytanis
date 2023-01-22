"""Tools related to assigning proposals to reviewers

In Pretalx assignments can be done in two directions:

 1. Assign proposals to reviewers
 2. Assign reviewers to proposals

We will always assume direction 1. in this file when we talk about an assignment.
So in Operation Research-speak, resources get assigned tasks, not the other way around.
The time needed for the task of reviewing a proposal is quite homogeneous while the number of reviews a single
reviewer may highly vary. Also, we will rather use the name submission instead of proposal as this also reflects
the naming of the Pretalx API.

We follow the convention over configuration principle here and thus check out the `Col` class for the naming of
columns.
"""
import json
from pathlib import Path
from typing import Iterable, Union

import pandas as pd

from .pretalx.types import Review, Speaker, Submission


class Col:
    """Convention of column names for the functions below."""

    created = "Created"
    name = "Name"
    title = "Title"
    address_as = "Address as"
    affiliation = "Affiliation"
    email = "Email"
    curr_assignments = "Current Assignments"
    nassignments = "#Assignments"
    track = "Track"
    submission = "Submission"
    target_nreviews = "Target #Reviews"
    rem_nreviews = "Remaining #Reviews"
    done_nreviews = "Done #Reviews"
    nreviews = "#Reviews"
    track_prefs = "Track Preferences"
    pretalx_activated = "Pretalx activated"
    pretalx_user = "Pretalx user"
    committee_contact = "Committee Contact"
    availability = "Availability"
    availability_comment = "Availability Comment"
    all_proposals = "All Proposals"
    public = "Public"
    comment = "Comment"
    speaker_code = "Speaker code"
    speaker_name = "Speaker name"
    biography = "Biography"
    duration = "Duration"
    submission_type = "Submission type"
    submission_type_id = "Submission type id"
    state = "State"
    pending_state = "Pending state"
    review_score = "Review Score"
    vote_score = "Vote Score"
    nvotes = "#Votes"


def read_assignment_as_df(file_path: Path) -> pd.DataFrame:
    """Reads an assignment and returns a dataframe"""
    with open(file_path) as fh:
        curr_assign = json.load(fh)
    df = pd.DataFrame({k: [v] for k, v in curr_assign.items()})
    df = df.T.rename_axis(index=Col.email).rename(columns={0: Col.curr_assignments}).reset_index()
    return df


def subs_as_df(subs: Iterable[Submission], with_questions: bool = False, question_prefix: str = "Q: ") -> pd.DataFrame:
    """Convert submissions into a dataframe

    Make sure to have `params={"questions": "all"}` for the PretalxAPI if `with_questions` is True.
    """
    rows = []
    for sub in subs:
        row = {
            Col.submission: sub.code,
            Col.title: sub.title,
            Col.track: sub.track.en if sub.track else None,
            Col.speaker_code: [speaker.code for speaker in sub.speakers],
            Col.speaker_name: [speaker.name for speaker in sub.speakers],
            Col.duration: sub.duration,
            Col.submission_type: sub.submission_type.en,
            Col.submission_type_id: sub.submission_type_id,
            Col.state: sub.state,
            Col.pending_state: sub.pending_state,
            Col.created: sub.created,
        }
        if with_questions and sub.answers is not None:
            for answer in sub.answers:
                row[f"{question_prefix}{answer.question.question.en}"] = answer.answer
        rows.append(row)
    return pd.DataFrame(rows)


def speakers_as_df(
    speakers: Iterable[Speaker], with_questions: bool = False, question_prefix: str = "Q: "
) -> pd.DataFrame:
    """Convert speakers into a dataframe

    Make sure to have `params={"questions": "all"}` for the PretalxAPI if `with_questions` is True.
    """
    rows = []
    for speaker in speakers:
        row = {
            Col.speaker_code: speaker.code,
            Col.speaker_name: speaker.name,
            Col.email: speaker.email,
            Col.biography: speaker.biography,
            Col.submission: speaker.submissions,
        }
        if with_questions and speaker.answers is not None:
            for answer in speaker.answers:
                # The API returns also questions that are 'per proposal/submission', we get these using the
                # submission endpoint and don't want them here due to ambiguity if several submission were made.
                if answer.person is not None:
                    row[f"{question_prefix}{answer.question.question.en}"] = answer.answer
        rows.append(row)
    return pd.DataFrame(rows)


def reviews_as_df(reviews: Iterable[Review]) -> pd.DataFrame:
    """Convert the reviews to a dataframe"""
    df = pd.DataFrame([review.dict() for review in reviews])
    df.rename(columns={"user": Col.name, "score": Col.review_score}, inplace=True)  # name is the key we can join on
    # make first letter of column upper-case in accordance with our convention
    df.rename(columns={col: col.title() for col in df.columns}, inplace=True)

    return df


def save_assignments_as_json(df: pd.DataFrame, file_path: Union[Path, str]):
    """Save the dataframe as proposal assignment JSON file"""
    file_path = Path(file_path)
    df = df.loc[:, [Col.email, Col.curr_assignments]]
    json_dct = json.loads(df.set_index(Col.email).to_json())[Col.curr_assignments]
    # prettify the json string for human-edit-ability if reviewers need to be dropped later
    json_str = json.dumps(json_dct).replace("{", "{\n").replace("], ", "],\n").replace("]}", "]\n}")
    with open(file_path, "w") as fh:
        fh.write(json_str)
