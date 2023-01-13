"""Tools related to assigning proposals to reviewers

In Pretalx assignments can be done in two directions:

 1. Assign proposals to reviewers
 2. Assign reviewers to proposals

We will always assume direction 1. in this file when we talk about an assignment.
So in Operation Research-speak, resources get assigned tasks, not the other way around.
The time needed for the task of reviewing a proposal is quite homogeneous while the number of reviews a single
reviewer may highly vary. Also, we will rather use the name submission instead of proposal as this also reflects
the naming of the Pretalx API.

We will use the following terminology:
 * sub(s): submission(s) equivalent to proposal(s)

"""
import json
from pathlib import Path
from typing import Iterator

import pandas as pd

from .pretalx.types import Submission


def read_assignment_as_df(file_path: Path) -> pd.DataFrame:
    """Reads an assignment and returns a dataframe"""
    with open(file_path) as fh:
        curr_assign = json.load(fh)
    df = pd.DataFrame({k: [v] for k, v in curr_assign.items()})
    df = df.T.rename_axis(index="email").rename(columns={0: "curr_subs"}).reset_index()
    return df


def sub_tracks_as_df(all_subs: Iterator[Submission]) -> pd.DataFrame:
    """Retrieves all submission and creates a dataframe of submission code and their tracks"""
    return (
        pd.DataFrame({s.code: [s.track.en] for s in all_subs}).T.rename(columns={0: "track"}).rename_axis(index="sub")
    )
