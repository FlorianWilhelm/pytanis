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
from typing import Iterator, Union

import pandas as pd

from .pretalx.types import Submission


class Col:
    """Convention of column names for the functions below."""

    timestamp = "Timestamp"
    name = "Name"
    affiliation = "Affiliation"
    email = "Email"
    curr_assignments = "Current Assignments"
    num_assignments = "#Assignments"
    track = "Track"
    submission = "Submission"
    needed_nreviews = "Needed #Reviews"
    track_prefs = "Track Preferences"
    pretalx_activated = "Pretalx activated"
    committee_contact = "Committee Contact"
    availability = "Availability"
    availability_comment = "Availability Comment"
    all_proposals = "All Proposals"
    public = "Public"
    comment = "Comment"


def read_assignment_as_df(file_path: Path) -> pd.DataFrame:
    """Reads an assignment and returns a dataframe"""
    with open(file_path) as fh:
        curr_assign = json.load(fh)
    df = pd.DataFrame({k: [v] for k, v in curr_assign.items()})
    df = df.T.rename_axis(index=Col.email).rename(columns={0: Col.curr_assignments}).reset_index()
    return df


def sub_tracks_as_df(all_subs: Iterator[Submission]) -> pd.DataFrame:
    """Retrieves all submissions and creates a dataframe of submission codes and tracks"""
    return (
        pd.DataFrame({s.code: [s.track.en if s.track else "None"] for s in all_subs})
        .T.rename(columns={0: Col.track})
        .rename_axis(index=Col.submission)
    )


def save_assignments_as_json(df: pd.DataFrame, file_path: Union[Path, str]):
    """Save the dataframe as proposal assignment JSON file"""
    file_path = Path(file_path)
    df = df.loc[:, [Col.email, Col.curr_assignments]]
    json_dct = json.loads(df.set_index(Col.email).to_json())[Col.curr_assignments]
    # prettify the json string for human-edit-ability if reviewers need to be dropped later
    json_str = json.dumps(json_dct).replace("{", "{\n").replace("], ", "],\n").replace("]}", "]\n}")
    with open(file_path, "w") as fh:
        fh.write(json_str)
