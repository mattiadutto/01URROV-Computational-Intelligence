from re import I
import numpy as np
from collections import defaultdict

from constants import NUMBER_OF_CARD
from client import colorToValue, valueToColor
from clientFunctions import completeHand

MAX_DEPTH = 4
# NOTE: myCardValues is form of 4 values, so before calling MCTS is need to expand to an array of 4 from 2. When I call MCTS I have to add to the names my name
# todo: check value in playerNames
class MonteCarloTreeSearchNode():
    def __init__(self, state, player, numPlayer, playerNames, table, discardPile, depth, parent=None, parent_action=None):
        """ 
        State = userTables point of view up to a 4*5*4 matrix + myCardValues -> 5 x 5 x 4, numPlayer it indicate where the current player is playing.
        myCardValues = myCardValues, state[numPlayer]
        Player = index of player that is virtually playing
        """
        self.state = state
        #self.myCardValues = myCardValues # my State
        self.numPlayer = numPlayer
        self.playerNames = playerNames
        self.depth = depth + 1
        self.table = table
        self.discardPile = discardPile

        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict()
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        self.player = player
        return
 
    def untried_actions(self):
        self._untried_actions = self.get_legal_actions(self.state)
        return self._untried_actions
  
    def findBestResult(self):
        array = np.array(list(self._results.items()))
        max = np.argmax(array[:, 1] )
        return array[max][0], array[max][1] # it return action, result
  
    def expand(self):
        action = self._untried_actions.pop()
        state, table, discarded = self.move(self.state, action, self.player)
        

        depth = self.depth
        if self.player + 1 > self.numPlayer:
            depth += 1

        player = (self.player + 1) % self.numPlayer
        
        child_node = MonteCarloTreeSearchNode(state, player, self.numPlayer, self.playerNames, table, discarded, depth, parent=self, parent_action=action)
       
        self.children.append(child_node)
        return child_node 
 
    def is_terminal_node(self):
        return self.is_game_over(self.state)

    def rollout(self):
        current_rollout_state = self.state.copy()
        player = self.player
        while not self.is_game_over(current_rollout_state):    
            possible_moves = self.get_legal_actions(current_rollout_state)
            if possible_moves:
                action = self.rollout_policy(possible_moves)
                _, table, _ = self.move(current_rollout_state, action, player)

            else: 
                break
            player = (self.player + 1) % self.numPlayer
        return self.game_result(table), action
 
    def backpropagate(self, result, action):
        self._number_of_visits += 1.
        self._results[action] = result
        if self.parent:
            self.parent.backpropagate(result, action)
  
    def is_fully_expanded(self):
        return len(self._untried_actions) == 0
  
    def best_child(self):
        iMax = -1
        vMax = -1
        for i, c in enumerate(self.children):
            _, r = c.findBestResult()
            if r > vMax:
                vMax, iMax = r, i
        return self.children[iMax]
 
    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]

    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node() and current_node.depth < MAX_DEPTH:
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node
  
    def best_action(self):
        simulation_no = 5

        for _ in range(simulation_no):            
            v = self._tree_policy()
            reward, action = v.rollout()
            v.backpropagate(reward, action)
        
        return self.best_child()

    def get_legal_actions(self): 
        moves = list()
        
        # If a card is already present I can discard it. I can only produce one fire per color. 
        for i in range(NUMBER_OF_CARD):
            if self.state[self.numPlayer][i][0] > -1 and self.state[self.numPlayer][i][1] > -1 and self.state[self.numPlayer][i][0] <= self.table[self.state[self.numPlayer][i][1]]:
                moves.append(f"discard {i}")
        # Play suggestion
        for i in range(NUMBER_OF_CARD):
            for j in range(NUMBER_OF_CARD):
                # table with 2 rows we have on the first cell the value and in the second the color
                # With the change that table is only one row we have:
                if sum(self.table) == 0 and self.state[self.numPlayer][i][0] == 1:
                    moves.append(f"play {i}")
                elif self.state[self.numPlayer][i][1] != -1 and ((self.state[self.numPlayer][i][0] == 1 and self.table[self.state[self.numPlayer][i][1]] == 0) or \
                (self.state[self.numPlayer][i][0] == (self.table[self.state[self.numPlayer][i][1]] + 1) and self.table[self.state[self.numPlayer][i][j]] <= 4)): 
                    moves.append(f"play {i}")

        # Hint suggestion
        # Value part
        suggestPlayer = None
        suggestValue = None
        
        for i in range(self.numPlayer):
            if i != self.numPlayer: # I exclude the case where the selected player is mySelf
                for v in range(NUMBER_OF_CARD):
                    for ci in range(NUMBER_OF_CARD):
                        card = self.state[i][ci]
                        if card[2] == v and card[2] > self.table[card[3]] and card[0] != 1:
                            suggestPlayer = i
                            suggestValue = v
                        if suggestPlayer is not None:
                            break
                    if suggestPlayer is not None:
                            break
                if suggestPlayer is not None:
                            break

        suggestValues = []
        for i in range(5):
            if self.state[suggestPlayer][i][2] == suggestValue:
                suggestValues.append(i)
        
        # Color part
        valuePerColor = np.zeros(self.numPlayer * NUMBER_OF_CARD) # NUMBER_OF_CARD in this case is NUMBER_OF_COLORS
        valuePerColor = np.reshape(valuePerColor, (self.numPlayer, NUMBER_OF_CARD))
        for pi in range(self.numPlayer - 1): # for each player
            for ci in range(NUMBER_OF_CARD): # for each card
                # we count the # of card of that colour.
                if self.state[pi][ci][1] != 1: # if the card color is already hinted we don't add to the sum.
                    valuePerColor[pi][self.state[pi][ci][3]] += 1
        hintPlayers, hintColorValues = np.where(valuePerColor == np.max(valuePerColor)) 
        hintPlayer, hintColor = hintPlayers[0], hintColorValues[0] # I have to take only the first case
        moves.append(f"hint color {self.playerNames[hintPlayer]} {valueToColor(hintColor)} {0}") 
        moves.append(f"hint value {self.playerNames[suggestPlayer]} {suggestValue} {suggestValues}")
        
        # Discard part, bad discard.
        if len(moves) == 0:
            cardsValue = self.state[self.numPlayer][:][0]
            min = None
            minI = None
            for i in range(NUMBER_OF_CARD):
                if cardsValue[i] < min and cardsValue[i] != 0:
                    min = cardsValue[i]
                    minI = i
            if minI is not None:
                moves.append(f"discard {minI}")
        return moves

    def move(self, action):
        userCardValues = self.state.copy() # In this case myCardValues = userCardValues[self.numPlayer]
        table = self.table.copy()
        discardPile = self.discardPile.copy()

        ply, plyInfo = action.split(" ", maxsplit=1)
        if ply == "discard":
            discardPile = np.append(discardPile, userCardValues[self.numPlayer][plyInfo][2:])
            userCardValues[self.numPlayer][plyInfo] = [-1, -1, -1, -1]
            userCardValues[self.numPlayer] = completeHand(userCardValues, userCardValues[self.numPlayer], discardPile, table)
        if ply == "hint":
            h_type, h_player, h_value, h_pos = plyInfo.split(" ", maxsplit = 3)
            posPlayer = self.playerNames.index(h_player)
            for i in h_pos:
                if h_type == "value":
                    userCardValues[posPlayer][i][0] = 1
                else:
                    userCardValues[posPlayer][i][1] = 1
        if ply == "play":
            table[userCardValues[self.numPlayer][plyInfo][3]] += 1 # I play the card 
            userCardValues[self.numPlayer][plyInfo] = [-1, -1, -1, -1] # I remove from the possible card
            userCardValues[self.numPlayer] = completeHand(userCardValues, userCardValues[self.numPlayer], discardPile, table) # I generate a new card
        return userCardValues, table, discardPile

    def is_game_over(self):
        if self.depth == MAX_DEPTH:
            return True
        return False

    def game_result(self, table):
        return sum(table)

#main of connect 4
random.seed(time.ctime())
player = random.randint(0, 1)
if player == 0:
    player = -1
print(f"Starting player is: {player}")
board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype = np.byte)
root = MonteCarloTreeSearchNode(board, player)
move_number = 0
while not root.is_game_over(root.state):
    selected_node = root.best_action()
    print_board(selected_node.state)
    root = selected_node
    move_number += 1
    print(f"{move_number} -> {root.player}")
    root.player = -root.player
print(f"Final state: \n Winning player: {_eval_board(root.state)} \n {np.flip(root.state.T, axis=0)}")