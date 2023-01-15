import os
from textwrap import dedent

import pytest

from pytanis.helpdesk.mail import Mail, MailClient, Recipient


@pytest.mark.skipif(os.getenv('MAILTEST') is None, reason="people might get annoyed")
def test_sending_dummy_mail(tmp_config):
    # To actually test if this works, set the environment variable "NO_DRY_RUN" to 1.
    dry_run = os.getenv("NO_DRY_RUN") is None
    test_recipients = [
        Recipient(
            name="Florian Wilhelm", email="Florian.Wilhelm@gmail.com", address_as="Flo", data={"company": "inovex"}
        ),
    ]
    test_mail = Mail(
        subject="Pytanis API TEST: Ignore this message from {mail.data.me}",
        text=dedent(
            """
        Hello {recipient.address_as},

        this is an automated test message via our helpdesk using https://florianwilhelm.info/pytanis/!
        Looks like we are getting somewhere?

        Hope it's ok to call you {recipient.address_as} and not by your full {recipient.name}.
        Have you read the email's subject '{mail.subject}'?

        How is your work at {recipient.data.company}? We contact you because of a {mail.data.reason}!

        Cheers!
        """
        ),
        team_id="3f68251e-17e9-436f-90c3-c03b06a72472",  # Program
        agent_id="2d8b5727-49c8-410d-bae8-0da13a65609d",  # Program
        status="solved",
        recipients=test_recipients,
        data={"reason": "promotion", "me": "myself"},
    )

    client = MailClient()
    tickets, errors = client.send(test_mail, dry_run=dry_run)
    assert not errors
