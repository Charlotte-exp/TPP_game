from os import environ
from os import popen

COUNTRIES = ['dz', 'ar', 'au', 'bo', 'br', 'bg', 'ca', 'cl', 'cn', 'co', 'cr', 'hr', 'do', 'ec', 'eg', 'sv', 'fi', 'fr', 'de', 'gr', 'gt', 'hu', 'in', 'id', 'it', 'jp', 'ke', 'kr', 'my', 'mx', 'ma', 'nz', 'ng', 'pe', 'ph', 'ro', 'ru', 'sa', 'sg', 'za', 'es', 'se', 'ch', 'tw', 'th', 'tr', 'ae', 'ua', 'us', 'vn']
COUNTRYNAMES = ['Algeria', 'Argentina', 'Australia', 'Bolivia', 'Brazil', 'Bulgaria', 'Canada', 'Chile', 'China', 'Colombia', 'Costa Rica', 'Croatia', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Finland', 'France', 'Germany', 'Greece', 'Guatemala', 'Hungary', 'India', 'Indonesia', 'Italy', 'Japan', 'Kenya', 'Korea', 'Malaysia', 'Mexico', 'Morocco', 'New Zealand', 'Nigeria', 'Peru', 'Philippines', 'Romania', 'Russia', 'Saudi Arabia', 'Singapore', 'South Africa', 'Spain', 'Sweden', 'Switzerland', 'Taiwan', 'Thailand', 'Turkey', 'UAE', 'Ukraine', 'United States', 'Vietnam']

# SESSION_CONFIGS = []

SESSION_CONFIGS = [
    dict(
        name='TPP',
        display_name="Third party punishment game",
        app_sequence=['language_selection', 'baseline_trials'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip(),
        config=dict(CURRENT_COUNTRY="us"),
    ),
    dict(
        name='extras',
        display_name="All extra tasks",
        app_sequence=['language_selection', 'pref_2PP_3PP', 'rule_following', 'crowding_out', 'dice_task', 'free_rider', 'demographics'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip(),
        config=dict(CURRENT_COUNTRY="us"),
    ),
    dict(
        name='crowding',
        display_name="Crowding-out",
        app_sequence=['language_selection', 'crowding_out'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip(),
        config=dict(CURRENT_COUNTRY="us"),
    ),
    dict(
        name='pref_2PP_3PP',
        display_name="Preference for 2PP versus 3PP",
        app_sequence=['language_selection', 'pref_2PP_3PP'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip(),
        config=dict(CURRENT_COUNTRY="us"),
    ),
    dict(
        name='dice',
        display_name="Dice task",
        app_sequence=['language_selection', 'dice_task'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip(),
        config=dict(CURRENT_COUNTRY="us"),
    ),
    dict(
        name='rule',
        display_name="Anti-social rule following",
        app_sequence=['language_selection', 'rule_following'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip(),
        config=dict(CURRENT_COUNTRY="us"),
    ),
    dict(
        name='narratives',
        display_name="Free rider narratives",
        app_sequence=['language_selection', 'free_rider'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip(),
        config=dict(CURRENT_COUNTRY="us"),
    ),
    dict(
        name='demographics',
        display_name="demographics only",
        app_sequence=['language_selection', 'demographics'],
        num_demo_participants=6,
        use_browser_bots=False,
        oTree_version_used=popen('otree --version').read().strip(),
        config=dict(CURRENT_COUNTRY="us",prolific = False),
    ),
]

for code, name in zip(COUNTRIES, COUNTRYNAMES):
    SESSION_CONFIGS.append(
        dict(
            name=f'all_games_{code}',  # session name uses country code (for URL, etc.)
            display_name=f"Complete study for {name}",  # show full country name in admin
            app_sequence=[
                'language_selection',
                'baseline_trials',
                'pref_2PP_3PP',
                'rule_following',
                'crowding_out',
                'dice_task',
                'free_rider',
                'demographics'
            ],
            num_demo_participants=6,
            use_browser_bots=False,
            config=dict(CURRENT_COUNTRY=code),
        )
    )


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.33,
    participation_fee=4.50,
    total_pages=321,
    doc=""
)

PARTICIPANT_FIELDS = ['language', 'lang_confirmed', 'language_selection_shown', 'current_country', 'current_countryname', 'dictator_country', 'receiver_country', 'progress', 'decision_page_number',
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
