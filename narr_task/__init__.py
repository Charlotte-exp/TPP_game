from otree.api import *

from translations import get_translation

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'free_rider'
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


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ## Relational Mobility
    wealthy_contribution = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    wealthy_merit = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    poor_contribution = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    poor_merit = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )


#########  PAGES  ###########
class NarrPage(Page):
    form_model = "player"
    form_fields = ["wealthy_contribution", "wealthy_merit", "poor_contribution", "poor_merit"]

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        return dict(
            narratives_question=get_translation("narratives_question", lang),
            narratives_wealthy_contribution=get_translation("narratives_wealthy_contribution", lang),
            narratives_wealthy_merit=get_translation("narratives_wealthy_merit", lang),
            narratives_poor_contribution=get_translation("narratives_poor_contribution", lang),
            narratives_poor_merit=get_translation("narratives_poor_merit", lang),\
            strongly_disagree=get_translation("strongly_disagree", lang),
            disagree=get_translation("disagree", lang),
            slightly_disagree=get_translation("slightly_disagree", lang),
            slightly_agree=get_translation("slightly_agree", lang),
            agree=get_translation("agree", lang),
            strongly_agree=get_translation("strongly_agree", lang),
            button_next=get_translation("button_next", lang),
            error3=get_translation("error3", lang),
            additional_questions=get_translation("additional_questions", lang),
            lang = lang,
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


page_sequence = [NarrPage,
                 #ResultsWaitPage,
                 ]
