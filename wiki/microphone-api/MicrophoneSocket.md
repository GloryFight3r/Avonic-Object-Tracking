This class is used to send and receive requests and responses to the microphone via raw UDP packets.

# Functions

## connect(address: tuple[str, int])
Sets the IP address of the microphone

## send(command: str, responses: int) -> list[str]
Sends a command and waits 0.1 seconds for a response \
Args: 
* command - command to send
* responses - number of responses we are awaiting

Return: \
A list of N=*responses* responses