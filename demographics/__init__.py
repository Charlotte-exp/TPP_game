from otree.api import *
import csv
import os

from translations import get_translation


doc = """
Your app description
"""

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
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


def get_country_list(lang):
    filepath = os.path.join(os.path.dirname(__file__), '../_static/global/countrynames_all_lang.csv')
    with open(filepath, encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        if lang not in reader.fieldnames:
            raise ValueError(f"Language '{lang}' not found in CSV columns: {reader.fieldnames}")
        countries_world = [row[lang] for row in reader if row[lang]]
        countries_world.sort()  # Sort alphabetically
        return countries_world



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
            participant.current_countryname = get_country_dict(participant.language, participant.current_country)



class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ## Demographics
    age = models.IntegerField(
        min=10, max=100
    )
    gender = models.StringField()

    #gender = models.StringField()

    # born = models.StringField(
    #     choices=['Yes', 'No'],
    #     widget=widgets.RadioSelect
    # )
    born = models.StringField()
    born_mother = models.StringField()
    born_father = models.StringField()
    income_ladder = models.IntegerField(
        choices=[i for i in range(1, 11)],
        blank=True,
    )
    education = models.StringField()
    rural_urban = models.StringField()

    ## Relational Mobility
    meeting_1 = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    meeting_2 = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    # meeting_3 = models.StringField(
    #     choices=[
    #         [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
    #         [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
    #     ],
    #     verbose_name='',
    #     widget=widgets.RadioSelectHorizontal
    # )
    choosing_1 = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    choosing_2 = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    # choosing_3 = models.StringField(
    #     choices=[
    #         [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
    #         [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
    #     ],
    #     verbose_name='',
    #     widget=widgets.RadioSelectHorizontal
    # )
    # choosing_4 = models.StringField(
    #     choices=[
    #         [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
    #         [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
    #     ],
    #     verbose_name='',
    #     widget=widgets.RadioSelectHorizontal
    # )

    ## Self - other circle
    self_other = models.IntegerField()

    # ## Comment field
    # question_box = models.LongStringField()

    # comment_box = models.LongStringField(
    #     blank = True  # Optional: allow it to be empty
    # )

    toluna_id = models.IntegerField()


########### PAGES ############

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender','born','born_mother', 'born_father', 'education', 'rural_urban', 'toluna_id']

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        current_countryname = player.participant.current_countryname

        all_countries = get_country_list(lang)
        countries = [current_countryname] + [c for c in all_countries if c != current_countryname]

        return dict(
            total_pages=player.session.config['total_pages'],
            #descr_incentive=get_translation('descr_incentive', lang),
            age_question=get_translation('age_question', lang),
            gender_question = get_translation('gender_question', lang),
            born_question=get_translation('born_question', lang),
            born_mother_question=get_translation('born_mother_question', lang),
            born_father_question=get_translation('born_father_question', lang),
            education_question=get_translation('education_question', lang),
            rural_urban_question=get_translation('rural_urban_question', lang),
            female=get_translation('female', lang),
            male=get_translation('male', lang),
            other=get_translation('other', lang),
            pnts=get_translation('pnts', lang),
            rural=get_translation('rural', lang),
            town=get_translation('town', lang),
            city=get_translation('city', lang),
            edu0=get_translation('edu0', lang),
            edu1=get_translation('edu1', lang),
            edu2=get_translation('edu2', lang),
            edu3=get_translation('edu3', lang),
            edu4=get_translation('edu4', lang),
            edu5=get_translation('edu5', lang),
            edu6=get_translation('edu6', lang),
            edu7=get_translation('edu7', lang),
            edu8=get_translation('edu8', lang),
            toluna_id_question = get_translation('toluna_id', lang),
            select_country=get_translation('select_country', lang),
            button_next=get_translation('button_next', lang),
            additional_questions=get_translation('additional_questions', lang),
            lang = lang,
            error3=get_translation('error3', lang),
            countries=countries,
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class Ladder(Page):
    form_model = 'player'
    form_fields = ['income_ladder']

    @staticmethod
    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        return dict(
            total_pages=player.session.config['total_pages'],
            ladder_values=list(range(10, 0, -1)),  # From 10 to 1
            ladder_question=get_translation('ladder_question', lang),
            ladder_intro=get_translation('ladder_intro', lang),
            ladder_best_off=get_translation('ladder_best_off', lang),
            ladder_worst_off=get_translation('ladder_worst_off', lang),
            button_next=get_translation('button_next', lang),
            additional_questions=get_translation('additional_questions', lang),
            lang=lang,
            error1=get_translation('error1', lang),
        )

    def error_message(self, values):
        if values['income_ladder'] in [None, 0]:
            return 'Missing response'

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class RelationalMobility(Page):
    form_model = 'player'
    form_fields = ['meeting_1', 'meeting_2', 'choosing_1', 'choosing_2']

    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        #lang = "Korean" #override for testing

        return dict(
            total_pages=player.session.config['total_pages'],
            rel_intro=get_translation('rel_intro', lang),
            rmob1=get_translation('rmob1', lang),
            rmob4=get_translation('rmob4', lang),
            rmob10=get_translation('rmob10', lang),
            rmob12=get_translation('rmob12', lang),
            strongly_disagree=get_translation('strongly_disagree', lang),
            disagree=get_translation('disagree', lang),
            slightly_disagree=get_translation('slightly_disagree', lang),
            slightly_agree=get_translation('slightly_agree', lang),
            agree=get_translation('agree', lang),
            strongly_agree=get_translation('strongly_agree', lang),
            button_next=get_translation('button_next', lang), #"다음"
            additional_questions=get_translation('additional_questions', lang), #"추가 질문"
            lang = lang,
            error3=get_translation('error3', lang),
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class Circle(Page):
    form_model = 'player'
    form_fields = ['self_other']

    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        return dict(
            total_pages=player.session.config['total_pages'],
            circle_intro=get_translation('circle_intro', lang),
            circle_question=get_translation('circle_question', lang),
            you=get_translation('you', lang),
            your_country=get_translation('your_country', lang),
            button_next=get_translation('button_next', lang),
            additional_questions=get_translation('additional_questions', lang),
            lang=lang,
            error1=get_translation('error1', lang),
        )

    def error_message(self, values):
        if values['self_other'] in [None, 0]:
            return 'Missing response'

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1

class CommentBox(Page):
    form_model = 'player'
    form_fields = ['question_box']

    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        return dict(
            total_pages=player.session.config['total_pages'],
            feedback=get_translation('feedback', lang),
            #comment_intro=get_translation('comment_intro', lang),
            question_box=get_translation('question_box', lang),
            lang=lang,
            #comment_box=get_translation('comment_box', lang),
            button_next=get_translation('button_next', lang)
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        prolific = player.session.config['config']['prolific']

        return dict(
            prolific = prolific,
            total_pages=player.session.config['total_pages'],
            participation_fee= player.session.config['participation_fee'],
            study_complete=get_translation('study_complete', lang),
            thank_you=get_translation('thank_you', lang),
            thank_you_short=get_translation('thank_you_short', lang),
            end_bonus=get_translation('end_bonus', lang),
            redirect_prolific=get_translation('redirect_prolific', lang),
            debrief=get_translation('debrief', lang),
            close_window=get_translation('close_window', lang),
            bonus_payment=get_translation('bonus_payment', lang),
            lang=lang,
            button_next=get_translation('button_next', lang)
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class ProlificLink(Page):
    """
    This page redirects pp to prolific automatically with a javascript (don't forget to put paste the correct link!).
    There is a short text, the completion code and the link in case it is not automatic.
    """
    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        return dict(
            thank_you_short=get_translation('thank_you_short', lang),
            redirect_prolific_wait=get_translation('redirect_prolific_wait', lang),
            redirect_prolific_info=get_translation('redirect_prolific_info', lang),
            redirect_prolific_code=get_translation('redirect_prolific_code', lang),
            lang=lang,
            button_next=get_translation('button_next', lang)
        )


page_sequence = [RelationalMobility,
                 Circle,
                 Ladder,
                 Demographics,
                 Payment,
                 ProlificLink]
