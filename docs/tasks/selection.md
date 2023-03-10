# The Selection Process

## Overview

On a high-level, the selection process involves the following

1. have an optional public voting for the proposals,
2. decide on how many talks, tutorials in which length, track or skill level you want to have,
3. get an overview of the proposals, the speakers, the reviewer scores, and optionally the vote scores,
4. select in Pretalx which talks are accepted and which ones are not.

## 1. Optional Public Voting

The [pretalx-public-voting] plugin allows to vote for the proposals which is a nice signal if a talk is generally interesting
to the audience or not, solely based on the title and abstract. If it is installed activate it in Pretalx under
<kbd>Settings</kbd> » <kbd>Public voting</kbd>. After the end date of the voting has passed this is also the place where you can
download the results as a csv file. Unfortunately, there is currently no API provided by Pretalx for this feature.

## 2. Decision on Number of Talks and Rules for Acceptance

Deciding on the rules of acceptance might be one of the hardest parts and no Software can support you with it. It is really
important to do this early on since it will help with the actual selection process. In order to decide for instance for the
number of talks/tutorials in various lengths, it's important to already have a blank schedule, i.e. just the time slots, at hand.
Diversity is also an important topic, so one rule might be to over-represent the under-represented but by how much?
And do you expect your audience to be rather advanced, even senior, and what does that mean for ratio of the various required
skill levels of the talks? How about the tracks you defined? Are speakers allowed to give more than one talk? How to deal
with talks that have been given before? It's best to decide on a few guidelines before you proceed with the next steps.

## 3. Overview of the proposals

Getting an overview of all proposals, their features, their review score and optionally their public score, is crucial
when it comes to make a selection. Luckily with the help of Pytanis this is really easy. You can pull all the data from
Pretalx, join it with additional data like the voting scores and push it to a [Google Sheet], where everyone can easily view it
and add comments. Find a practical example on how Pytanis was used for the PyConDE / PyData 2023 in this notebook [30_selection_v1].

## 4. Final Selection in Pretalx

Selecting the talks/tutorials for your conference is an iterative process. Maybe there are some talks you definitely want to
select and others so bad you surely want to reject. Then there might be some you want to preliminarily accept or reject.
Fortunately, [Pretalx] allows all that and Pytanis can pull that information to mark the rows in your GSheet with a certain colour.
Here is an example on how this might look like.

<div align="center">
<img src="https://raw.githubusercontent.com/FlorianWilhelm/pytanis/main/docs/assets/images/gsheet_proposal_selection.png" alt="Proposal selection in Google Sheet" width="800" role="img">
</div>

This example is also part of the notebook [30_selection_v1]. Also be aware that after you accepted a talk or tutorial the
author(s) must confirm. In practice, it happens also that accepted talks are withdrawn, so make sure you always keep a buffer
of talks that haven't gotten any feedback yet to be able to accept some more.

[30_selection_v1]: https://github.com/FlorianWilhelm/pytanis/blob/main/notebooks/pyconde-pydata-berlin-2023/30_selection_v1.ipynb
