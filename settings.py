from os import environ
from os import popen


SESSION_CONFIGS = [
    dict(
        name='TPP',
        display_name="Third party punishment game",
        app_sequence=['baseline_trials'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
    dict(
        name='dice',
        display_name="Dice task",
        app_sequence=['dice_task'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
    dict(
        name='rule',
        display_name="Anti-social rule following",
        app_sequence=['rule_following', 'demographics'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
dict(
        name='crowding',
        display_name="Crowding-out",
        app_sequence=['crowding_out'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc=""
)

PARTICIPANT_FIELDS = ['dictator_country', 'receiver_country', 'progress', 'treatment_incentive', 'treatment_cond_coop']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

#DEBUG = False

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo',
         display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'C&C'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '8876387233144'

INSTALLED_APPS = ['otree']
