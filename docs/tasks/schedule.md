# Creating the Schedule

After all you talks and tutorials are confirmed, the next major milestone is to create a schedule so that each
talk gets a time and place to be presented. [Pretalx] allows you to create a schedule by dragging & dropping the talk
blocks onto a schedule, where you can define the number of days and rooms. You can also specify breaks like lunch or coffee breaks
and later on publish the schedule for everyone. So this feature is pretty need but for larger conferences with a lot of
parallel sessions, i.e. many rooms, some help might be needed.

Assuming that you had some blank schedule before that already defines the time slots with their lengths and when the
breaks are, then surely following constraints must be satisfied:

* each talk must be assigned to a time slot,
* each room/time slot combination can only be occupied by one talk at most,
* the length of the time slot must match the length of the talk,
* if some talks/tutorials have several parts, e.g. part 1 & 2, they must be consecutive.

Besides those constraints you might want to optimize for several objectives:

1. the preferences for day and time of the speakers are considered (if they provided some),
2. the more popular a talk is (from the public voting data), the more capacity the assigned room should have,
3. if many people are highly interested in seeing two talks (voting data), these talks should rather not be scheduled in parallel.
   Also, sponsored talks should never be in parallel to avoid cannibalization,
4. talks should have same main track, e.g. PyData, if they are in the same session (block of talks in one room),
5. talks should have same sub track, e.g. PyData: Data Handling, if they are in the same session.

The easiest way of dealing with multi-objective optimization is to create one new main objective by weighting and summing all objectives.
For the objectives outlined above, it surely makes sense to choose the weights so that the importance is 1 > 2 > 3 > 4 > 5.

In the notebook [50_scheduling_v1], you can find an example that uses [Mixed-Integer-Programming] (MIP) to generate a preliminary
schedule that can be used as a starting point before creating the schedule in Pretalx. Although the constraints and objective
from above may look quite simple, MIPs are not only hard, they are even [NP-hard] ;-) The example in the notebook uses
[Pyomo] to formulate the problem and transform it into a standardized form, so that the solver [HiGHS] can do its job.
In the concrete example, even after 24h no perfect solution was found, but the good thing is that the gap between best found feasible
solution and the maximum possible objective value, i.e. the gap, was relatively small.

Again, to visualize a solution like this, you can push it easily with the help of Pytanis to [Google Sheets],  which
is illustrated in the figure below.

<div align="center">
<img src="https://raw.githubusercontent.com/FlorianWilhelm/pytanis/main/docs/assets/images/gsheet_schedule.png" alt="Schedule view in Google Sheet" width="800" role="img">
</div>

!!! tip
    If you want to also specify [link previews], sometimes also called a social banners, then check out the notebook [40_talk_image_v1]
    on how Pytanis can help you to create them.

[link previews]: https://developers.facebook.com/docs/sharing/webmasters/images
[40_talk_image_v1]: https://github.com/FlorianWilhelm/pytanis/blob/main/notebooks/pyconde-pydata-berlin-2023/40_talk_image_v1.ipynb
[50_scheduling_v1]: https://github.com/FlorianWilhelm/pytanis/blob/main/notebooks/pyconde-pydata-berlin-2023/50_scheduling_v1.ipynb
[Pyomo]: http://www.pyomo.org/
[HiGHS]: https://highs.dev/
[Mixed-Integer-Programming]: https://en.wikipedia.org/wiki/Integer_programming
[NP-hard]: https://en.wikipedia.org/wiki/NP-hardness
