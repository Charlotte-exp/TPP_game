from otree.api import *
import csv
import os
import random
import time

from translations import get_translation


doc = """
Your app description
"""

# For testing the QUOTA/SPEEDERS redirects: Change speeder threshold in demographics; remove some pages for faster advancing; use quota_by_country_test.csv with U.S.

def parse_participant_label(label_string):
    if not label_string:
        return None, None
    try:
        gid_part, sname_part = label_string.split('_')
        if gid_part.startswith('gid') and sname_part.startswith('sname'):
            gid = gid_part[3:]
            sname = sname_part[5:]
            return gid, sname
        else:
            return None, None
    except (ValueError, IndexError):
        return None, None

def get_quotas(country): ### TO TEST QUOTAS, comment out baseline_trials/init 1130
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


class C(BaseConstants):
    NAME_IN_URL = 'demographics_age_gender'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


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

    ## Demographics
    age = models.IntegerField(
        min=10, max=100
    )
    gender = models.StringField()

    age_group = models.IntegerField() # This field stores the age group for easier counting

    quota_gender = models.StringField(blank=True) # This field stores the (binary) gender group on which quotas are based

    is_screened_out = models.BooleanField(default=False) # This stores whether the player is screened out. It defaults to False.

    screenout_reason = models.StringField(blank=True) # This stores the reason.

########### PAGES ############

class Demographics_age_gender(Page):
    form_model = 'player'
    form_fields = ['age', 'gender']

    def vars_for_template(player: Player):
        participant = player.participant

        ### Fetch URL parameter with GID and sname
        raw_label = participant.label  # label must be included as ?participant_label=gid001_snameDEU1

        gid_value, sname_value = parse_participant_label(raw_label)

        if gid_value and sname_value:
            participant.GID = gid_value
            participant.sname = sname_value
            print(
                f"-> SUCCESS: Participant {participant.id_in_session} - Parsed GID='{participant.GID}' and sname='{participant.sname}'")
        else:
            participant.GID = "INVALID_LABEL_FORMAT"
            participant.sname = "INVALID_LABEL_FORMAT"
            print(
                f"-> ERROR: Participant {participant.id_in_session} - Could not parse label '{raw_label}'.")

        ### Record start time
        player.participant.vars['session_start_time'] = time.time()
        print('Start time', player.participant.vars.get('session_start_time'))

        lang = participant.language

        #current_countryname = player.participant.current_countryname
        current_countryname_no_in = get_country_dict_no_in(participant.language, participant.current_country)

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
            error3=get_translation('error3', lang),
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1

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

        # Get all players in the session
        all_players = player.subsession.get_players()

        for p in all_players:
            if p.id_in_subsession == player.id_in_subsession:
                continue

            # Safely get the value of the gender field to see if they passed demographics.
            gender_for_quota_check = p.field_maybe_none('quota_gender')

            # Safely get the value of your MILESTONE field to see if they are "complete".
            is_complete = p.participant.vars.get('is_fully_complete')

            # Only count people who have submitted BOTH the demographics AND the final page.
            if gender_for_quota_check is not None and is_complete is not None:

                # Now we know this is a "complete" response, so we can count them.
                if gender_for_quota_check == 'Female':
                    current_female_count += 1
                elif gender_for_quota_check == 'Male':
                    current_male_count += 1

                age_group_value = p.field_maybe_none('age_group')
                if age_group_value in current_age_counts:
                    current_age_counts[age_group_value] += 1

        print("current_female_count", current_female_count)
        print("current_male_count", current_male_count)
        print("current_age_counts[player_age_group]", current_age_counts[player.age_group])

        ## 4) Compare current player against quotas
        is_screened_out = False
        screenout_reason = ""

        # Check gender quota
        if player.quota_gender == 'Female' and current_female_count >= quotas['female']:
            is_screened_out = True
            screenout_reason = "Gender quota (Female) is full"

        elif player.quota_gender == 'Male' and current_male_count >= quotas['male']:
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
            quota_full_info=get_translation('quota_full_info', lang),
            redirect_wait=get_translation('redirect_wait', lang),
            redirect_link=redirect_link,
            lang=lang,
            button_next=get_translation('button_next', lang)
        )


page_sequence = [Demographics_age_gender,
                 ScreenedOutLink,
                 ]
