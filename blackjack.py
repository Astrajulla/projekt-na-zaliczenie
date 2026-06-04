import random
import sys
from typing import List, Tuple
import pygame
from pygame.locals import *
import pygame_textinput
 

class Card(pygame.sprite.Sprite):
    """Reprezentacja karty"""
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['H', 'D', 'C', 'S']  # hearts, diamonds, clubs, spades
    SUIT_NAMES = {
        'H': 'kier',
        'D': 'karo',
        'C': 'trefl',
        'S': 'pik'
    }

    def __init__(self, rank: str, suit: str, x:int = 0, y:int = 0, alpha:float = 0.0):
        self.rank = rank
        self.suit = suit
        self.path = f"textures/karty/{suit}-{rank}.png"
        super().__init__() 
        self.image = pygame.image.load(self.path)
        self.image.set_alpha(int(alpha * 255))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def __str__(self):
        return f"{self.rank}{Card.SUIT_NAMES[self.suit]}"
    
    def get_value(self) -> int:
        """Zwraca wartość karty"""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

class Deck:
    """Talia kart"""
    def __init__(self):
        self.cards = []
        self.create_deck()
    
    def create_deck(self):
        """Tworzy nową talię kart"""
        self.cards = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.cards.append(Card(rank, suit))
        random.shuffle(self.cards)
    
    def deal_card(self) -> Card:
        """Wydaje kartę z talii"""
        if len(self.cards) < 10:
            self.create_deck()
        return self.cards.pop()

class Hand:
    """Ręka gracza/krupiera"""
    def __init__(self):
        self.cards: List[Card] = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def cards_str(self):
        return ", ".join(str(card) for card in self.cards)
    
    def get_value(self) -> int:
        """Zwraca wartość ręki (asy automatycznie dostosowywane)"""
        value = 0
        aces = 0
        
        for card in self.cards:
            value += card.get_value()
            if card.rank == 'A':
                aces += 1
        
        # Zmiana asów z 11 na 1, jeśli przekroczył 21
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value

    
    def can_split(self):
        """Czy można zrobić split"""
        if len(self.cards) != 2:
            return False

        return self.cards[0].rank == self.cards[1].rank
    
    def __str__(self):
        return ", ".join(str(card) for card in self.cards)
    
    def reset(self):
        """Resetuje rękę"""
        self.cards = []

class Player:
    """Gracz"""
    def __init__(self, name: str):
        self.name = name
        self.hands = [Hand()]   # lista rąk (na wypadek rozdzielenia)
        self.points = 0

    @property
    def hand(self):
        return self.hands[0]
    
    def reset_hand(self):
        """Resetuje rękę gracza do nowej rundy"""
        self.hand.reset()

    def split_hand(self):
        """Dzieli rękę na dwie"""
    
        original_hand = self.hands[0]

        card1 = original_hand.cards[0]
        card2 = original_hand.cards[1]

        hand1 = Hand()
        hand1.add_card(card1)

        hand2 = Hand()
        hand2.add_card(card2)

        self.hands = [hand1, hand2]
    def draw(self, displaysurf):
        for hand in self.hands:
            for card in hand.cards:
                i = hand.cards.index(card)
                card.image.set_alpha(255)
                card.rect.center = (200+i*200, 500)
                displaysurf.blit(card.image, card.rect)
        pygame.display.update()

class Dealer(Player):
    """Krupier"""
    def __init__(self):
        super().__init__("Krupier")

    def draw1(self, displaysurf):
        for hand in self.hands:
            for card in hand.cards:
                i = hand.cards.index(card)
                card.image.set_alpha(255)
                card.rect.center = (200+i*200, 200)
                if hand.cards.index(card) != 0:
                    card.image = pygame.image.load("textures/karty/rewers.png")
                displaysurf.blit(card.image, card.rect)
                
        pygame.display.update()

    def draw2(self, displaysurf):
        for hand in self.hands:
            for card in hand.cards:
                i = hand.cards.index(card)
                card.image.set_alpha(255)
                card.rect.center = (200+i*200, 200)
                if hand.cards.index(card) != 0:
                    card.image = pygame.image.load(f'textures/karty/{card.suit}-{card.rank}.png')
                displaysurf.blit(card.image, card.rect)
                
        pygame.display.update()


class BlackjackGame:
    """Główna gra w blackjacka"""
    
    def __init__(self, players: List[Player], displaysurf):
        self.players = players
        self.dealer = Dealer()
        self.deck = Deck()
        self.round_results = {}
        self.displaysurf = displaysurf
    
    def display_rules(self):
        """Wyświetla zasady gry"""
        print("\n" + "="*60)
        print("BLACKJACK - ZASADY GRY")
        print("="*60)
        print("""
1. CEL GRY:
   • Uzyskaj więcej punktów niż krupier bez przekroczenia 21
   • Gracz z największą liczbą wygranych rund zostaje zwycięzcą

2. WARTOŚCI KART:
   • Karty 2-10: nominalna wartość
   • Figury (J, Q, K): 10 punktów
   • As (A): 11 lub 1 punkt (automatycznie dostosowywany)

3. PRZEBIEG GRY:
   • Każdy gracz i krupier otrzymują 2 karty
   • Gracze na zmianę decydują: DOBIERZ (H) czy PASUJ (S)
   • Krupier dobiera do 16 punktów, pauzuje na 17+ punktów
   • Zwycięzca każdej rundy zdobywa 1 punkt

4. WYNIKI:
   • Zwycięstwo: Twoja suma wyższa od krupiera (bez przebicia 21 punktów)
   • Przebicie: Przekroczenie 21 punktów = przegrana
   • Przegrana: Suma niższa od krupiera

5. AKCJE GRACZA:
   • H - DOBIERZ: Weź dodatkową kartę
   • S - PASUJ: Zatrzymaj się na obecnej sumie
   • P - SPLIT: Podziel rękę na dwie (jeśli masz parę)
""")
        print("="*60 + "\n")
    
    def display_game_state(self, show_dealer_cards: bool = False):
        """Wyświetla stan gry"""
        print("\n" + "-"*60)
        
        # Wyświetl krupiera
        if show_dealer_cards:
            dealer_value = self.dealer.hand.get_value()
            print(f"{self.dealer.name}: {self.dealer.hand.cards_str()}")
            print(f"Suma: {dealer_value}")
        else:
            # Ukryj drugą kartę krupiera
            if len(self.dealer.hand.cards) > 0:
                print(f"{self.dealer.name}: {self.dealer.hand.cards[0]} + [ukryta karta]")
        
        print("-"*60)
        
        # Wyświetl graczy
        for i, player in enumerate(self.players, 1):
            value = player.hand.get_value()
            status = "AKTYWNY" if value <= 21 else "PRZEBICIE"
            print(f"{i}. {player.name}: {player.hand.cards_str()}")
            print(f"Suma: {value} | Punkty: {player.points} | {status}")
        
        print("-"*60 + "\n")
    
    def play_split_hand(self, player, hand):

        while True:
            value = hand.get_value()

            print(f"Karty: {hand.cards_str()} | Suma: {value}")

            if value >= 21:
                break

            action = input("(H - DOBIERZ / S - PASUJ): ").upper().strip()

            if action == 'H':
                card = self.deck.deal_card()
                hand.add_card(card)

                print(f"Dobrałeś: {card}")

            elif action == 'S':
                break

    def play_round(self):
        """Rozgrywa jedną rundę"""
        print("\n" + "="*60)
        print("NOWA RUNDA")
        print("="*60)
        
        # Resetuj ręce
        self.dealer.reset_hand()
        self.round_results = {}
        for player in self.players:
            player.reset_hand()
        
        # Wydaj po 2 karty
        for _ in range(2):
            for player in self.players:
                player.hand.add_card(self.deck.deal_card())
            self.dealer.hand.add_card(self.deck.deal_card())
        
        self.display_game_state()

        
        
        # Tury graczy
        for player in self.players:
            self.displaysurf.fill((0, 128, 0))  # Zielone tło
            self.dealer.draw1(displaysurf=self.displaysurf)
            self.player_turn(player)
            pygame.display.update()
        
        # Tura krupiera
        self.dealer_turn()
        self.dealer.draw2(displaysurf=self.displaysurf)
        # Ocena wyników
        self.evaluate_results()
    
    def player_turn(self, player: Player):
        """Obsługuje turę gracza z możliwością wyboru"""
        print(f"\nTura {player.name}:")
        
        while True:
            value = player.hand.get_value()
            player.draw(displaysurf=self.displaysurf)
            pygame.display.update()
            
            # Sprawdź czy gracz przebił
            if value > 21:
                print(f"{player.name} przebił 21! Przegrana!")
                break
            
            # Sprawdź czy gracz ma dokładnie 21
            if value == 21:
                print(f"{player.name} ma 21! Automatycznie PASUJE.")
                break
            
            self.display_game_state()
            
            print(f"{player.name} - Twoje karty: {player.hand.cards_str()} | Suma: {value}")

            options = "(H - DOBIERZ / S - PASUJ"

            if player.hand.can_split():
                options += " / P - SPLIT"

            options += ")"

            #action = input(f"{player.name}, wybierz akcję {options}: ").upper().strip()

            action = None
            while action is None:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_h:
                            action = 'H'
                        elif event.key == pygame.K_s:
                            action = 'S'
                        elif event.key == pygame.K_p:
                            action = 'P'
            
            if action == 'H':
                card = self.deck.deal_card()
                player.hand.add_card(card)
                print(f"Dobrałeś: {card}")
                print(f"Aktualne karty: {player.hand.cards_str()} | Suma: {player.hand.get_value()}")
                player.draw(displaysurf=self.displaysurf)
                pygame.display.update()
            elif action == 'S':
                print(f"{player.name} PAUZUJE na {value}")
                break
            elif action == 'P' and player.hand.can_split():
                player.split_hand()

                print(f"{player.name} wykonuje SPLIT!")

                # Dobierz po jednej karcie do obu rąk
                for hand in player.hands:
                    hand.add_card(self.deck.deal_card())

                # Rozegraj obie ręce osobno
                for i, hand in enumerate(player.hands, 1):
                    print(f"\nRĘKA {i}")

                    self.play_split_hand(player, hand)
                    player.draw(displaysurf=self.displaysurf)
                    pygame.display.update()
                
                break
            elif player.hand.can_split():
                print(f"Nieprawidłowa akcja! Wpisz H, S lub P.")
            else:
                print(f"Nieprawidłowa akcja! Wpisz H lub S.")
    
    def dealer_turn(self):
        """Obsługuje turę krupiera (automatycznie dobiera do 16, pauzuje na 17+)"""
        print(f"\n{self.dealer.name}:")
        
        while True:
            value = self.dealer.hand.get_value()
            
            if value > 21:
                print(f"{self.dealer.name} przebił 21!")
                break
            
            if value >= 17:
                print(f"{self.dealer.name} PASUJE na {value}")
                break
            
            card = self.deck.deal_card()
            self.dealer.hand.add_card(card)
            print(f"{self.dealer.name} dobiera kartę: {card}")
            self.dealer.draw2(displaysurf=self.displaysurf)
            pygame.display.update()
        
        self.display_game_state(show_dealer_cards=True)
    
    def evaluate_results(self):
        """Ocenia wyniki rundy"""

        dealer_value = self.dealer.hand.get_value()
        dealer_bust = dealer_value > 21

        self.round_results = {}

        for player in self.players:

            for i, hand in enumerate(player.hands, 1):

                player_value = hand.get_value()
                player_bust = player_value > 21

                if player_bust:
                    result = "PRZEGRANA"
                    reason = "PRZEBICIE"
                    won = False

                elif dealer_bust:
                    result = "WYGRANA"
                    reason = "KRUPIER PRZEBIŁ"
                    won = True

                elif player_value > dealer_value:
                    result = "WYGRANA"
                    reason = "WYŻSZA SUMA"
                    won = True

                elif player_value < dealer_value:
                    result = "PRZEGRANA"
                    reason = "NIŻSZA SUMA"
                    won = False

                else:
                    result = "REMIS"
                    reason = "RÓWNE SUMY"
                    won = False

                if won:
                    player.points += 1

                key = f"{player.name}_hand_{i}"

                self.round_results[key] = {
                    "value": player_value,
                    "result": result,
                    "reason": reason
                }

        self.display_round_results(dealer_value)
    
    def display_round_results(self, dealer_value: int):
        """Wyświetla wyniki rundy dla wszystkich graczy"""

        print("\n" + "="*60)
        print("WYNIKI RUNDY")
        print("="*60)

        print(f"\nKrupier: {self.dealer.hand.cards_str()}")
        print(f"Suma: {dealer_value}\n")

        print("-"*60)

        for player in self.players:

            for i, hand in enumerate(player.hands, 1):

                key = f"{player.name}_hand_{i}"

                result_data = self.round_results[key]

                print(f"\n{player.name} - ręka {i}:")
                print(f"   Karty: {hand.cards_str()}")
                print(f"   Suma: {result_data['value']}")
                print(f"   {result_data['result']} - {result_data['reason']}")
                print(f"   Liczba wygranych: {player.points}")

        print("\n" + "="*60)
    
    def display_final_scores(self):
        """Wyświetla ostateczny wynik"""
        print("\n" + "="*60)
        print("PODSUMOWANIE PUNKTÓW")
        print("="*60)
        
        sorted_players = sorted(self.players, key=lambda p: p.points, reverse=True)
        
        for i, player in enumerate(sorted_players, 1):
            print(f"{i} MIEJSCE. {player.name}: {player.points} punktów")
        
        print("="*60)
    
    def play_game(self):
        """Główna pętla gry"""
        self.display_rules()
        
        round_num = 1
        while True:

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            

            self.displaysurf.fill((0, 128, 0))  # Zielone tło
            self.play_round()
            
            # Pytaj czy grać dalej
            choice = None
            while choice is None:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_t:
                            choice = 'T'
                        elif event.key == pygame.K_n:
                            choice = 'N'
            if choice == 'N':
                break
            round_num += 1
        
        self.display_final_scores()
        print("\n KONIEC GRY \n")


def main():
    pygame.init()
    width, height = 1200, 800
    displaysurf = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Blackjack")
    displaysurf.fill((0, 128, 0))  # Zielone tło
    font = pygame.font.SysFont(None, 48)
    


    """Funkcja główna"""
    print("="*60)
    print("BLACKJACK - GRA DLA WIELU GRACZY")
    print("="*60)
    
   #karta = Card('A', 'S', x=120, y=600, alpha=1.0)
   #displaysurf.blit(karta.image, karta.rect)
#pygame.display.update()
        


    while True:
        try:
            num_players = int(input("\nIle graczy będzie grać? (1-4): "))
            if 1 <= num_players <= 4:
                break
            else:
                print("Podaj liczbę między 1 a 4")
        except ValueError:
            print("Podaj liczbę!")
    
    # Zbierz imiona graczy
    players = []
    for i in range(num_players):
        name = input(f"Imię gracza {i+1}: ").strip()
        if not name:
            name = f"Gracz {i+1}"
        players.append(Player(name))
    
   
   

    # Uruchom grę
    game = BlackjackGame(players, displaysurf)
    game.play_game()

if __name__ == "__main__":
    main()