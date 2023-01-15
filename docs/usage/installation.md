To install Pytanis simple run:
```commandline
pip install pytanis
```
and then create a file `~/.pytanis/config.toml` with the content:
```toml
[Pretalx]
api_token = "932ndsf9uk32nf9sdkn3454532nj32jn"

[Google]
client_secret_json = "client_secret.json"
token_json = "token.json"

[HelpDesk]
account = "934jcjkdf-39df-9df-93kf-934jfhuuij39fd"
entity_id = "email@host.com"
token = "dal:Sx4id934C3Y-X934jldjdfjk"
```
where you need to replace the dummy values in the sections `[Pretalx]` and `[HelpDesk]` accordingly.


### Retrieving the credentials and token
* **Google**: Follow the [Python Quickstart for the Google API] to generate and download the file `client_secret.json`.
Move it to the `~/.pytanis` folder as `client_secret.json`. The file `token.json` will be automatically generated
later. Note that `config.toml` references those two files relative to its own location.
* **Pretalx**: The API token for the [Pretalx API] can be found in your user settings.
* **HelpDesk**: Use the same (shared) email you use to log into HelpDesk/LiveChat to create the token following
 [this video](https://www.youtube.com/watch?v=-EUZ_Ynvz5Q&t=32s). In case there is any trouble with livechat,
  contact a helpdesk admin.
