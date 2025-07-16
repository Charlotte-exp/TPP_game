from otree.api import *

from translations import get_translation

doc = """
Your app description
"""

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

    CURRENT_COUNTRY = 'ch'  # CHANGE TO COUNTRY FOR THIS LINK
    POSSIBLE_LANG = get_possible_languages(CURRENT_COUNTRY)
    POSSIBLE_LANG_NAMES = get_language_names(POSSIBLE_LANG)

    DEFAULT_LANGUAGE = POSSIBLE_LANG[0]
    NUM_LANGS = len(POSSIBLE_LANG)


class Subsession(BaseSubsession):
    pass


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
        return not player.participant.vars.get('lang_confirmed', False) and C.NUM_LANGS > 1

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['lang']

    def vars_for_template(player: Player):
        default_language = C.DEFAULT_LANGUAGE
        return dict(
            current_country = C.CURRENT_COUNTRY,
            language_options=zip(C.POSSIBLE_LANG, C.POSSIBLE_LANG_NAMES),
            welcome=get_translation('consent_title', default_language),
            language_selection_en = "Please select your language",
            language_select_en="Select language",
            button_next=get_translation('button_next', default_language),
            error3=get_translation('error3', default_language),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.language = player.lang


class LanguageConfirmation(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.vars.get('lang_confirmed', False) and C.NUM_LANGS > 1

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['confirm_language']

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language
        default_language = C.DEFAULT_LANGUAGE
        selected_lang_name = get_language_names([lang])[0]
        selected_lang_name_en = get_language_names([lang], True)[0]
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