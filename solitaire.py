#!/usr/bin/env python

"""solitaire.py: A simple game of solitaire using the pygame engine"""

import sys
from card import *


def get_path(filename):
    """Gets the current path for an executable built with pyinstaller"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename


pygame.init()

WINDOW_WIDTH = 925
WINDOW_HEIGHT = 700
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Solitaire")

DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)

deck = create_deck(get_path("assets/card_faces"))
card_back_image = pygame.image.load(get_path("assets/card_back_red.png")).convert_alpha()
card_back_image = pygame.transform.scale(card_back_image, (100, 150))
card_back = Card("card_back", card_back_image)

foundation_piles = [[], [], [], []]
foundation_pile1_rect = None
foundation_pile2_rect = None
foundation_pile3_rect = None
foundation_pile4_rect = None

discard_pile = []
tableau_piles, stock_pile = deal(deck)

king_placeholder_locations = [(tableau_piles[0][0].rect.x, tableau_piles[0][0].rect.y),
                              (tableau_piles[1][0].rect.x, tableau_piles[1][0].rect.y),
                              (tableau_piles[2][0].rect.x, tableau_piles[2][0].rect.y),
                              (tableau_piles[3][0].rect.x, tableau_piles[3][0].rect.y),
                              (tableau_piles[4][0].rect.x, tableau_piles[4][0].rect.y),
                              (tableau_piles[5][0].rect.x, tableau_piles[5][0].rect.y),
                              (tableau_piles[6][0].rect.x, tableau_piles[6][0].rect.y)]

king_placeholder1_rect = None
king_placeholder2_rect = None
king_placeholder3_rect = None
king_placeholder4_rect = None
king_placeholder5_rect = None
king_placeholder6_rect = None
king_placeholder7_rect = None

draggable_cards = [card for pile in tableau_piles for card in pile if card.position == CardPosition.FACE_UP]

currently_dragging_card = False
card_being_dragged = None
reset_stock_pile_circle = None
original_dragging_x = 0
original_dragging_y = 0

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if card_back.rect.collidepoint(mouse_x, mouse_y):

                    if len(discard_pile) > 0:
                        draggable_cards.remove(discard_pile[-1])

                    for z in range(1, 4, 1):
                        if len(stock_pile) > 0:
                            discarded_card = stock_pile.pop(0)
                            discarded_card.rect.x = 125 + z * 20
                            discarded_card.rect.y = 25
                            discarded_card.position = CardPosition.FACE_UP
                            discard_pile.append(discarded_card)

                    if len(discard_pile) > 0:
                        draggable_cards.append(discard_pile[-1])

                if reset_stock_pile_circle is not None and reset_stock_pile_circle.collidepoint(pygame.mouse.get_pos()):
                    if discard_pile:
                        draggable_cards.remove(discard_pile[-1])
                        stock_pile = discard_pile
                        for card in list(stock_pile):
                            card.position = CardPosition.FACE_DOWN
                            card.rect.x = 25
                            card.rect.y = 25
                        discard_pile = []
                        reset_stock_pile_circle = None

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if currently_dragging_card:
                    for card in draggable_cards:
                        if (card_being_dragged.rect.colliderect(card.rect) and
                                is_valid_move(card_being_dragged, card) and
                                card not in discard_pile and
                                card not in foundation_piles[0] and
                                card not in foundation_piles[1] and
                                card not in foundation_piles[2] and
                                card not in foundation_piles[3]):

                            offset = len(card.linked_cards) * 20 + 20
                            for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                linked_card.rect.x = card.rect.x
                                linked_card.rect.y = card.rect.y + offset + (20 * (i + 1))
                            card_being_dragged.rect.x = card.rect.x
                            card_being_dragged.rect.y = card.rect.y + offset

                            if card_being_dragged.current_tableau is None:
                                discard_pile.remove(card_being_dragged)
                                if len(discard_pile) > 0:
                                    draggable_cards.append(discard_pile[-1])
                                card_being_dragged.set_tableau(card.current_tableau)
                                tableau_piles[card.current_tableau].append(card_being_dragged)
                            else:
                                old_tableau = card_being_dragged.current_tableau
                                tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)
                                card_being_dragged.set_tableau(card.current_tableau)
                                tableau_piles[card.current_tableau].append(card_being_dragged)

                                for linked_card in card_being_dragged.linked_cards:
                                    tableau_piles[linked_card.current_tableau].remove(linked_card)
                                    linked_card.set_tableau(card.current_tableau)
                                    tableau_piles[card.current_tableau].append(linked_card)


                                if len(tableau_piles[old_tableau]) > 0:
                                    if tableau_piles[old_tableau][-1].position != CardPosition.FACE_UP:
                                        # Flip over new card on old tableau pile
                                        tableau_piles[old_tableau][-1].position = CardPosition.FACE_UP
                                        draggable_cards.append(tableau_piles[old_tableau][-1])
                                    else:
                                        # Orphan cards case; reset links
                                        orphan_cards = [c for c in tableau_piles[old_tableau] if c.position == CardPosition.FACE_UP]
                                        unlink_cards(orphan_cards)
                                        link_cards(orphan_cards)

                            # Find the back of the stack of cards
                            back_card_index = 0
                            for i, tableau_card in enumerate(tableau_piles[card.current_tableau]):
                                if tableau_card.position == CardPosition.FACE_UP:
                                    back_card_index = i
                                    break

                            unlink_cards(tableau_piles[card.current_tableau][back_card_index:])
                            link_cards(tableau_piles[card.current_tableau][back_card_index:])

                            currently_dragging_card = False
                            card_being_dragged = None
                            break
                    else:
                        if foundation_pile1_rect.colliderect(card_being_dragged.rect):
                            if not foundation_piles[0]:
                                if card_being_dragged.rank == 1 and not card_being_dragged.linked_cards:

                                    card_being_dragged.rect.x = foundation_pile1_rect.x
                                    card_being_dragged.rect.y = foundation_pile1_rect.y

                                    foundation_piles[0].append(card_being_dragged)
                                    if card_being_dragged in discard_pile:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        # Flip over new card on old tableau pile if next card on old pile is face down
                                        # Else, card was split from a stack on the old tableau and the cards need to be re-linked
                                        if len(tableau_piles[card_being_dragged.current_tableau]) > 0:
                                            if tableau_piles[card_being_dragged.current_tableau][-1].position == CardPosition.FACE_DOWN:
                                                tableau_piles[card_being_dragged.current_tableau][-1].position = CardPosition.FACE_UP
                                                draggable_cards.append(tableau_piles[card_being_dragged.current_tableau][-1])
                                            else:
                                                face_up_cards = [tableau_card for tableau_card in tableau_piles[card_being_dragged.current_tableau] if tableau_card.position == CardPosition.FACE_UP]
                                                unlink_cards(face_up_cards)
                                                link_cards(face_up_cards)

                                    card_being_dragged.set_tableau(None)
                                    draggable_cards.remove(card_being_dragged)

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (
                                                    i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None

                            elif foundation_piles[0]:
                                if (card_being_dragged.rank == foundation_piles[0][-1].rank + 1 and
                                    card_being_dragged.suit == foundation_piles[0][-1].suit and
                                    not card_being_dragged.linked_cards):

                                    card_being_dragged.rect.x = foundation_pile1_rect.x
                                    card_being_dragged.rect.y = foundation_pile1_rect.y

                                    foundation_piles[0].append(card_being_dragged)
                                    if card_being_dragged in discard_pile:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        # Flip over new card on old tableau pile if next card on old pile is face down
                                        # Else, card was split from a stack on the old tableau and the cards need to be re-linked
                                        if len(tableau_piles[card_being_dragged.current_tableau]) > 0:
                                            if tableau_piles[card_being_dragged.current_tableau][-1].position == CardPosition.FACE_DOWN:
                                                tableau_piles[card_being_dragged.current_tableau][-1].position = CardPosition.FACE_UP
                                                draggable_cards.append(tableau_piles[card_being_dragged.current_tableau][-1])
                                            else:
                                                face_up_cards = [tableau_card for tableau_card in tableau_piles[card_being_dragged.current_tableau] if tableau_card.position == CardPosition.FACE_UP]
                                                unlink_cards(face_up_cards)
                                                link_cards(face_up_cards)

                                    card_being_dragged.set_tableau(None)
                                    draggable_cards.remove(card_being_dragged)

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None

                        elif foundation_pile2_rect.colliderect(card_being_dragged.rect):
                            if not foundation_piles[1]:
                                if card_being_dragged.rank == 1 and not card_being_dragged.linked_cards:

                                    card_being_dragged.rect.x = foundation_pile2_rect.x
                                    card_being_dragged.rect.y = foundation_pile2_rect.y

                                    foundation_piles[1].append(card_being_dragged)
                                    if card_being_dragged in discard_pile:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        # Flip over new card on old tableau pile if next card on old pile is face down
                                        # Else, card was split from a stack on the old tableau and the cards need to be re-linked
                                        if len(tableau_piles[card_being_dragged.current_tableau]) > 0:
                                            if tableau_piles[card_being_dragged.current_tableau][-1].position == CardPosition.FACE_DOWN:
                                                tableau_piles[card_being_dragged.current_tableau][-1].position = CardPosition.FACE_UP
                                                draggable_cards.append(tableau_piles[card_being_dragged.current_tableau][-1])
                                            else:
                                                face_up_cards = [tableau_card for tableau_card in tableau_piles[card_being_dragged.current_tableau] if tableau_card.position == CardPosition.FACE_UP]
                                                unlink_cards(face_up_cards)
                                                link_cards(face_up_cards)

                                    card_being_dragged.set_tableau(None)
                                    draggable_cards.remove(card_being_dragged)

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (
                                                    i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None

                            elif foundation_piles[1]:
                                if (card_being_dragged.rank == foundation_piles[1][-1].rank + 1 and
                                    card_being_dragged.suit == foundation_piles[1][-1].suit and
                                    not card_being_dragged.linked_cards):

                                    card_being_dragged.rect.x = foundation_pile2_rect.x
                                    card_being_dragged.rect.y = foundation_pile2_rect.y

                                    foundation_piles[1].append(card_being_dragged)
                                    if card_being_dragged in discard_pile:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        # Flip over new card on old tableau pile if next card on old pile is face down
                                        # Else, card was split from a stack on the old tableau and the cards need to be re-linked
                                        if len(tableau_piles[card_being_dragged.current_tableau]) > 0:
                                            if tableau_piles[card_being_dragged.current_tableau][-1].position == CardPosition.FACE_DOWN:
                                                tableau_piles[card_being_dragged.current_tableau][-1].position = CardPosition.FACE_UP
                                                draggable_cards.append(tableau_piles[card_being_dragged.current_tableau][-1])
                                            else:
                                                face_up_cards = [tableau_card for tableau_card in tableau_piles[card_being_dragged.current_tableau] if tableau_card.position == CardPosition.FACE_UP]
                                                unlink_cards(face_up_cards)
                                                link_cards(face_up_cards)

                                    card_being_dragged.set_tableau(None)
                                    draggable_cards.remove(card_being_dragged)

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None


                        elif foundation_pile3_rect.colliderect(card_being_dragged.rect):
                            if not foundation_piles[2]:
                                if card_being_dragged.rank == 1 and not card_being_dragged.linked_cards:

                                    card_being_dragged.rect.x = foundation_pile3_rect.x
                                    card_being_dragged.rect.y = foundation_pile3_rect.y

                                    foundation_piles[2].append(card_being_dragged)
                                    if card_being_dragged in discard_pile:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        # Flip over new card on old tableau pile if next card on old pile is face down
                                        # Else, card was split from a stack on the old tableau and the cards need to be re-linked
                                        if len(tableau_piles[card_being_dragged.current_tableau]) > 0:
                                            if tableau_piles[card_being_dragged.current_tableau][-1].position == CardPosition.FACE_DOWN:
                                                tableau_piles[card_being_dragged.current_tableau][-1].position = CardPosition.FACE_UP
                                                draggable_cards.append(tableau_piles[card_being_dragged.current_tableau][-1])
                                            else:
                                                face_up_cards = [tableau_card for tableau_card in tableau_piles[card_being_dragged.current_tableau] if tableau_card.position == CardPosition.FACE_UP]
                                                unlink_cards(face_up_cards)
                                                link_cards(face_up_cards)

                                    card_being_dragged.set_tableau(None)
                                    draggable_cards.remove(card_being_dragged)

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (
                                                    i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None

                            elif foundation_piles[2]:
                                if (card_being_dragged.rank == foundation_piles[2][-1].rank + 1 and
                                    card_being_dragged.suit == foundation_piles[2][-1].suit and
                                    not card_being_dragged.linked_cards):

                                    card_being_dragged.rect.x = foundation_pile3_rect.x
                                    card_being_dragged.rect.y = foundation_pile3_rect.y

                                    foundation_piles[2].append(card_being_dragged)
                                    if card_being_dragged in discard_pile:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        # Flip over new card on old tableau pile if next card on old pile is face down
                                        # Else, card was split from a stack on the old tableau and the cards need to be re-linked
                                        if len(tableau_piles[card_being_dragged.current_tableau]) > 0:
                                            if tableau_piles[card_being_dragged.current_tableau][-1].position == CardPosition.FACE_DOWN:
                                                tableau_piles[card_being_dragged.current_tableau][-1].position = CardPosition.FACE_UP
                                                draggable_cards.append(tableau_piles[card_being_dragged.current_tableau][-1])
                                            else:
                                                face_up_cards = [tableau_card for tableau_card in tableau_piles[card_being_dragged.current_tableau] if tableau_card.position == CardPosition.FACE_UP]
                                                unlink_cards(face_up_cards)
                                                link_cards(face_up_cards)

                                    card_being_dragged.set_tableau(None)
                                    draggable_cards.remove(card_being_dragged)

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None

                        elif foundation_pile4_rect.colliderect(card_being_dragged.rect):
                            if not foundation_piles[3]:
                                if card_being_dragged.rank == 1 and not card_being_dragged.linked_cards:

                                    card_being_dragged.rect.x = foundation_pile4_rect.x
                                    card_being_dragged.rect.y = foundation_pile4_rect.y

                                    foundation_piles[3].append(card_being_dragged)
                                    if card_being_dragged in discard_pile:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        # Flip over new card on old tableau pile if next card on old pile is face down
                                        # Else, card was split from a stack on the old tableau and the cards need to be re-linked
                                        if len(tableau_piles[card_being_dragged.current_tableau]) > 0:
                                            if tableau_piles[card_being_dragged.current_tableau][-1].position == CardPosition.FACE_DOWN:
                                                tableau_piles[card_being_dragged.current_tableau][-1].position = CardPosition.FACE_UP
                                                draggable_cards.append(tableau_piles[card_being_dragged.current_tableau][-1])
                                            else:
                                                face_up_cards = [tableau_card for tableau_card in tableau_piles[card_being_dragged.current_tableau] if tableau_card.position == CardPosition.FACE_UP]
                                                unlink_cards(face_up_cards)
                                                link_cards(face_up_cards)

                                    card_being_dragged.set_tableau(None)
                                    draggable_cards.remove(card_being_dragged)

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (
                                                    i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None

                            elif foundation_piles[3]:
                                if (card_being_dragged.rank == foundation_piles[3][-1].rank + 1 and
                                    card_being_dragged.suit == foundation_piles[3][-1].suit and
                                    not card_being_dragged.linked_cards):

                                    card_being_dragged.rect.x = foundation_pile4_rect.x
                                    card_being_dragged.rect.y = foundation_pile4_rect.y

                                    foundation_piles[3].append(card_being_dragged)
                                    if card_being_dragged in discard_pile:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        # Flip over new card on old tableau pile if next card on old pile is face down
                                        # Else, card was split from a stack on the old tableau and the cards need to be re-linked
                                        if len(tableau_piles[card_being_dragged.current_tableau]) > 0:
                                            if tableau_piles[card_being_dragged.current_tableau][-1].position == CardPosition.FACE_DOWN:
                                                tableau_piles[card_being_dragged.current_tableau][-1].position = CardPosition.FACE_UP
                                                draggable_cards.append(tableau_piles[card_being_dragged.current_tableau][-1])
                                            else:
                                                face_up_cards = [tableau_card for tableau_card in tableau_piles[card_being_dragged.current_tableau] if tableau_card.position == CardPosition.FACE_UP]
                                                unlink_cards(face_up_cards)
                                                link_cards(face_up_cards)

                                    card_being_dragged.set_tableau(None)
                                    draggable_cards.remove(card_being_dragged)

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None


                        elif not tableau_piles[0] or not tableau_piles[1] or not tableau_piles[2] or not tableau_piles[3] or not tableau_piles[4] or not tableau_piles[5] or not tableau_piles[6]:
                            if card_being_dragged.rank == 13:

                                if king_placeholder1_rect is not None and card_being_dragged.rect.colliderect(king_placeholder1_rect):

                                    if card_being_dragged.current_tableau is None:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                        card_being_dragged.set_tableau(0)
                                        tableau_piles[0].append(card_being_dragged)

                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        old_tableau = card_being_dragged.current_tableau
                                        card_being_dragged.set_tableau(0)
                                        tableau_piles[0].append(card_being_dragged)
                                        for linked_card in card_being_dragged.linked_cards:
                                            tableau_piles[old_tableau].remove(linked_card)
                                            linked_card.set_tableau(0)
                                            tableau_piles[0].append(linked_card)

                                        # Flip over new card on old tableau pile
                                        if len(tableau_piles[old_tableau]) > 0:
                                            tableau_piles[old_tableau][-1].position = CardPosition.FACE_UP
                                            draggable_cards.append(tableau_piles[old_tableau][-1])

                                        for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                            linked_card.rect.x = king_placeholder1_rect.x
                                            linked_card.rect.y = king_placeholder1_rect.y + 20 * (i + 1)

                                    card_being_dragged.rect.x = king_placeholder1_rect.x
                                    card_being_dragged.rect.y = king_placeholder1_rect.y

                                    currently_dragging_card = False
                                    card_being_dragged = None


                                elif king_placeholder2_rect is not None and card_being_dragged.rect.colliderect(king_placeholder2_rect):

                                    if card_being_dragged.current_tableau is None:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                        card_being_dragged.set_tableau(1)
                                        tableau_piles[1].append(card_being_dragged)

                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        old_tableau = card_being_dragged.current_tableau
                                        card_being_dragged.set_tableau(1)
                                        tableau_piles[1].append(card_being_dragged)
                                        for linked_card in card_being_dragged.linked_cards:
                                            tableau_piles[old_tableau].remove(linked_card)
                                            linked_card.set_tableau(1)
                                            tableau_piles[1].append(linked_card)

                                        # Flip over new card on old tableau pile
                                        if len(tableau_piles[old_tableau]) > 0:
                                            tableau_piles[old_tableau][-1].position = CardPosition.FACE_UP
                                            draggable_cards.append(tableau_piles[old_tableau][-1])

                                        for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                            linked_card.rect.x = king_placeholder2_rect.x
                                            linked_card.rect.y = king_placeholder2_rect.y + 20 * (i + 1)

                                    card_being_dragged.rect.x = king_placeholder2_rect.x
                                    card_being_dragged.rect.y = king_placeholder2_rect.y

                                    currently_dragging_card = False
                                    card_being_dragged = None


                                elif king_placeholder3_rect is not None and card_being_dragged.rect.colliderect(king_placeholder3_rect):

                                    if card_being_dragged.current_tableau is None:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                        card_being_dragged.set_tableau(2)
                                        tableau_piles[2].append(card_being_dragged)

                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        old_tableau = card_being_dragged.current_tableau
                                        card_being_dragged.set_tableau(2)
                                        tableau_piles[2].append(card_being_dragged)
                                        for linked_card in card_being_dragged.linked_cards:
                                            tableau_piles[old_tableau].remove(linked_card)
                                            linked_card.set_tableau(2)
                                            tableau_piles[2].append(linked_card)

                                        # Flip over new card on old tableau pile
                                        if len(tableau_piles[old_tableau]) > 0:
                                            tableau_piles[old_tableau][-1].position = CardPosition.FACE_UP
                                            draggable_cards.append(tableau_piles[old_tableau][-1])

                                        for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                            linked_card.rect.x = king_placeholder3_rect.x
                                            linked_card.rect.y = king_placeholder3_rect.y + 20 * (i + 1)

                                    card_being_dragged.rect.x = king_placeholder3_rect.x
                                    card_being_dragged.rect.y = king_placeholder3_rect.y

                                    currently_dragging_card = False
                                    card_being_dragged = None


                                elif king_placeholder4_rect is not None and card_being_dragged.rect.colliderect(king_placeholder4_rect):

                                    if card_being_dragged.current_tableau is None:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                        card_being_dragged.set_tableau(3)
                                        tableau_piles[3].append(card_being_dragged)

                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        old_tableau = card_being_dragged.current_tableau
                                        card_being_dragged.set_tableau(3)
                                        tableau_piles[3].append(card_being_dragged)
                                        for linked_card in card_being_dragged.linked_cards:
                                            tableau_piles[old_tableau].remove(linked_card)
                                            linked_card.set_tableau(3)
                                            tableau_piles[3].append(linked_card)

                                        # Flip over new card on old tableau pile
                                        if len(tableau_piles[old_tableau]) > 0:
                                            tableau_piles[old_tableau][-1].position = CardPosition.FACE_UP
                                            draggable_cards.append(tableau_piles[old_tableau][-1])

                                        for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                            linked_card.rect.x = king_placeholder4_rect.x
                                            linked_card.rect.y = king_placeholder4_rect.y + 20 * (i + 1)

                                    card_being_dragged.rect.x = king_placeholder4_rect.x
                                    card_being_dragged.rect.y = king_placeholder4_rect.y

                                    currently_dragging_card = False
                                    card_being_dragged = None


                                elif king_placeholder5_rect is not None and card_being_dragged.rect.colliderect(king_placeholder5_rect):

                                    if card_being_dragged.current_tableau is None:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                        card_being_dragged.set_tableau(4)
                                        tableau_piles[4].append(card_being_dragged)

                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        old_tableau = card_being_dragged.current_tableau
                                        card_being_dragged.set_tableau(4)
                                        tableau_piles[4].append(card_being_dragged)
                                        for linked_card in card_being_dragged.linked_cards:
                                            tableau_piles[old_tableau].remove(linked_card)
                                            linked_card.set_tableau(4)
                                            tableau_piles[4].append(linked_card)

                                        # Flip over new card on old tableau pile
                                        if len(tableau_piles[old_tableau]) > 0:
                                            tableau_piles[old_tableau][-1].position = CardPosition.FACE_UP
                                            draggable_cards.append(tableau_piles[old_tableau][-1])

                                        for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                            linked_card.rect.x = king_placeholder5_rect.x
                                            linked_card.rect.y = king_placeholder5_rect.y + 20 * (i + 1)

                                    card_being_dragged.rect.x = king_placeholder5_rect.x
                                    card_being_dragged.rect.y = king_placeholder5_rect.y

                                    currently_dragging_card = False
                                    card_being_dragged = None


                                elif king_placeholder6_rect is not None and card_being_dragged.rect.colliderect(king_placeholder6_rect):

                                    if card_being_dragged.current_tableau is None:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                        card_being_dragged.set_tableau(5)
                                        tableau_piles[5].append(card_being_dragged)

                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        old_tableau = card_being_dragged.current_tableau
                                        card_being_dragged.set_tableau(5)
                                        tableau_piles[5].append(card_being_dragged)
                                        for linked_card in card_being_dragged.linked_cards:
                                            tableau_piles[old_tableau].remove(linked_card)
                                            linked_card.set_tableau(5)
                                            tableau_piles[5].append(linked_card)

                                        # Flip over new card on old tableau pile
                                        if len(tableau_piles[old_tableau]) > 0:
                                            tableau_piles[old_tableau][-1].position = CardPosition.FACE_UP
                                            draggable_cards.append(tableau_piles[old_tableau][-1])

                                        for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                            linked_card.rect.x = king_placeholder6_rect.x
                                            linked_card.rect.y = king_placeholder6_rect.y + 20 * (i + 1)

                                    card_being_dragged.rect.x = king_placeholder6_rect.x
                                    card_being_dragged.rect.y = king_placeholder6_rect.y

                                    currently_dragging_card = False
                                    card_being_dragged = None


                                elif king_placeholder7_rect is not None and card_being_dragged.rect.colliderect(king_placeholder7_rect):

                                    if card_being_dragged.current_tableau is None:
                                        discard_pile.remove(card_being_dragged)
                                        if len(discard_pile) > 0:
                                            draggable_cards.append(discard_pile[-1])
                                        card_being_dragged.set_tableau(6)
                                        tableau_piles[6].append(card_being_dragged)
                                    else:
                                        tableau_piles[card_being_dragged.current_tableau].remove(card_being_dragged)

                                        old_tableau = card_being_dragged.current_tableau
                                        card_being_dragged.set_tableau(6)
                                        tableau_piles[6].append(card_being_dragged)
                                        for linked_card in card_being_dragged.linked_cards:
                                            tableau_piles[old_tableau].remove(linked_card)
                                            linked_card.set_tableau(6)
                                            tableau_piles[6].append(linked_card)

                                        # Flip over new card on old tableau pile
                                        if len(tableau_piles[old_tableau]) > 0:
                                            tableau_piles[old_tableau][-1].position = CardPosition.FACE_UP
                                            draggable_cards.append(tableau_piles[old_tableau][-1])

                                        for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                            linked_card.rect.x = king_placeholder7_rect.x
                                            linked_card.rect.y = king_placeholder7_rect.y + 20 * (i + 1)

                                    card_being_dragged.rect.x = king_placeholder7_rect.x
                                    card_being_dragged.rect.y = king_placeholder7_rect.y

                                    currently_dragging_card = False
                                    card_being_dragged = None

                                else:
                                    # Couldn't find a match so reset the card(s) being dragged
                                    for i, linked_card in enumerate(
                                            card_being_dragged.linked_cards):
                                        linked_card.rect.x = original_dragging_x
                                        linked_card.rect.y = original_dragging_y + 20 * (
                                                i + 1)
                                    card_being_dragged.rect.x = original_dragging_x
                                    card_being_dragged.rect.y = original_dragging_y
                                    currently_dragging_card = False
                                    card_being_dragged = None


                            else:
                                # Couldn't find a match so reset the card(s) being dragged
                                for i, linked_card in enumerate(
                                        card_being_dragged.linked_cards):
                                    linked_card.rect.x = original_dragging_x
                                    linked_card.rect.y = original_dragging_y + 20 * (
                                                i + 1)
                                card_being_dragged.rect.x = original_dragging_x
                                card_being_dragged.rect.y = original_dragging_y
                                currently_dragging_card = False
                                card_being_dragged = None

                        else:

                            # Couldn't find a match so reset the card(s) being dragged
                            for i, linked_card in enumerate(card_being_dragged.linked_cards):
                                linked_card.rect.x = original_dragging_x
                                linked_card.rect.y = original_dragging_y + 20 * (i + 1)
                            card_being_dragged.rect.x = original_dragging_x
                            card_being_dragged.rect.y = original_dragging_y
                            currently_dragging_card = False
                            card_being_dragged = None

    if pygame.mouse.get_pressed()[0]:
        for card in draggable_cards:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if card.rect.collidepoint(mouse_x, mouse_y) and not currently_dragging_card:
                original_dragging_x = card.rect.x
                original_dragging_y = card.rect.y
                for i, linked_card in enumerate(card.linked_cards):
                    linked_card.rect.centerx = mouse_x
                    linked_card.rect.centery = mouse_y + 20 * (i + 1)
                card.rect.centerx = mouse_x
                card.rect.centery = mouse_y
                currently_dragging_card = True
                card_being_dragged = card

            if currently_dragging_card and card == card_being_dragged:
                for i, linked_card in enumerate(card.linked_cards):
                    linked_card.rect.centerx = mouse_x
                    linked_card.rect.centery = mouse_y + 20 * (i + 1)
                card.rect.centerx = mouse_x
                card.rect.centery = mouse_y

    # Drawing stuff
    display_surface.fill(DARK_GREEN)
    for tableau in tableau_piles:
        for card in tableau:
            if card.position == CardPosition.FACE_DOWN:
                card_back.rect.x = card.rect.x
                card_back.rect.y = card.rect.y
                display_surface.blit(card_back.surface, card_back.rect)
            elif card.position == CardPosition.FACE_UP:
                display_surface.blit(card.surface, card.rect)
    # Get empty tableaus
    empty_tableaus_nums = [i for i, _ in enumerate(tableau_piles) if not tableau_piles[i]]
    # Draw king placeholders
    for empty_tableau_num in empty_tableaus_nums:
        if empty_tableau_num == 0:
            king_placeholder1_rect = pygame.draw.rect(display_surface, WHITE, (king_placeholder_locations[0][0], king_placeholder_locations[0][1], 100, 150), 2)
        elif empty_tableau_num == 1:
            king_placeholder2_rect = pygame.draw.rect(display_surface, WHITE,(king_placeholder_locations[1][0], king_placeholder_locations[1][1], 100, 150), 2)
        elif empty_tableau_num == 2:
            king_placeholder3_rect = pygame.draw.rect(display_surface, WHITE,(king_placeholder_locations[2][0], king_placeholder_locations[2][1], 100, 150), 2)
        elif empty_tableau_num == 3:
            king_placeholder4_rect = pygame.draw.rect(display_surface, WHITE,(king_placeholder_locations[3][0], king_placeholder_locations[3][1], 100, 150), 2)
        elif empty_tableau_num == 4:
            king_placeholder5_rect = pygame.draw.rect(display_surface, WHITE,(king_placeholder_locations[4][0], king_placeholder_locations[4][1], 100, 150), 2)
        elif empty_tableau_num == 5:
            king_placeholder6_rect = pygame.draw.rect(display_surface, WHITE,(king_placeholder_locations[5][0], king_placeholder_locations[5][1], 100, 150), 2)
        elif empty_tableau_num == 6:
            king_placeholder7_rect = pygame.draw.rect(display_surface, WHITE,(king_placeholder_locations[6][0], king_placeholder_locations[6][1], 100, 150), 2)

    if len(stock_pile) == 0:
        reset_stock_pile_circle = pygame.draw.circle(display_surface, WHITE, (75, 100), 50, 2)
    else:
        card_back.rect.x = 25
        card_back.rect.y = 25
        display_surface.blit(card_back.surface, card_back.rect)
    for discard_pile_card in discard_pile[-3:]:
        display_surface.blit(discard_pile_card.surface, discard_pile_card.rect)
    foundation_pile1_rect = pygame.draw.rect(display_surface, WHITE, (350, 25, 100, 150), 2)
    foundation_pile2_rect = pygame.draw.rect(display_surface, WHITE, (475, 25, 100, 150), 2)
    foundation_pile3_rect = pygame.draw.rect(display_surface, WHITE, (600, 25, 100, 150), 2)
    foundation_pile4_rect = pygame.draw.rect(display_surface, WHITE, (725, 25, 100, 150), 2)
    for foundation_pile in foundation_piles:
        for foundation_card in foundation_pile:
            display_surface.blit(foundation_card.surface, foundation_card.rect)
    if currently_dragging_card:
        display_surface.blit(card_being_dragged.surface, card_being_dragged.rect)
        if card_being_dragged.linked_cards:
            for linked_card in card_being_dragged.linked_cards:
                display_surface.blit(linked_card.surface, linked_card.rect)

    # Win condition
    if foundation_piles[0] and foundation_piles[1] and foundation_piles[2] and foundation_piles[3]:
       if foundation_piles[0][-1].rank == 13 and foundation_piles[1][-1].rank == 13 and foundation_piles[2][-1].rank == 13 and foundation_piles[3][-1].rank == 13:
            draggable_cards = []
            font = pygame.font.SysFont('Arial', 42)
            winner_text = font.render("YOU WIN!", True, WHITE, DARK_GREEN)
            winner_text_rect = winner_text.get_rect()
            winner_text_rect.centerx = WINDOW_WIDTH//2
            winner_text_rect.centery = WINDOW_HEIGHT//2
            display_surface.blit(winner_text, winner_text_rect)

    pygame.display.update()

pygame.quit()