from os import environ
from os import popen


SESSION_CONFIGS = [
    dict(
        name='all_games',
        display_name="Complete study with all extra tasks",
        app_sequence=['baseline_trials', 'pref_2PP_3PP', 'rule_following', 'crowding_out', 'dice_task', 'free_rider', 'demographics'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
    dict(
        name='TPP',
        display_name="Third party punishment game",
        app_sequence=['baseline_trials'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
    dict(
        name='extras',
        display_name="All extra tasks",
        app_sequence=['pref_2PP_3PP', 'rule_following', 'crowding_out', 'dice_task', 'free_rider', 'demographics'],
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
    dict(
        name='pref_2PP_3PP',
        display_name="Preference for 2PP versus 3PP",
        app_sequence=['pref_2PP_3PP'],
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
        app_sequence=['rule_following'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
    dict(
        name='narratives',
        display_name="Free rider narratives",
        app_sequence=['free_rider'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip()
    ),
    dict(
        name='demographics',
        display_name="demographics only",
        app_sequence=['demographics'],
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
    real_world_currency_per_point=0.33,
    participation_fee=7.50,
    total_pages=336,
    doc=""
)

PARTICIPANT_FIELDS = ['language', 'current_country', 'current_countryname', 'dictator_country', 'receiver_country', 'progress', 'decision_page_number',
                      'treatment_incentive', 'treatment_cond_coop', 'pref_2PP_3PP_button_pos', 'crowding_out_button_pos']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'


# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
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
