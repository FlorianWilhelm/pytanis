# Pytanis

<div align="center">

<img src="https://raw.githubusercontent.com/FlorianWilhelm/pytanis/main/docs/assets/images/logo.svg" alt="Pytanis logo" width="500" role="img">

[Pytanis] provides useful tools for conferences using [Pretalx] to handle the call for papers and creating a program!

|         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CI/CD   | [![CI - Test](https://github.com/FlorianWilhelm/pytanis/actions/workflows/run-tests.yml/badge.svg)](https://github.com/FlorianWilhelm/pytanis/actions/workflows/run-tests.yml) [![Coverage](https://img.shields.io/coveralls/github/FlorianWilhelm/pytanis/main.svg?logo=coveralls&label=Coverage)](https://coveralls.io/r/FlorianWilhelm/pytanis) [![CD - Build](https://github.com/FlorianWilhelm/pytanis/actions/workflows/publish-pkg.yml/badge.svg)](https://github.com/FlorianWilhelm/pytanis/actions/workflows/publish-pkg.yml) [![Docs - Build](https://github.com/FlorianWilhelm/pytanis/actions/workflows/build-rel-docs.yml/badge.svg)](https://github.com/FlorianWilhelm/pytanis/actions/workflows/build-rel-docs.yml)                                                                                                            |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/pytanis.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/pytanis/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/pytanis.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pepy.tech/project/pytanis) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytanis.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/pytanis/)                                                                                                                                                                                                                                                                                                                                                                                        |
| Details | [![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/) [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![imports - isort](https://img.shields.io/badge/imports-isort-ef8336.svg)](https://github.com/pycqa/isort) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) [![GitHub Sponsors](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=ff69b4)](https://github.com/sponsors/FlorianWilhelm) |

</div>

-----

**Trivia**: The name *Pytanis* is a reference to [Prytanis] using the typical *py* prefix of [Python] tools. [Prytanis]
was the name given  to the leading members of the government of a city (polis) in ancient Greece.  Offices that used this
title usually had responsibility for presiding over councils of some kind, which met in the [Prytaneion].

**This is a pre-alpha version! Don't use it!**


## Features

- [x] simple configuration management with a config folder in your home directory, just like many other tools do
- [x] easily access [Google Sheets], potentially filled by some [Google Forms], and download it as DataFrame
- [x] easy to use [Pretalx] client that return proper Python objects thanks to the power of [pydantic]
- [x] simple [HelpDesk] client for batch mails, e.g. to your reviewers
- [ ] tools to assign proposals to reviewers based on constraints like preferences
- [ ] tools to support the final selection process of proposals
- [ ] tools to support the creation of the final program schedule
- [ ] awesome [documentation] with best practices for the program committee of any community conference



## Getting started

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



## Development

This section is only relevant if you want to contribute to Pytanis itself. Your help is highly appreciated!

After having cloned this repository:

1. install [hatch] globally, e.g. `pipx install hatch`,
2. create the default environment with `hatch env create`,
3. activate the default environment with `hatch shell`,
4. \[only once\] run `pre-commit install` to install [pre-commit],

and then you are already set up to start hacking. Use `hatch run test:cov` or `hatch run test:no-cov` to run
the unitest with or without coverage reports, respectively.

## Documentation

The [documentation] is made with [Material for MkDocs] and is hosted by [GitHub Pages]. Your help to extend the
documentation, especially in the context of using Pytanis for community conferences like [PyConDE], [EuroPython], etc.
is highly appreciated.

## License

Pytanis is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Credits

To start this project off a lot of inspiration and code was taken from [Alexander Hendorf] and [Matthias Hofmann].

[Pytanis]: https://florianwilhelm.info/pytanis/
[Python]: https://www.python.org/
[Pretalx]: https://pretalx.com/
[hatch]: https://hatch.pypa.io/
[pre-commit]: https://pre-commit.com/
[Prytanis]: https://en.wikipedia.org/wiki/Prytaneis
[Prytaneion]: https://en.wikipedia.org/wiki/Prytaneion
[Python Quickstart for the Google API]: https://developers.google.com/sheets/api/quickstart/python
[Pretalx API]: https://pretalx.com/api/events/
[documentation]: https://florianwilhelm.info/pytanis/
[Alexander Hendorf]: https://github.com/alanderex
[Matthias Hofmann]: https://github.com/mj-hofmann
[Google Forms]: https://www.google.com/forms/about/
[Google Sheets]: https://www.google.com/sheets/about/
[pydantic]: https://docs.pydantic.dev/
[HelpDesk]: https://www.helpdesk.com/
[Material for MkDocs]: https://github.com/squidfunk/mkdocs-material
[GitHub Pages]: https://docs.github.com/en/pages
[PyConDE]: https://pycon.de/
[EuroPython]: https://europython.eu/
