import random
import os
import pygame
from enum import Enum


class CardPosition(Enum):
    FACE_DOWN = 0
    FACE_UP = 1

class CardSuit(Enum):
    HEART = 1
    DIAMOND = 2
    SPADE = 3
    CLUB = 4

class CardColor(Enum):
    RED = 0,
    BLACK = 1


class Card:

    def __init__(self, name: str, surface: pygame.Surface):
        self.name = name
        self.surface = surface
        self.current_tableau = None
        self.rect = self.surface.get_rect()
        self.position = CardPosition.FACE_DOWN
        self.linked_cards = []

        if "hearts" in self.name:
            self.suit = CardSuit.HEART
            self.color = CardColor.RED
        if "diamonds" in self.name:
            self.suit = CardSuit.DIAMOND
            self.color = CardColor.RED
        if "spades" in self.name:
            self.suit = CardSuit.SPADE
            self.color = CardColor.BLACK
        if "clubs" in self.name:
            self.suit = CardSuit.CLUB
            self.color = CardColor.BLACK

        if self.name[0].isdigit():
            if self.name[:2].isdigit():
                self.rank = int(self.name[:2])
            else:
                self.rank = int(self.name[0])
        else:
            if self.name.startswith("ace"):
                self.rank = 1
            elif self.name.startswith("jack"):
                self.rank = 11
            elif self.name.startswith("queen"):
                self.rank = 12
            elif self.name.startswith("king"):
                self.rank = 13

    def set_tableau(self, current_tableau):
        self.current_tableau = current_tableau

def is_valid_move(top: Card, bottom: Card) -> bool:

    if bottom.linked_cards:
        bottom = bottom.linked_cards[-1]

    if bottom.rank == top.rank + 1 and bottom.color != top.color:
        return True
    else:
        return False


def create_deck(directory: str) -> list[Card]:
    cards = []
    for filename in os.listdir(directory):
        image_surface = pygame.image.load(os.path.join(directory, filename)).convert_alpha()
        image_surface = pygame.transform.scale(image_surface, (100, 150))
        cards.append(Card(os.path.splitext(filename)[0], image_surface))

    random.shuffle(cards)
    return cards


def deal(cards: list[Card]):
    tableaus = [[], [], [], [], [], [], []]

    for x in range(0, 7, 1):
        for y in range(1, x+2, 1):
            dealt_card = cards.pop(0)
            # On last iteration, turn last card up
            if x + 1 == y:
                dealt_card.position = CardPosition.FACE_UP

            dealt_card.rect.x = 50 + (x * 100) + (20 * x)
            dealt_card.rect.y = 250 + (y * 20)
            dealt_card.current_tableau = x
            tableaus[x].append(dealt_card)

    return tableaus, cards


def link_cards(cards: list[Card]):

    if len(cards) == 1:
        return
    else:
        main_card = cards[0]
        for card in cards[1:]:
            main_card.linked_cards.append(card)
        link_cards(cards[1:])


def unlink_cards(cards: list[Card]):
    for card in cards:
        card.linked_cards = []