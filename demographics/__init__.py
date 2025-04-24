from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ## Demographics
    age = models.IntegerField(
        verbose_name='What is your age?',
        min=0, max=100
    )
    gender = models.StringField(
        choices=['Female', 'Male', 'Other', 'Prefer not to say'],
        verbose_name='What gender do you identify as?',
        widget=widgets.RadioSelect
    )
    born = models.StringField(
        choices=['Yes', 'No'],
        widget=widgets.RadioSelect
    )
    born_mother = models.StringField(
        choices=['Yes', 'No'],
        widget=widgets.RadioSelect
    )
    born_father = models.StringField(
        choices=['Yes', 'No'],
        widget=widgets.RadioSelect
    )
    income_ladder = models.IntegerField(
        choices=[i for i in range(1, 11)],
        blank=True,
        label="Where would you place yourself on this ladder?"
    )
    education = models.StringField(
        choices=['No formal education/Early childhood education', 'Primary education (ages 5–12)',
                 'Lower secondary education (ages ~12–15)', 'Upper secondary education (ages ~15–18)',
                 'Post-secondary non-tertiary education (e.g., vocational training, certificates)',
                 'Short-cycle tertiary education (e.g., associate degree, advanced diploma)', 'Bachelor’s degree or equivalent',
                 'Master’s degree or equivalent', 'Doctoral degree (PhD) or equivalent'],
        verbose_name='What is the highest level of education you have completed?',
        widget=widgets.RadioSelect
    )
    rural = models.StringField(
        choices=["A rural area or village", 'Small or medium-sized town', 'Large town/city'],
        verbose_name='Would you say you live in...?',
        widget=widgets.RadioSelect
    )

    ## Relational Mobility
    q1 = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    q2 = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )

    ## Self - other circle
    self_other = models.IntegerField()

    ## Comment field
    comment_box = models.LongStringField(
        verbose_name=''
    )


########### PAGES ############

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender','born','born_mother', 'born_father', 'education', 'rural']

    @staticmethod
    def vars_for_template(player: Player):
        current_country = 'Switzerland'
        #participant = player.participant
        return {
            'born_question': f"Were you born in {current_country}?",
            'born_mother_question': f"Was your mother born in {current_country}?",
            'born_father_question': f"Was your father born in {current_country}?",
        }

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1

class Ladder(Page):
    form_model = 'player'
    form_fields = ['income_ladder']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            ladder_values=list(range(10, 0, -1)),  # From 10 to 1
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1

class RelationalMobility(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2']

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1

class Circle(Page):
    form_model = 'player'
    form_fields = ['self_other']

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1

class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box']

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1

class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        return {
            'participation_fee': player.session.config['participation_fee'],
        }

class ProlificLink(Page):
    """
    This page redirects pp to prolific automatically with a javascript (don't forget to put paste the correct link!).
    There is a short text, the completion code and the link in case it is not automatic.
    """
    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True


page_sequence = [Demographics,
                 Ladder,
                 Circle,
                 RelationalMobility,
                 CommentBox,
                 Payment,
                 ProlificLink]
