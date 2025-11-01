from otree.api import *


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


class C(BaseConstants):
    NAME_IN_URL = 'setup_app'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass

class ProcessUrlParams(Page):

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        raw_label = participant.label

        gid_value, sname_value = parse_participant_label(raw_label)

        if gid_value and sname_value:
            participant.GID = gid_value
            participant.sname = sname_value
            print(
                f"-> SUCCESS (in setup_app): Participant {participant.id_in_session} - Parsed GID='{participant.GID}' and sname='{participant.sname}'")
        else:
            participant.GID = "INVALID_LABEL_FORMAT"
            participant.sname = "INVALID_LABEL_FORMAT"
            print(
                f"-> ERROR (in setup_app): Participant {participant.id_in_session} - Could not parse label '{raw_label}'.")


page_sequence = [ProcessUrlParams]