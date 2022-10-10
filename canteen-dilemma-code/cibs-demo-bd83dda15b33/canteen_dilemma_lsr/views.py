from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
import random


class WaitForPartnerPage(WaitPage):
    group_by_arrival_time = True

    def is_displayed(self):
        return self.round_number == 1

    def after_all_players_arrive(self):
        # Groups are generated here, because we don't have the group object
        # before get_players_for_group has created a group
        for group in self.group.in_rounds(1, Constants.num_rounds):
            group.end_game = False
            p1 = group.get_player_by_id(1)
            p2 = group.get_player_by_id(2)

            # find a random arrival time for the player
            p1.arrival_time = random.choice(Constants.arrival_times[5:-5])

            # set the arrival time of the colleague
            indeks = Constants.arrival_times.index(p1.arrival_time)
            temp = [Constants.arrival_times[indeks - 5], Constants.arrival_times[indeks],
                    Constants.arrival_times[indeks + 5]]
            p2.arrival_time = random.choice(temp)


class Introduction(Page):
    timeout_seconds = 180

    def is_displayed(self):
        return self.round_number == 1 and not self.group.is_game_over()


class Choice(Page):
    # timeout_seconds = 30

    def is_displayed(self):
        return not self.group.is_game_over()

    form_model = models.Player
    form_fields = ['choice']

    def vars_for_template(self):
        self.subsession.day()
        return {
            'player_in_previous_rounds': self.player.in_previous_rounds()
        }


class Certainty(Page):
    # timeout_seconds = 30

    def is_displayed(self):
        return not self.group.is_game_over() and random.random() < Constants.p_certainty_prompt

    form_model = models.Player
    form_fields = ['certainty']


class ResultsWaitPage(WaitPage):
    def is_displayed(self):
        return not self.group.is_game_over()

    def after_all_players_arrive(self):
        if not self.group.is_game_lost():
            self.group.set_payoffs()


class GameLost(Page):
    def is_displayed(self):
        # Show this page only when the game has just been lost
        return self.group.is_game_just_lost()

    def vars_for_template(self):
        p1, p2 = self.group.get_players()
        if p1.arrival_time >= 9.00 or p2.arrival_time >= 9.00:
            too_late = True
        else:
            too_late = False
        return {
            'player_in_all_rounds': self.player.in_all_rounds(),
            'too_late': too_late,
            'tot_payoff': Constants.endowment + self.player.participant.payoff,
        }




class RunningResults(Page):
    # timeout_seconds = 30

    def is_displayed(self):
        return not self.group.is_game_over()

    def vars_for_template(self):

        p1, p2 = self.group.get_players()

        if p1.choice != p2.choice:
            lost = True
        else:
            lost = False

        if p1.arrival_time >= 9.00 or p2.arrival_time >= 9.00:
            too_late = True
        else:
            too_late = False

        player_for_completed_rounds = [player for player in self.player.in_all_rounds() if player.choice is not None]

        return {
            'too_late': too_late,
            'lost': lost,
            'payoff_in_this_phase': sum([p.payoff for p in player_for_completed_rounds]),
            'tot_payoff': Constants.endowment + self.player.participant.payoff,
            'player_in_all_rounds': player_for_completed_rounds,
        }



class Strategy(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds and not self.group.is_game_over()
    form_model = models.Player
    form_fields = ['strategy_canteen_dilemma']



class Debrief(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    def vars_for_template(self):
        player_for_completed_rounds = [player for player in self.player.in_all_rounds() if player.choice is not None]

        return {
            'payoff_in_this_phase': sum([p.payoff for p in player_for_completed_rounds]),
        }

class PaymentInfo(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    def vars_for_template(self):
        player_for_completed_rounds = [player for player in self.player.in_all_rounds() if player.choice is not None]

        return {
            'payoff_in_this_phase': sum([p.payoff for p in player_for_completed_rounds]),
        }


page_sequence = [
    WaitForPartnerPage,
    Introduction,
    Choice,
    Certainty,
    ResultsWaitPage,
    GameLost,
    RunningResults,
    Strategy,
    Debrief
]
