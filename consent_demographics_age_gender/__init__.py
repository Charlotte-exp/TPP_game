from otree.api import *
import csv
import os
import itertools
import random
import logging
import time
import re
from typing import Tuple, Optional

from translations import get_translation
from dotenv import load_dotenv


doc = """
Your app description
"""

# For testing the QUOTA/SPEEDERS redirects: Change speeder threshold in demographics; remove some pages for faster advancing; use quota_by_country_test.csv with U.S.
# Participant label must be included in format ?participant_label=gid001_snameDEU1

def parse_participant_label(
    label_string: str,
    gid_prefix: str = "gid",
    sname_prefix: str = "sname",
    #id_pattern: str = r"[A-Za-z0-9]+",
) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a participant label and return (gid, sname) or (None, None) if not found.

    - Finds occurrences like "gid<id>" and "sname<id>" anywhere in the string.
    - Captures ANY characters for the id (letters, numbers, symbols)
      until it finds another identifier (gid or sname) or the end of the string.
    - Case-insensitive.
    """
    if not label_string:
        return None, None

    # pattern: capture prefix (gid|sname) then non-greedily capture everything until
    # the next prefix or end of string.
    combined_prefix = rf"(?:{re.escape(gid_prefix)}|{re.escape(sname_prefix)})"
    pattern = rf"(?i)({combined_prefix})(.*?)(?=(?:{combined_prefix})|$)"

    gid = None
    sname = None

    for m in re.finditer(pattern, label_string, flags=re.DOTALL):
        prefix = m.group(1).lower()
        value = m.group(2)
        if prefix == gid_prefix.lower():
            gid = value
        elif prefix == sname_prefix.lower():
            sname = value

    # strip surrounding whitespace (if any) but keep symbols inside the id
    if gid is not None:
        gid = gid.strip()
    if sname is not None:
        sname = sname.strip()

    return gid, sname

def get_quotas(country):
    import csv
    # Quotas to extract:
    required_columns = ['male', 'female', 'age1', 'age2', 'age3', 'age4', 'age5']
    with open('_static/global/quota_by_country.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            if row['iso2'] == country:
                # Create a dictionary to hold the results
                quotas = {}
                try:
                    # Extract and convert each required column to an integer
                    for col in required_columns:
                        quotas[col] = int(row[col])

                    # Once all columns are successfully extracted, return the dictionary
                    return quotas
                except (ValueError, KeyError) as e:
                    # This handles cases where a column is missing or a value is not a number
                    print(f"Error processing row for country '{country}': {e}")
                    return None  # Return None to indicate a data error in that row
    return []  # Return empty list if country not found

def get_country_dict_no_in(lang, iso2=None):
    with open('_static/global/country_codes_Toluna_lang.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        column_name = f"{lang}_no_in"
        if column_name not in reader.fieldnames:
            raise ValueError(f"Column '{column_name}' not found in CSV columns: {reader.fieldnames}")

        country_dict = {
            row["iso2"]: row[column_name]
            for row in reader
            if row.get("iso2") and row.get(column_name)
        }

    if iso2:
        return country_dict.get(iso2)
    return country_dict

def get_country_dict(lang, iso2=None):
    with open('_static/global/country_codes_Toluna_lang.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        if lang not in reader.fieldnames:
            raise ValueError(f"Language '{lang}' not found in CSV columns: {reader.fieldnames}")

        country_dict = {
            row["iso2"]: row[lang]
            for row in reader
            if row.get("iso2") and row.get(lang)
        }

    if iso2:
        return country_dict.get(iso2)
    return country_dict

class C(BaseConstants):
    NAME_IN_URL = 'demographics_age_gender'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NUM_DECISIONS_APPROX = 43
    STUDY_TIME = 30
    prolific = False


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    for player in subsession.get_players():
        participant = player.participant

        # Set language to English if English is the only offered language in that country (in this case participants do not see language selection pages)
        if 'language' not in participant.vars:
            participant.language = 'en'

        if 'progress' not in participant.vars:
            participant.progress = 1
            participant.decision_page_number = 0
            #participant.current_countryname_no_in = get_country_dict_no_in(participant.language, participant.current_country)



class Group(BaseGroup):
    pass


class Player(BasePlayer):

    declined_consent = models.StringField(blank=True)  # This stores whether the player declined to consent.

    ## Demographics
    age = models.IntegerField(
        min=1, max=100
    )
    gender = models.StringField()

    age_group = models.IntegerField() # This field stores the age group for easier counting

    quota_gender = models.StringField(blank=True) # This field stores the (binary) gender group on which quotas are based

    is_screened_out = models.BooleanField(default=False) # This stores whether the player is screened out. It defaults to False.

    screenout_reason = models.StringField(blank=True) # This stores the reason.

    ip_country_code = models.LongStringField()
    ip_country_name = models.LongStringField()
    ip_region = models.LongStringField()
    ip_city = models.LongStringField()
    ip_latitude_rounded = models.FloatField()
    ip_longitude_rounded = models.FloatField()
    ip_time_zone = models.LongStringField()
    ip_current_time = models.LongStringField()
    ip_is_proxy = models.BooleanField()
    ip_is_vpn = models.BooleanField()
    ip_is_tor = models.BooleanField()
    ip_is_anonymous = models.BooleanField()
    ip_mobile_desktop = models.LongStringField()
    ip_browser = models.LongStringField()

########### PAGES ############

class Consent(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        else:
            return False

    form_model = 'player'
    form_fields = ['declined_consent']

    @staticmethod
    def live_method(player, data):
        if data.get('geo_data'):
            geo = data['geo_data']
            player.ip_country_code = geo.get('country_code3')
            player.ip_country_name = geo.get('country_name')
            player.ip_region = geo.get('region')
            player.ip_city = geo.get('city')
            player.ip_latitude_rounded = geo.get('latitude_rounded')
            player.ip_longitude_rounded = geo.get('longitude_rounded')
            player.ip_time_zone = geo.get('time_zone')
            player.ip_current_time = geo.get('current_time')
            player.ip_is_proxy = geo.get('is_proxy')
            player.ip_is_vpn = geo.get('is_vpn')
            player.ip_is_tor = geo.get('is_tor')
            player.ip_is_anonymous = geo.get('is_anonymous')
            player.ip_mobile_desktop = geo.get('mobile_desktop')
            player.ip_browser = geo.get('browser')

            # print('player.ip_country_code', player.ip_country_code)
            # print('player.ip_country_name', player.ip_country_name)
            # print('player.ip_region', player.ip_region)
            # print('player.ip_city', player.ip_city)
            # print('player.ip_latitude_rounded', player.ip_latitude_rounded)
            # print('player.ip_longitude_rounded', player.ip_longitude_rounded)
            # print('player.ip_time_zone', player.ip_time_zone)
            # print('player.ip_current_time', player.ip_current_time)
            # print('player.ip_is_proxy', player.ip_is_proxy)
            # print('player.ip_is_vpn', player.ip_is_vpn)
            # print('player.ip_is_tor', player.ip_is_tor)
            # print('player.ip_is_anonymous', player.ip_is_anonymous)
            # print('player.ip_mobile_desktop', player.ip_mobile_desktop)
            # print('player.ip_browser', player.ip_browser)

        return {}

    def vars_for_template(player: Player):
        participant = player.participant

        ### Fetch URL parameter with GID and sname
        raw_label = participant.label  # label must be included as ?participant_label=gid001_snameDEU1

        gid_value, sname_value = parse_participant_label(raw_label)

        if gid_value and sname_value:
            participant.GID = gid_value
            participant.sname = sname_value
            print(f"-> SUCCESS: Participant {participant.id_in_session} - Parsed GID='{participant.GID}' and sname='{participant.sname}'")

        elif gid_value and not sname_value:
            participant.GID = gid_value
            participant.sname = None
            print(f"-> SUCCESS (partial): Participant {participant.id_in_session} - Parsed GID='{participant.GID}' (no sname found)")

        elif sname_value and not gid_value:
            participant.GID = None
            participant.sname = sname_value
            print(f"-> SUCCESS (partial): Participant {participant.id_in_session} - Parsed sname='{participant.sname}' (no GID found)")

        else:
            participant.GID = "INVALID_LABEL_FORMAT"
            participant.sname = "INVALID_LABEL_FORMAT"
            print(f"-> ERROR: Participant {participant.id_in_session} - Could not parse label '{raw_label}'.")

        ### Record start time
        player.participant.vars['session_start_time'] = time.time()
        print('Start time', player.participant.vars.get('session_start_time'))

        ### Get current countryname
        lang = participant.language
        print("language: ", lang)

        # Load countrynames in selected language
        participant.current_countryname = get_country_dict(lang, participant.current_country)

        # Load dotenv to get API key for logging IP-related info
        load_dotenv()

        return dict(
            consent_title=get_translation('consent_title', lang),
            consent_thank_you=get_translation('consent_thank_you', lang),
            consent_intro_title=get_translation('consent_intro_title', lang),
            consent_intro1=get_translation('consent_intro1', lang,
                                          decisions_approx=C.NUM_DECISIONS_APPROX,
                                          time=C.STUDY_TIME),
            consent_intro2=get_translation('consent_intro2', lang),
            consent_intro3=get_translation('consent_intro3', lang),
            consent_payment_title=get_translation('consent_payment_title', lang),
            consent_payment_prolific=get_translation('consent_payment_prolific', lang,
                                            participation_fee=player.session.config['participation_fee']),
            consent_payment_toluna1=get_translation('consent_payment_toluna1', lang),
            consent_payment_toluna2=get_translation('consent_payment_toluna2', lang),
            consent_payment_toluna3=get_translation('consent_payment_toluna3', lang),
            consent_rights_title= get_translation('consent_rights_title', lang),
            consent_rights1=get_translation('consent_rights1', lang),
            consent_rights2=get_translation('consent_rights2', lang),
            consent_rights3=get_translation('consent_rights3', lang),
            consent_toluna_ID=get_translation('consent_toluna_ID', lang),
            consent_click=get_translation('consent_click', lang),
            consent_questions=get_translation('consent_questions', lang),
            consent_contact=get_translation('consent_contact', lang),
            button_consent=get_translation('button_consent', lang),
            consent_declined=get_translation('consent_declined', lang),
            lang = lang,
            ipregistry_key= os.getenv("IPREGISTRY_KEY")
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1

        print("player.declined_consent", player.declined_consent)

        if player.declined_consent == "1":
            participant.vars['declined_consent_boolean'] = True
            print("participant.vars['declined_consent_boolean']", participant.vars['declined_consent_boolean'])
            print(f"Player {player.id_in_subsession} SCREENED OUT. Reason: Declined to consent.")



class ConsentDeclined(Page):
    """
    This page redirects people to Toluna automatically if they declined to consent
    """
    @staticmethod
    def is_displayed(player: Player):
        if player.participant.vars.get('declined_consent_boolean'):
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        sname = participant.sname
        gid = participant.GID

        redirect_link = f"http://ups.surveyrouter.com/trafficui/mscui/SOTerminated.aspx?sname={sname}&gid={gid}"
        print("redirect_link consent declined", redirect_link)

        return dict(
            #consent_declined_info=get_translation('consent_declined_info', lang),
            #redirect_wait=get_translation('redirect_wait', lang),
            redirect_link=redirect_link,
            lang=lang,
            button_next=get_translation('button_next', lang)
        )


class Demographics_age_gender(Page):
    form_model = 'player'
    form_fields = ['age', 'gender']

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        #current_countryname = player.participant.current_countryname
        current_countryname_no_in = get_country_dict_no_in(participant.language, participant.current_country)

        current_country = participant.current_country

        return dict(
            total_pages=player.session.config['total_pages'],
            #descr_incentive=get_translation('descr_incentive', lang),
            age_question=get_translation('age_question', lang),
            gender_question = get_translation('gender_question', lang),
            female=get_translation('female', lang),
            male=get_translation('male', lang),
            other=get_translation('other', lang),
            pnts=get_translation('pnts', lang),
            button_next=get_translation('button_next', lang),
            consent_title=get_translation('consent_title', lang),
            lang = lang,
            current_country = current_country,
            error3=get_translation('error3', lang),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1

        #### CHECK IF TOO YOUNG

        print("player.age", player.age)

        if player.age < 18:
            participant.vars['age_too_low_boolean'] = True
            print("participant.vars['age_too_low_boolean']", participant.vars['age_too_low_boolean'])
            print(f"Player {player.id_in_subsession} SCREENED OUT. Reason: Age too low.")

        if player.age >= 18:

            #### CHECK QUOTAS

            ## 1) Age categorization
            if 18 <= player.age <= 24:
                player.age_group = 1
            elif 25 <= player.age <= 34:
                player.age_group = 2
            elif 35 <= player.age <= 44:
                player.age_group = 3
            elif 45 <= player.age <= 54:
                player.age_group = 4
            else:
                player.age_group = 5

            # Special case: Morocco has no age category 5 and category 4 is 45+ --> Recode age groups 5 to 4
            if participant.current_country == "ma" and player.age_group == 5:
                player.age_group = 4

            ## 2) Get quotas
            quotas = get_quotas(participant.current_country)
            print("quotas_country", quotas)
            print("input age_group", player.age_group)
            print("input gender", player.gender)

            # Determine Gender for Quota Check
            # Create a temporary variable, quota_gender. This preserves the player's actual response in player.gender.

            actual_gender = player.gender

            if actual_gender == 'Female':
                player.quota_gender = 'Female'
            elif actual_gender == 'Male':
                player.quota_gender = 'Male'
            else:  # Since quota is binary, randomly allocate non-binary responses ('Other', 'Prefer not to say') to one of the two categories
                player.quota_gender = random.choice(['Male', 'Female'])
                print(f"Player {player.id_in_subsession} chose '{actual_gender}', randomly assigned to '{player.quota_gender}' for quota check.")

            ## 3) Count other completed players
            current_female_count = 0
            current_male_count = 0
            current_age_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  # A dictionary to hold counts for each age group
            current_total_count = 0

            # Extra counts to check how many people started survey in last 25 minutes
            NOW = time.time()
            WINDOW_SECONDS = 25 * 60
            MAX_ACTIVE_STARTERS = 50
            recent_starters = 0

            # Get all players in the session
            all_players = player.subsession.get_players()

            for p in all_players:
                if p.id_in_subsession == player.id_in_subsession:
                    continue

                # Safely check if they passed demographics.
                gender_for_quota_check = p.field_maybe_none('quota_gender')

                # Safely check if they are "complete".
                is_complete = p.participant.vars.get('is_fully_complete')

                # Only count people who have submitted BOTH the demographics AND the final page.
                if gender_for_quota_check is not None and is_complete is not None:

                    current_total_count += 1

                    # Now we know this is a "complete" response, so we can count them.
                    if gender_for_quota_check == 'Female':
                        current_female_count += 1
                    elif gender_for_quota_check == 'Male':
                        current_male_count += 1

                    age_group_value = p.field_maybe_none('age_group')
                    if age_group_value in current_age_counts:
                        current_age_counts[age_group_value] += 1

                # Additionally check how many activiely participate
                start_time = p.participant.vars.get('session_start_time')

                if start_time is None:
                    continue

                if NOW - start_time <= WINDOW_SECONDS:
                    recent_starters += 1

            print("current_female_count", current_female_count)
            print("current_male_count", current_male_count)
            print("current_age_counts[player_age_group]", current_age_counts[player.age_group])
            print("recent_starters", recent_starters)

            ## 4) Compare current player against quotas
            is_screened_out = False
            screenout_reason = ""

            # Adjust quotas based on country updates
            QUOTAS_UPDATED = {
                'dz': {'total': 365, 'female': 999, 'male': 999},
                'au': {'total': 365, 'female': 999, 'male': 0},
                'do': {'total': 365, 'female': 999, 'male': 999},
                'eg': {'total': 365, 'female': 999, 'male': 999},
                'fr': {'total': 370, 'female': 0, 'male': 999},
                'de': {'total': 365, 'female': 999, 'male': 0},
                'gr': {'total': 365, 'female': 0, 'male': 999},
                'gt': {'total': 365, 'female': 0, 'male': 999},
                'hu': {'total': 370, 'female': 0, 'male': 999},
                'jp': {'total': 369, 'female': 999, 'male': 0},
                'ke': {'total': 371, 'female': 999, 'male': 0},
                'ru': {'total': 365, 'female': 999, 'male': 999},
                'sa': {'total': 365, 'female': 999, 'male': 999},
                'sg': {'total': 365, 'female': 999, 'male': 999},
                'za': {'total': 371, 'female': 0, 'male': 999},
                'es': {'total': 371, 'female': 0, 'male': 999},
                'se': {'total': 365, 'female': 999, 'male': 999},
                'ch': {'total': 365, 'female': 999, 'male': 999},
                'tw': {'total': 368, 'female': 999, 'male': 0},
                'tr': {'total': 373, 'female': 0, 'male': 999},
                'ae': {'total': 365, 'female': 999, 'male': 999},
                'ua': {'total': 405, 'female': 999, 'male': 0},
                'us': {'total': 369, 'female': 999, 'male': 0},
                'vn': {'total': 365, 'female': 999, 'male': 0},
            }


            country_quota = QUOTAS_UPDATED.get(participant.current_country)

            if country_quota is None:
                country_quota = {'total': 365, 'female': 999, 'male': 999}

            # Screen out if too many people currently in study
            if recent_starters > MAX_ACTIVE_STARTERS:
                is_screened_out = True
                screenout_reason = "Too many participants currently in the study"

            # Check gender quota
            if current_total_count >= country_quota['total']:
                is_screened_out = True
                screenout_reason = "Total quota is full"

            elif player.quota_gender == 'Female' and (current_female_count >= quotas['female'] or current_female_count >= country_quota['female']):
                is_screened_out = True
                screenout_reason = "Gender quota (Female) is full"

            elif player.quota_gender == 'Male' and (current_male_count >= quotas['male'] or current_male_count >= country_quota['male']):
                is_screened_out = True
                screenout_reason = "Gender quota (Male) is full"

            # Check age quota
            player_age_group = player.age_group
            if not is_screened_out and current_age_counts[player_age_group] >= quotas[f'age{player_age_group}']:
                is_screened_out = True
                screenout_reason = f"Age group {player_age_group} quota full"

            ## 5) Set a flag on the participant
            if is_screened_out:
                player.is_screened_out = True
                player.screenout_reason = screenout_reason
                print(f"Player {player.id_in_subsession} SCREENED OUT. Reason: {player.screenout_reason}")
            else:
                # The default is already False, but it's good to be explicit
                player.is_screened_out = False
                print(f"Player {player.id_in_subsession} PASSED quotas.")


class ScreenedOutAge(Page):
    """
    This page redirects people to Toluna automatically if they are under 18 years
    """
    @staticmethod
    def is_displayed(player: Player):
        if player.participant.vars.get('age_too_low_boolean'):
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        sname = participant.sname
        gid = participant.GID

        redirect_link = f"http://ups.surveyrouter.com/trafficui/mscui/SOTerminated.aspx?sname={sname}&gid={gid}"
        print("redirect_link age check failed", redirect_link)

        return dict(
            redirect_link=redirect_link,
            lang=lang,
            button_next=get_translation('button_next', lang)
        )



class ScreenedOutLink(Page):
    """
    This page redirects people to Toluna automatically if quota is full
    """
    @staticmethod
    def is_displayed(player: Player):
        if player.is_screened_out:
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        sname = participant.sname
        gid = participant.GID

        redirect_link = f"http://ups.surveyrouter.com/trafficui/mscui/SOQuotafull.aspx?sname={sname}&gid={gid}"
        print("redirect_link", redirect_link)

        return dict(
            #quota_full_info=get_translation('quota_full_info', lang),
            #redirect_wait=get_translation('redirect_wait', lang),
            redirect_link=redirect_link,
            lang=lang,
            button_next=get_translation('button_next', lang)
        )


page_sequence = [Consent,
                 ConsentDeclined,
                 Demographics_age_gender,
                 ScreenedOutAge,
                 ScreenedOutLink,
                 ]
