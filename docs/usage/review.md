# The Review Process

On a high-level, the review process of the proposals for a conference works like that:

1. finding external reviewers and learning about their preferences,
2. onboarding reviewers in [Pretalx],
3. assign proposals to reviewers according to their preferences,
4. communicate with the reviewers occasionally for updates,
5. track the whole process.

## Finding external Reviewers and learning about their preferences

For the PyConDE / PyData Berlin 2023, we were looking for about 50 external reviewers since we expected about 400
proposals, and we wanted to have 3 reviews per proposal. This would amount to about 25 proposals to review per person
and still manageable within a few weeks if you schedule 5-15 minutes per proposal.

To get external reviewers, we would only ask within our circle of trust and refer them to some [Google Forms]. This
basically consisted of following questions with descriptions:

* **Name** \[short answer\]: Please write your name starting with your first name, e.g. Albert Einstein.
* **Affiliation** \[short answer\]: Please state the name or organisation you are affiliated with.
* **Who do you know from the Committee?** \[short answer\]: We believe in the ring of trust model. With this question, we really only
  want to make sure that not random people sign up with no connection to any member of the Program Committee at all.
* **Availability during the Review Period** \[checkboxes]: The bulk of the review work will take place from January 5th to February
  13th, 2023, so it is important that you are broadly available during this period. That being said, you will be quite
  flexible in managing your time but being on vacation with no internet for 3 weeks might be suboptimal here ;-)
  *There was only one mandatory checkbox: Yes, I am broadly available during this period.*
* **Additional comments regarding your availability during the review period.** \[long answer\]
* **Topics you want to review**: These are the topics you are interested in reviewing. The more you select the better.
  Don't be shy, you don't have to be an expert in a topic to review a proposal. If you are interested in a topic and
  have some knowledge about it, you are totally up for the job :-)
  *Each track in Pretalx corresponded to one checkbox in this form. At least 5 preferences needed to be chosen.*
* **Do you want your name to be listed as a reviewer on the conference website?** \[checkbox\] *Mandatory yes/no checkboxes*
* **Any additional comments for the Program Committee** \[long answer\]

!!! tip
    * [Google Form] will use the separator `, ` (comma, whitespace) for the selected checkboxes. Having the same separator
      in your track name, e.g. "General: Community, Diversity, Career, Life and everything else", will make it a bit harder
      to parse the resulting [Google Sheet]. So it's better to avoid them in track names.
    * Depending on how you want to assign proposals to reviewers later, it might also make sense to ask the reviewers if
      they only want to be assigned a single batch, or if they are also interested in getting more proposals to review after
      their batch is done.

Every submission of the Google Form is then automatically added to a Google Sheet, let's call it *volunteer sheet*, which can be easily read with the
help of Pytanis. It's as simple as:
```python
from pytanis import GSheetClient

gsheet_client = GSheetClient()
gsheet_df = gsheet_client.gsheet_as_df(SPREADSHEET_ID, WORKSHEET_NAME)
```
where `SPREADSHEET_ID` is the ID taken from the spreadsheet's url, e.g. the ID is `17juVXM7V3p7Fgfi-9WkwPlMAYJB-DuxRhYCi_hastbB`
if your spreadsheet's url is `https://docs.google.com/spreadsheets/d/17juVXM7V3p7Fgfi-9WkwPlMAYJB-DuxRhYCi_hastbB/edit#gid=1289752230`,
and `WORKSHEET_NAME` is the name of the actual sheet, e.g. `Form responses 1`, that you find in the lower bar of your
spreadsheet. Check out [Pytanis' google module](../../reference/pytanis/google/#pytanis.google) to learn about more functionality.

## Onboarding Reviewers in Pretalx

In Pretalx select in the left menu bar <kbd>Organisers</kbd> (you need Admin-rights for that) and click the <kbd>teams</kbd> under your event name.
You should see a list of all teams and is good to have one for all reviewers, e.g. `2023-Reviewers-ALL`. By clicking on the team name
get to a page that lists the names and corresponding e-mails of team members as well as an option to add new members at the bottom.

You can now start typing in the e-mail addresses from the volunteer sheet to send out invitations to them. After the accepted
the invitation they will show up with a user-name and e-mail in the team table above. Now, here comes the tricky part that can
cause a lot of confusion. If person A entered in the Google Form the e-mail address work@mail.com, and you added this in Pretalx,
it might happen that person A accepts the team invitation with a different Pretalx account that is linked to the e-mail
address private@mail.com. In this case Pretalx will automatically replace work@mail.com, which was used for the invitation,
with private@mail.com in the Pretalx table of team members.
Unfortunately, Pretalx has no way of automatically tracking this change of mail addresses and this issue [#1417] is still unresolved.

To work around it and to be able to later join your volunteer sheet for instance with reviews it makes sense to introduce
a new column, e.g. "Pretalx mail", where you add the actual Pretalx account e-mail that was used by the invited user.
Additionally, you should have a column for the Pretalx user-name, e.g. "Pretalx user", where you state the user-name
by copying it over from the Pretalx team member table. The is actually the column we can later use to join our reviewer volunteers
with the reviews they did as the [review-endpoint] of Pretalx only returns the user-name, not the e-mail of a reviewer.
This problem was also discussed in [#1416] and is an intended behaviour.

## Assign proposals to reviewers according to their preferences

## Communicate with the reviewers occasionally for updates

## Track the whole process


[#1417]: https://github.com/pretalx/pretalx/issues/1417
[#1416]: https://github.com/pretalx/pretalx/issues/1416
[review-endpoint]: https://docs.pretalx.org/api/resources/reviews.html
