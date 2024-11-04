""" Solitaire """

import arcade
import random



# Constants for sizing
CARD_SCALE = 0.6

# How big are the cards?
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# How big is the mat we'll place the card on?
MAT_PERCENT_OVERSIZE = 1.25
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

# How much space do we leave as a gap between the mats?
# Done as a percent of the mat size.
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# The Y of the bottom row (2 piles)
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The X of where to start putting things on the left side
START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# Card constants
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Drag and Drop Cards"

TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The Y of the middle row (7 piles)
MIDDLE_Y = TOP_Y - MAT_HEIGHT - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# How far apart each pile goes
X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT


# If we fan out cards stacked on each other, how far apart to fan them?
CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3

# Constants that represent "what pile is what" for the game
PILE_COUNT = 13
BOTTOM_FACE_DOWN_PILE = 0
BOTTOM_FACE_UP_PILE = 1
PLAY_PILE_1 = 2
PLAY_PILE_2 = 3
PLAY_PILE_3 = 4
PLAY_PILE_4 = 5
PLAY_PILE_5 = 6
PLAY_PILE_6 = 7
PLAY_PILE_7 = 8
TOP_PILE_1 = 9
TOP_PILE_2 = 10
TOP_PILE_3 = 11
TOP_PILE_4 = 12

FACE_DOWN_IMAGE = ":resources:images/cards/cardBack_red2.png"

class Card(arcade.Sprite):
    """ Card sprite """

    def __init__(self, suit, value, scale=1):
        """ Card constructor """

        # Attributes for suit and value
        self.suit = suit
        self.value = value

        # Image to use for the sprite when face up
        self.image_file_name = f":resources:images/cards/card{self.suit}{self.value}.png"

        self.is_face_up = False
        super().__init__(FACE_DOWN_IMAGE, scale, hit_box_algorithm="None")

    def face_down(self):
        """ Turn card face-down """
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)
        self.is_face_up = False

    def face_up(self):
        """ Turn card face-up """
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True

    @property
    def is_face_down(self):
        """ Is this card face down? """
        return not self.is_face_up
    

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = None

        arcade.set_background_color(arcade.color.AMAZON)

          # List of cards we are dragging with the mouse
        self.held_cards = None
        self.move_counter = 0

        self.waiting_for_click = False

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = None

     # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list = None

        self.piles = None



    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

      # List of cards we are dragging with the mouse
        self.held_cards = []

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = []

        
        # Sprite list with all the cards, no matter what pile they are in.

           # ---  Create the mats the cards go on.

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the mats for the bottom face down and face up piles
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X, BOTTOM_Y
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X + X_SPACING, BOTTOM_Y
        self.pile_mat_list.append(pile)

        # Create the seven middle piles
        for i in range(7):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, MIDDLE_Y
            self.pile_mat_list.append(pile)

        # Create the top "play" piles
        for i in range(4):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, TOP_Y
            self.pile_mat_list.append(pile)

        self.card_list = arcade.SpriteList()

        # Create every card
        for card_suit in CARD_SUITS:
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                card.position = START_X, BOTTOM_Y
                self.card_list.append(card)
                
                # Shuffle the cards

        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

        self.piles = [[] for _ in range(PILE_COUNT)]

        # Put all the cards in the bottom face-down pile
        for card in self.card_list:
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)

         # - Pull from that pile into the middle piles, all face-down
        # Loop for each pile
        for pile_no in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            # Deal proper number of cards for that pile
            for j in range(pile_no - PLAY_PILE_1 + 1):
                # Pop the card off the deck we are dealing from
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                # Put in the proper pile
                self.piles[pile_no].append(card)
                # Move card to same position as pile we just put it in
                card.position = self.pile_mat_list[pile_no].position
                # Put on top in draw order
                self.pull_to_top(card)

                # Flip up the top cards
        for i in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            self.piles[i][-1].face_up()

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

            # Draw the mats the cards go on to
        self.pile_mat_list.draw()

        # Draw the cards
        self.card_list.draw()

    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top) """

        # Remove, and append to the end
        self.card_list.remove(card)
        self.card_list.append(card)

    def draw_three_cards(self):
        """ Draw three cards from the draw pile """
        # Draw up to three cards from the face-down pile
        for i in range(3):
            if len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                break
            # Get the top card
            card = self.piles[BOTTOM_FACE_DOWN_PILE][-1]
            # Flip face up
            card.face_up()
            # Move card position to bottom-right face-up pile
            card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position
            # Remove card from face-down pile
            self.piles[BOTTOM_FACE_DOWN_PILE].remove(card)
            # Move card to face-up list
            self.piles[BOTTOM_FACE_UP_PILE].append(card)
            # Put on top draw-order wise
            self.pull_to_top(card)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # Have we clicked on a card?
        if len(cards) > 0:

            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            assert isinstance(primary_card, Card)

            # Figure out what pile the card is in
            pile_index = self.get_pile_for_card(primary_card)

            # Are we clicking on the bottom deck, to flip three cards?
            if pile_index == BOTTOM_FACE_DOWN_PILE and len(self.piles[BOTTOM_FACE_UP_PILE]) == 0:
                # Flip three cards if the face-up pile is empty
                self.draw_three_cards()

            elif pile_index == BOTTOM_FACE_DOWN_PILE:
                # If we still have cards in the face-up pile, don't allow drawing more until they are used
                if len(self.piles[BOTTOM_FACE_UP_PILE]) > 0:
                    return
                # Otherwise, draw three more cards
                self.draw_three_cards()

            elif primary_card.is_face_down:
                # Is the card face down? In one of those middle 7 piles? Then flip up
                primary_card.face_up()
            else:
                # All other cases, grab the face-up card we are clicking on
                self.held_cards = [primary_card]
                # Save the position
                self.held_cards_original_position = [self.held_cards[0].position]
                # Put on top in drawing order
                self.pull_to_top(self.held_cards[0])

                # Is this a stack of cards? If so, grab the other cards too
                card_index = self.piles[pile_index].index(primary_card)
                for i in range(card_index + 1, len(self.piles[pile_index])):
                    card = self.piles[pile_index][i]
                    self.held_cards.append(card)
                    self.held_cards_original_position.append(card.position)
                    self.pull_to_top(card)
        else:
            # Click on a mat instead of a card?
            mats = arcade.get_sprites_at_point((x, y), self.pile_mat_list)

            if len(mats) > 0:
                mat = mats[0]
                mat_index = self.pile_mat_list.index(mat)

                # Is it our turned over flip mat? and no cards on it?
                if mat_index == BOTTOM_FACE_DOWN_PILE and len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                    # Flip the deck back over so we can restart
                    temp_list = self.piles[BOTTOM_FACE_UP_PILE].copy()
                    for card in reversed(temp_list):
                        card.face_down()
                        self.piles[BOTTOM_FACE_UP_PILE].remove(card)
                        self.piles[BOTTOM_FACE_DOWN_PILE].append(card)
                        card.position = self.pile_mat_list[BOTTOM_FACE_DOWN_PILE].position

    def remove_card_from_pile(self, card):
        """ Remove card from whatever pile it was in. """
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break
    
    def get_pile_for_card(self, card):
        """ What pile is this card in? """
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index
            
    def move_card_to_new_pile(self, card, pile_index):
        """ Move the card to a new pile """
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def on_mouse_release(self, x: float, y: float, button: int,
                        modifiers: int):
        if self.waiting_for_click:
            self.waiting_for_click = False
            self.message = ""
            self.setup()
            return
        """ Called when the user presses a mouse button. """
        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return

        # Find the closest pile, in case we are in contact with more than one
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True

        # See if we are in contact with the closest pile
        if arcade.check_for_collision(self.held_cards[0], pile):

            # What pile is it?
            pile_index = self.pile_mat_list.index(pile)

            #  Is it the same pile we came from?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # If so, who cares. We'll just reset our position.
                pass

            elif PLAY_PILE_1 <= pile_index <= PLAY_PILE_7:
                # Are there already cards there?
                if len(self.piles[pile_index]) > 0:
                    # Get the top card of the pile
                    top_card = self.piles[pile_index][-1]
                    
                    # Check if the card being moved is one rank lower and of alternating color
                    if self.can_stack_card(self.held_cards[0], top_card):
                        # Move cards to proper position
                        for i, dropped_card in enumerate(self.held_cards):
                            dropped_card.position = top_card.center_x, \
                                                    top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)
                        for card in self.held_cards:
                            # Cards are in the right position, but we need to move them to the right list
                            self.move_card_to_new_pile(card, pile_index)

                        # Success, don't reset position of cards
                        reset_position = False
                else:
                    # Are there no cards in the middle play pile?
                    # Only allow Kings to be placed in empty spots
                    if self.held_cards[0].value == "K":
                        for i, dropped_card in enumerate(self.held_cards):
                            # Move cards to proper position
                            dropped_card.position = pile.center_x, \
                                                    pile.center_y - CARD_VERTICAL_OFFSET * i
                        for card in self.held_cards:
                            # Cards are in the right position, but we need to move them to the right list
                            self.move_card_to_new_pile(card, pile_index)

                        # Success, don't reset position of cards
                        reset_position = False

            elif TOP_PILE_1 <= pile_index <= TOP_PILE_4 and len(self.held_cards) == 1:
                # Check if the foundation pile is empty and the card is an Ace
                if len(self.piles[pile_index]) == 0 and self.held_cards[0].value == "A":
                    # Move position of card to pile
                    self.held_cards[0].position = pile.position
                    # Move card to card list
                    for card in self.held_cards:
                        self.move_card_to_new_pile(card, pile_index)

                    reset_position = False
                # Check if the card can be added to the foundation pile (same suit and ascending order)
                elif len(self.piles[pile_index]) > 0:
                    top_card = self.piles[pile_index][-1]
                    if self.can_add_to_foundation(self.held_cards[0], top_card):
                        # Move position of card to pile
                        self.held_cards[0].position = pile.position
                        # Move card to card list
                        for card in self.held_cards:
                            self.move_card_to_new_pile(card, pile_index)

                        reset_position = False

        # If the move wasn't valid, reset the cards to their original position
        if reset_position:
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []

        self.move_counter +=1
        if self.check_for_win():
            print("Congratulations! You've won the game!")
            self.message = "Congratulations! You've won the game!"
            self.waiting_for_click = True

    # Check if no moves are left
        if self.check_no_moves_left():
            print("No more moves available. Game over!")
            self.message = "No more moves available. Game over!"
            self.waiting_for_click = True
            

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

        # Draw the mats the cards go on to
        self.pile_mat_list.draw()

        # Draw the cards
        self.card_list.draw()

        # Draw the message if there is one
        if hasattr(self, 'message') and self.message:
            arcade.draw_text(
                self.message,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.color.BLACK,
                font_size=20,
                anchor_x="center",
                anchor_y="center"
            )

    def can_stack_card(self, moving_card, target_card):
        """ Check if the moving card can be stacked on the target card """
        # Check if the cards are of alternating colors
        is_alternating_color = (moving_card.suit in ["Hearts", "Diamonds"] and target_card.suit in ["Clubs", "Spades"]) or \
                            (moving_card.suit in ["Clubs", "Spades"] and target_card.suit in ["Hearts", "Diamonds"])
        # Check if the moving card is one rank lower than the target card
        is_one_rank_lower = CARD_VALUES.index(moving_card.value) == CARD_VALUES.index(target_card.value) - 1

        return is_alternating_color and is_one_rank_lower

    def can_add_to_foundation(self, moving_card, target_card):
        """ Check if the moving card can be added to the foundation pile """
        # Check if the cards are of the same suit
        is_same_suit = moving_card.suit == target_card.suit
        # Check if the moving card is one rank higher than the target_card
        is_one_rank_higher = CARD_VALUES.index(moving_card.value) == CARD_VALUES.index(target_card.value) + 1

        return is_same_suit and is_one_rank_higher

    def check_for_win(self):
        """ Check if the player has won the game """
        # Check if all foundation piles have 13 cards (Ace to King)
        for pile_index in range(TOP_PILE_1, TOP_PILE_4 + 1):
            if len(self.piles[pile_index]) != 13:
                return False
        return True
    
    def check_no_moves_left(self):
        """ Check if there are no moves left in the game """
        # Check if there are any face-down cards in the play piles that can be flipped
        for pile_index in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            if len(self.piles[pile_index]) > 0:
                    # Ensure there are no face-up cards above the face-down card
                if self.piles[pile_index][-1].is_face_down:
                    print(f"Face-down card found in pile {pile_index - 1} with no face-up cards above, returning False.")
                    return False

        # Check if there are any cards left in the face-down pile to be dealt, only if there are no face-up cards
        if len(self.piles[BOTTOM_FACE_DOWN_PILE]) > 0 and len(self.piles[BOTTOM_FACE_UP_PILE]) == 0:
            print("Face-down pile is not empty and face-up pile is empty, returning False.")
            return False

        # Check if there are any valid moves left in the play piles
        for pile_index in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            if len(self.piles[pile_index]) > 0:
                top_card = self.piles[pile_index][-1]
                # Check if the card can be moved to another play pile or foundation pile
                for target_pile_index in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
                    if pile_index != target_pile_index and len(self.piles[target_pile_index]) > 0:
                        target_card = self.piles[target_pile_index][-1]
                        if self.can_stack_card(top_card, target_card):
                            # Prevent recognizing moves that simply reverse the last move
                            if self.held_cards_original_position and self.held_cards_original_position[0] == self.pile_mat_list[target_pile_index].position:
                                continue

                            print(f"Can stack {top_card} from pile {pile_index -1 } onto {target_card} in pile {target_pile_index -1}, returning False.")
                            return False
                for target_pile_index in range(TOP_PILE_1, TOP_PILE_4 + 1):
                    if len(self.piles[target_pile_index]) > 0:
                        target_card = self.piles[target_pile_index][-1]
                        if self.can_add_to_foundation(top_card, target_card):
                            print(f"Can add {top_card} from pile {pile_index -1} to foundation pile {target_pile_index -1}, returning False.")
                            return False
                    elif top_card.value == "A":
                        print(f"Top card {top_card} is an Ace and can be moved to an empty foundation pile, returning False.")
                        return False

        # Check if there are any valid moves left in the face-up pile
        if len(self.piles[BOTTOM_FACE_UP_PILE]) > 0:
            top_card = self.piles[BOTTOM_FACE_UP_PILE][-1]
            # Check if the top card from the draw pile can be moved to a play pile or foundation pile
            for target_pile_index in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
                if len(self.piles[target_pile_index]) > 0:
                    target_card = self.piles[target_pile_index][-1]
                    if self.can_stack_card(top_card, target_card):
                        print(f"Can stack {top_card} from face-up pile onto {target_card} in play pile {target_pile_index -1 }, returning False.")
                        return False
                elif top_card.value == "K":
                    print(f"Top card {top_card} is a King and can be moved to an empty play pile, returning False.")
                    return False
            for target_pile_index in range(TOP_PILE_1, TOP_PILE_4 + 1):
                if len(self.piles[target_pile_index]) > 0:
                    target_card = self.piles[target_pile_index][-1]
                    if self.can_add_to_foundation(top_card, target_card):
                        print(f"Can add {top_card} from face-up pile to foundation pile {target_pile_index -1}, returning False.")
                        return False
                elif top_card.value == "A":
                    print(f"Top card {top_card} is an Ace and can be moved to an empty foundation pile, returning False.")
                    return False

        # If no valid moves are found, return True indicating no moves are left
        print("No moves left, returning True.")
        return True
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """
        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def on_key_press(self, symbol: int, modifiers: int):
        """ User presses key """
        if symbol == arcade.key.R:
            # Restart
            self.setup()


def main():
    """ Main function """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()


        