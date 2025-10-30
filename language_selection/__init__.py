from otree.api import *

from translations import get_translation

doc = """
Your app description
"""


def parse_participant_label(label_string):
    """
    Parses a participant label string with the format "gid[GID]_sname[sname]".

    Args:
        label_string (str): The participant label, e.g., "gid0012_snameDEU1".

    Returns:
        tuple: A tuple containing (gid, sname).
               Returns (None, None) if the format is incorrect.
    """
    try:
        # 1. Split the string into two parts at the underscore
        gid_part, sname_part = label_string.split('_')

        # 2. Check if the parts have the correct prefixes
        if gid_part.startswith('gid') and sname_part.startswith('sname'):
            # 3. Extract the values by slicing off the prefixes
            # "gid" is 3 characters long, "sname" is 5 characters long.
            gid = gid_part[3:]
            sname = sname_part[5:]

            # 4. Return the extracted values
            return gid, sname
        else:
            # The prefixes were not correct
            return None, None

    except (ValueError, IndexError):
        # This block runs if .split() fails (no '_') or other errors occur.
        # It prevents your app from crashing if a bad label is used.
        return None, None


def get_possible_languages(country):
    import csv
    with open('_static/global/languages_by_country.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            if row['country'] == country:
                return [lang.strip() for lang in row['languages'].split(',')]
    return []  # Return empty list if country not found

def get_language_names(language_codes, use_english_name=False):
    import csv
    language_names = []
    with open('_static/global/language_codes.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        # Create two lookup dictionaries
        code_to_native = {}
        code_to_english = {}
        for row in reader:
            code_to_native[row['language_code']] = row['language']
            code_to_english[row['language_code']] = row['language_en']

    for code in language_codes:
        if use_english_name:
            name = code_to_english.get(code)
        else:
            name = code_to_native.get(code)
        if name:
            language_names.append(name)

    return language_names



class C(BaseConstants):
    NAME_IN_URL = 'language_selection'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10

    # CURRENT_COUNTRY = 'ch'  # CHANGE TO COUNTRY FOR THIS LINK
    # POSSIBLE_LANG = get_possible_languages(CURRENT_COUNTRY)
    # POSSIBLE_LANG_NAMES = get_language_names(POSSIBLE_LANG)
    #
    # DEFAULT_LANGUAGE = POSSIBLE_LANG[0]
    # NUM_LANGS = len(POSSIBLE_LANG)


class Subsession(BaseSubsession):
    pass

# def js_vars(player: 'Player'):
#     # This function runs for every page load for every player.
#     # We get the language from your custom participant field.
#     lang_code = player.participant.language
#     return dict(
#         language_code=lang_code
#     )


def creating_session(subsession):

    current_country = subsession.session.config['config']['CURRENT_COUNTRY']

    # Check if language selection should be shown for current_country (only if languages other than English are available)
    num_langs = len(get_possible_languages(current_country))
    show_language_selection = num_langs > 1

    print("current_country", current_country)
    print("num_langs", num_langs)

    for player in subsession.get_players():
        participant = player.participant
        participant.language_selection_shown = show_language_selection
        if current_country == 'all':
            participant.all_language_test = True
            participant.current_country = "us"
        else:
            participant.all_language_test = False
            participant.current_country = current_country


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    lang = models.StringField()
    confirm_language = models.StringField()
    lang_confirmed = models.BooleanField(initial=False)


# PAGES

class LanguageSelection(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.vars.get('lang_confirmed', False) and player.participant.language_selection_shown

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['lang']

    def vars_for_template(player: Player):
        participant = player.participant
        current_country = participant.current_country
        all_language_test = participant.all_language_test

        # For all-language testing page, set default country to US AFTER language selection menu set
        if all_language_test == True:
            possible_lang = get_possible_languages("all")
        else:
            possible_lang = get_possible_languages(current_country)

        possible_lang_names = get_language_names(possible_lang)
        default_language = possible_lang[0]


        return dict(
            current_country = current_country,
            language_options=zip(possible_lang, possible_lang_names),
            welcome=get_translation('consent_title', default_language),
            language_selection = get_translation('language_selection', default_language),
            language_select=get_translation('language_selection_placeholder', default_language),
            button_next=get_translation('button_next', default_language),
            default_language = default_language,
            error3=get_translation('error3', default_language),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.language = player.lang

        ### Fetch GID (participant ID) and sname (study name) from url input participant_label

        # Get the raw label from the URL
        raw_label = participant.label
        print(f"Raw url label '{raw_label}'")

        # Call function to parse the label and extract gid and sname
        gid_value, sname_value = parse_participant_label(raw_label)

        # Check if parsing was successful before saving the data
        if gid_value and sname_value:
            participant.GID = gid_value
            participant.sname = sname_value
            print(f"-> SUCCESS: Saved GID='{participant.GID}' and sname='{participant.sname}'")
        else:
            # Handle cases with bad labels. You can assign defaults or leave them blank.
            participant.GID = "INVALID_LABEL_FORMAT"
            participant.sname = "INVALID_LABEL_FORMAT"
            print(f"-> ERROR: Could not parse label. Assigned default error values.")


class LanguageConfirmation(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.vars.get('lang_confirmed', False) and player.participant.language_selection_shown

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['confirm_language']

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language
        current_country = participant.current_country

        selected_lang_name = get_language_names([lang])[0]
        selected_lang_name_en = get_language_names([lang], True)[0]

        default_language = get_possible_languages(current_country)[0]

        return dict(
            lang=lang,
            language_confirmation_question=get_translation('language_confirmation_question', lang,
                                                  language = selected_lang_name),
            language_confirmation=get_translation('language_confirmation', lang),
            button_go_back=get_translation('button_go_back', lang),
            button_confirm=get_translation('button_confirm', lang),
            language_confirmation_question_en=get_translation('language_confirmation_question', 'en',
                                                  language = selected_lang_name_en),
            button_go_back_en=get_translation('button_go_back', 'en'),
            button_confirm_en=get_translation('button_confirm', 'en'),
            default_language = default_language,
            error3=get_translation('error3', default_language),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        if player.confirm_language == 'yes':
            participant.lang_confirmed = True # Language selection page is shown as long language has not been confirmed
        else:
            participant.lang_confirmed = False  # Explicit for clarity

page_sequence = [LanguageSelection, LanguageConfirmation]