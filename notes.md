# Client
For start the connection: python3 client.py 127.0.0.1 1024 user
Hint commands:
- hint value player 1...5 positions
- hint color player color positions

Positions are from 0 to 4
We might add a hint color player color - # for no card of that color

To check:
- Invio on player
- Player that start the game

Add the check on hint values

Original client -> copy from the vanilla client.

> PROBLEM: for see the hint I have to send a show command
>          investigare su cio che arriva quando mando un hint


COME VIENE FATTO IL CAMBIO TRA UN GIOCATORE E L'ALTRO SI INVIANO DEI DATI o NO?


TODO:
- Capire dove vienee caricato il table
- Caricare table anche quando faccio play
- Reordering table quando faccio play



DONE: 
- Funzione che calcola i punti
- Togliere dalle hint I valori già hintati
- Da settare free [0,0,-1,-1] quando una carta viene giocata.


# 18 / 01 / 2022
TODO: Compute discarded cards
~~TODO: Rename discardedCards -> discardPile~~

Implement this in MCTS
For the discard check that I have at least 1 used token. Add this in the MCTSN, already fix into suggestedMove(s) in @client.py, for MCTS I have to add that param. 

With a play no new note tokens.
Add the check that I have at least a token for do the hint. 
With a discard I receive back a token.

TO CHECK: What is happening when I try to hint myself.

# 01 / 02 / 2022
Fix if I'm the first player
Fix hint case that with good hint we have the print
After a show: AttributeError: 'ServerHintData' object has no attribute 'usedNoteTokens', line 278, line 469
Play is working at first time
Fix hint places.

# 02 / 02 / 2022
Add: discard when I have 2 equal cards
Fix: usedTokenNotes (it was not declare as global)
Fix: discard part: how to select the values
~~To fix: remove all "suggested move"~~
Fix: if in hint value part, add not none checks.
Fix: on suggest part when the player is starting as first
~~To fix: remove already hinted suggestions~~
Fix: compute score
Fix: update userTable after a change on the other player
~~To test: update of the hint table (again)~~

# 03 / 02 / 2022
To test: way that if all previous card of a card are already played: discard that card!
~~To test: multiple player~~
~~To fix: hint color vs hint value~~
To add: the fact that if one card is already present in the table to hint asap
To add: manage when we have less then 5 cards.
To add: discard a card for which we know the minimum thing (-1, -1), (-1, X), (X, -1)
~~To add: print of the player before the move~~
To remove: comments, unused file...
Fix: player names, with multiple players

Finished match
- 13 (two players)
- 0 (two players)
-  