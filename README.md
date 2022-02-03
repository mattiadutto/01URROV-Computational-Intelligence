# Computational Intelligence 2021-2022
Original README.md can be found [here](https://github.com/squillero/computational-intelligence/blob/master/project/hanabi/README.md) with some informations about how the system works. 
This agent was developed base on the following [repository](https://github.com/squillero/computational-intelligence/blob/master/project/hanabi) provided as a tamplate for 2021/2022 edition of ```01URROV - Computational Intelligence``` at [Politecnico di Torino](https://www.polito.it/). 

## Server
For launch the server the basic syntax is:
```bash 
python3 server.py
```

## Client
Is an hard coded implementation, with a focus on the discard move, the aim of the agent is to avoid wrong moves (for a wrong move is meant to use a red token). 

For launch the client the complete syntax is:
```bash
python3 client.py <SERVER_IP> <SERVER_PORT> <CLIENT_NAME>
```

If you launch ```python3 client.py```: the default values for the parameters are:
```SERVER_IP = 127.0.0.1, SERVER_PORT = 1024 and CLIENT_NAME = SuperPippo```

After the launch of the client, you have to put the following command: ```ready``` for start the communication with the server and to tell to the others players that the client is ready. If you want to close after ```ready``` command use the combination of ```CTRL+C``` because the input is not read anymore (in the template implamentation the input was managed asynchronous), before giving ```ready``` command also ```exit``` command is available for quit the client. 

For developing the hard coded version the only support used is a translated version of the rules, available [here](https://www.goblins.net/files/downloads/Hanabi.pdf), and [numpy](https://numpy.org) online communities. 
All the "intelligence" of the agent is inside the ```suggestMove()``` function, where after asking for the current state of the game to the server is computing which play is more suggested. 
The agent's hand is matrix based on the hints from others players or from moves done by the agent it self.

This works was developed by Mattia Dutto ([s287598@studenti.polito.it](mailto:s287598@studenti.polito.it))