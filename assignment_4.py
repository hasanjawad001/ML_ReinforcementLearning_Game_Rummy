import random
from functools import reduce
from collections import defaultdict
import numpy as np
from copy import copy
# %matplotlib inline

SUIT = ['H','S','D','C']
RANK = ['A', '2', '3', '4', '5','6','7']
RANK_VALUE = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'Q': 10, 'K': 10}


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.rank_to_val = RANK_VALUE[self.rank]

    def __str__(self):
        return f'{self.rank}{self.suit}'

    def __repr__(self):
        return f'{self.rank}{self.suit}'

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


class Deck:
    def __init__(self, packs):
        self.packs = packs
        self.cards = []
        for pack in range(0, packs):
            for suit in SUIT:
                for rank in RANK:
                    self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        card = self.cards[0]
        self.cards.pop(0)
        return card


class Player:
    """
        Player class to create a player object.
        eg: player = Player("player1", list(), isBot = False)
        Above declaration will be for your agent.
        All the player names should be unique or else you will get error.

    """

    def __init__(self, name, stash=list(), isBot=False, points=0, conn=None):
        self.stash = stash
        self.name = name
        self.game = None
        self.isBot = isBot
        self.points = points
        self.conn = conn

    def deal_card(self, card):
        try:
            self.stash.append(card)
            if len(self.stash) > self.game.cardsLength + 1:
                raise ValueError('Cannot have cards greater than ')
        except ValueError as err:
            print(err.args)

    def drop_card(self, card):
        self.stash.remove(card)
        self.game.add_pile(card)
        return -1

    def meld(self):
        card_hash = defaultdict(list)
        for card in self.stash:
            card_hash[card.rank].append(card)
        melded_card_ranks = []
        for (card_rank, meld_cards) in card_hash.items():
            if len(meld_cards) >= 3:
                self.game.meld.append(meld_cards)
                melded_card_ranks.append(card_rank)
                for card in meld_cards:
                    self.stash.remove(card)

        for card_rank in melded_card_ranks:
            card_hash.pop(card_rank)
        return len(melded_card_ranks) > 0

    def stash_score(self):
        score = 0
        for card in self.stash:
            score += RANK_VALUE[card.rank]
        return score

    def get_info(self, debug):
        if debug:
            print(
                f'Player Name : {self.name} \n Stash Score: {self.stash_score()} \n Stash : {", ".join(str(x) for x in self.stash)}')
        card_ranks = []
        card_suits = []
        pileset = None
        pile = None
        for card in self.stash:
            card_ranks.append(RANK_VALUE[card.rank])
            card_suits.append(card.suit)
        if len(self.game.pile) > 0:
            return {
                "Stash Score": self.stash_score(),
                "CardSuit": card_suits,
                "CardRanks": card_ranks,
                "PileRank": self.game.pile[-1].rank,
                "PileSuit": self.game.pile[-1].suit
            }

        return {
            "Stash Score": self.stash_score(),
            "CardSuit": card_suits,
            "CardRanks": card_ranks
        }


class RummyAgent():
    """
    Simple Rummy Environment

    Simple Rummy is a game where you need to make all the cards in your hand same before your opponent does.
    Here you are given 3 cards in your hand/stash to play.
    For the first move you have to pick a card from the deck or from the pile.
    The card in deck would be random but you can see the card from the pile.
    In the next move you will have to drop a card from your hand.
    Your goal is to collect all the cards of the same rank.
    Higher the rank of the card, the higher points you lose in the game.
    You need to keep the stash score low. Eg, if you can AH,7S,5D your strategy would be to either find the first pair of the card or by removing the highest card in the deck.
    You only have 20 turns to either win the same or collect low scoring card.
    You can't see other players cards or their stash scores.

    Parameters
    ====
    players: Player objects which will play the game.
    max_card_length : Number of cards each player can have
    max_turns: Number of turns in a rummy game
    """

    def __init__(self, players, max_card_length=5, max_turns=20):
        self.max_card_length = max_card_length
        self.max_turns = max_turns
        self.reset(players)

    def update_player_cards(self, players):
        for player in players:
            player = Player(player.name, list(), isBot=player.isBot, points=player.points, conn=player.conn)
            stash = []
            for i in range(self.max_card_length):
                player.stash.append(self.deck.draw_card())
            player.game = self
            self.players.append(player)
        self.pile = [self.deck.draw_card()]

    def add_pile(self, card):
        if len(self.deck.cards) == 0:
            self.deck.cards.extend(self.pile)
            self.deck.shuffle()
            self.pile = []
        self.pile.append(card)

    def pick_card(self, player, action):
        before_unique_rank_list = list(set([card.rank_to_val for card in player.stash]))
        before_unique_length = len(before_unique_rank_list)
        ss_before = int(player.stash_score())
        if action == 0:
            self.pick_from_pile(player)
        else:
            self.pick_from_deck(player)
        after_unique_rank_list = list(set([card.rank_to_val for card in player.stash]))
        after_unique_length = len(after_unique_rank_list)
        ss_after = int(player.stash_score())
        ss_delta = ss_after - ss_before

        s = [player.stash[0].rank_to_val, player.stash[1].rank_to_val, player.stash[2].rank_to_val, player.stash[3].rank_to_val]

        if player.meld():
            reward = 100
        elif after_unique_length == before_unique_length:
            reward = 80
        else:
            reward = -3 * ss_delta
        return {"reward": reward, "state": s}



    def pick_from_pile(self, player):
        card = self.pile[-1]
        self.pile.pop()
        return player.stash.append(card)

    def pick_from_deck(self, player):
        return player.stash.append(self.deck.draw_card())

    def get_player(self, player_name):
        return_player = [player for player in self.players if player.name == player_name]
        if len(return_player) != 1:
            print("Invalid Player")
            return None
        else:
            return return_player[0]

    def drop_card(self, player, card):
        before_unique_rank_list = list(set([card.rank_to_val for card in player.stash]))
        before_unique_length = len(before_unique_rank_list)
        ss_before = int(player.stash_score())
        player.drop_card(card)
        after_unique_rank_list = list(set([card.rank_to_val for card in player.stash]))
        after_unique_length = len(after_unique_rank_list)
        ss_after = int(player.stash_score())
        ss_delta = ss_after - ss_before

        if before_unique_length  == after_unique_length:
            reward = -80
        else:
            reward = -3 * ss_delta
        return {"reward": reward}

    def computer_play(self, player):
        # Gets a card from deck or pile
        if random.randint(0, 1) == 1:
            self.pick_from_pile(player)
        else:
            self.pick_from_deck(player)

        # tries to meld if it can
        #         if random.randint(0,10) > 5 :
        player.meld()

        # removes a card from the stash
        if len(player.stash) != 0:
            card = player.stash[(random.randint(0, len(player.stash) - 1))]
            player.drop_card(card)

    def play(self):
        for player in self.players:
            if len(player.stash) == 0:
                return True
        if self.max_turns <= 0:
            return True
        return False

    def _update_turn(self):
        self.max_turns -= 1

    def reset(self, players, max_turns=20):
        self.players = []
        self.deck = Deck(1)
        self.deck.shuffle()
        self.meld = []
        self.pile = []
        self.max_turns = max_turns
        self.update_player_cards(players)

def coord_convert(s, sz):
    return [s[1], sz[0]-s[0]-1]


class RLAgent:
    """
        Reinforcement Learning Agent Model for training/testing
        with Tabular function approximation

    """

    def printQ(self):
        for i in range(7):
            for j in range(7):
                for k in range(7):
                    for l in range(7):
                        for m in range(2):
                            for n in range(4):
                                if self.Q[i,j,k,l,m,n] > 0:
                                    print(i,j,k,l,m,n)

    def __init__(self, env):
        self.env = env
        self.states = self.get_states()
        self.actions = self.get_actions()
        self.n_a = len(self.actions)
        self.n_s = len(self.states)
        self.Q = np.zeros(( len(RANK), len(RANK), len(RANK), len(RANK), len([0,1]), len([0,1,2,3])  ))


    def get_states(self):
        states = []
        for fi in RANK:
            for s in RANK:
                for t in RANK:
                    for fo in RANK:
                        state = [
                            RANK_VALUE[fi],
                            RANK_VALUE[s],
                            RANK_VALUE[t],
                            RANK_VALUE[fo]
                        ]
                        states.append(state)
        return states

    def get_actions(self):
        pick = list(range(0, 2))
        drop = list(range(0, 4))
        actions = []
        for p in pick:
            for d in drop:
                action = [p,d]
                actions.append(action)
        return actions

    def epsilon_greed(self, epsilon, s, type):
        i0 = s[0] - 1
        i1 = s[1] - 1
        i2 = s[2] - 1
        i3 = s[3] - 1
        if type == 'pick':
            if np.random.uniform() < epsilon:
                index = np.random.randint(2)
            else:
                index = np.where(self.Q[i0, i1, i2, i3, :, 0] == np.max(self.Q[i0, i1, i2, i3, :, 0]))[0][0]
        else:
            if np.random.uniform() < epsilon:
                index = np.random.randint(4)
            else:
                index = np.where(self.Q[i0, i1, i2, i3, 0, :] == np.max(self.Q[i0, i1, i2, i3, 0, :]))[0][0]
        return index


    def train(self):
        maxiter = 10000
        w=0
        debug = True
        for j in range(maxiter):
            # self.printQ()
            for player in rummy.players:
                player.points = player.stash_score()

            rummy.reset(rummy.players)
            random.shuffle(rummy.players)
            # int i = 0
            if debug:
                print(f'**********************************\n\t\tGame Starts : {j}\n***********************************')
            while not rummy.play():
                rummy._update_turn()
                print(rummy.max_turns)
                for player in rummy.players:
                    if player.isBot:
                        if rummy.play():
                            continue
                        if debug:
                            print(f'{player.name} Plays')
                        rummy.computer_play(player)
                        if debug:
                            player.get_info(debug)
                            if player.stash == 0:
                                print(f'{player.name} wins the round')

                    else:
                        if rummy.play():
                            continue
                        if debug:
                            print(f'{player.name} Plays')
                        player_info = player.get_info(debug)
                        #1s: pick ###################################################################################
                        # action_taken = np.random.choice(1)
                        i0_rank_to_val =player.stash[0].rank_to_val
                        i1_rank_to_val =player.stash[1].rank_to_val
                        i2_rank_to_val =player.stash[2].rank_to_val
                        card_pile_rank_to_val = rummy.pile[-1].rank_to_val
                        s = [
                            i0_rank_to_val,
                            i1_rank_to_val,
                            i2_rank_to_val,
                            card_pile_rank_to_val
                        ]
                        a = self.epsilon_greed(0.05, s, type='pick')
                        if debug:
                            print(f'Card in pile {player_info["PileSuit"]}{player_info["PileRank"]}')
                        result_1 = rummy.pick_card(player, a)
                        r1 = result_1["reward"]
                        s1 = result_1["state"]
                        a1 = self.epsilon_greed(0.05, s1, type='drop')
                        self.Q[s[0] - 1, s[1] - 1, s[2] - 1, s[3] - 1, a, :] += 0.1 * (
                                r1 + 0.99 * self.Q[s1[0] - 1, s1[1] - 1, s1[2] - 1, s1[3] - 1, 0, a1] - self.Q[
                            s[0] - 1, s[1] - 1, s[2] - 1, s[3] - 1, a, 0]
                        )
                        s = s1
                        a = a1
                        # self.printQ()
                        #1e: pick ###################################################################################
                        if debug:
                            print(f'{player.name} takes action {a}')
                        # player stash will have no cards if the player has melded them
                        # When you have picked up a card and you have drop it since the remaining cards have been melded.
                        if len(player.stash) == 1:
                            rummy.drop_card(player, player.stash[0])
                            if debug:
                                print(f'{player.name} Wins the round')
                                w+=1

                        elif len(player.stash) != 0:

                            player_info = player.get_info(debug)
                            # s = player_info['CardRanks']
                            #2s: drop ###################################################################################
                            # action_taken = np.random.choice(4)
                            # s = [player.stash[0].rank_to_val, player.stash[1].rank_to_val, player.stash[2].rank_to_val, player.stash[3].rank_to_val]
                            # a = self.epsilon_greed(0.1, s, type='drop')
                            card = player.stash[a]
                            if debug:
                                print(f'{player.name} drops card {card}')
                            result_1 = rummy.drop_card(player, card)
                            r1 = result_1["reward"]
                            card_pile_rank_to_val = rummy.pile[-1].rank_to_val
                            s1 = [
                                player.stash[0].rank_to_val,
                                player.stash[1].rank_to_val,
                                player.stash[2].rank_to_val,
                                card_pile_rank_to_val
                            ]
                            a1 = self.epsilon_greed(0.05, s1, type='pick')
                            self.Q[s[0] - 1, s[1] - 1, s[2] - 1, s[3] - 1, :, a] += 0.1 * (
                                    r1 + 0.99 * self.Q[s1[0] - 1, s1[1] - 1, s1[2] - 1, s1[3] - 1, a1, 0] -
                                    self.Q[s[0] - 1, s[1] - 1, s[2] - 1, s[3] - 1, 0, a]
                            )
                            s=s1
                            a=a1
                            #2e: drop ###################################################################################
                        #                             pdb.set_trace()
                        else:
                            if debug:
                                print(f'{player.name} Wins the round')
                                w+=1
                        if debug:
                            player.get_info(debug)
        print('====================================================', w)
        return self.Q

    def test(self):
        return None

if __name__ == '__main__':
    p1 = Player('jawad', list())
    p2 = Player('comp1', list(), isBot=True)
    rummy = RummyAgent([p1, p2], max_card_length=3, max_turns=20)
    r = RLAgent(rummy)
    r.train()
    r.test()

