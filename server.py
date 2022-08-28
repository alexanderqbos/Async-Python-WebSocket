#!/usr/bin/python3

import asyncio

KEY_SIZE = 8
MAX_MSG_SIZE = 160
BUF_SIZE = 1024

ERROR_RESPONSE = b'NO\n'
GET_CMD = "GET"
NUM_CONNECTIONS = 8
OK_RESPONSE = b'OK\n'
PUT_CMD = "PUT"

messages = {}

#
# PURPOSE:
# Given a string, extracts the key and message from it
#
# PARAMETERS:
# 's' is the string that will be used for the key and message extraction
#
# RETURN/SIDE EFFECTS:
# Returns (key, message, flag), where flag is True if the extraction
# succeeded, False otherwise
#
# NOTES:
# To succeed, the string must be of format "KEYMSG" where KEY is of length KEY_SIZE
#
def get_key(s):
    if len(s) < KEY_SIZE:
        return ("", "", False)
    else:
        return (s[:KEY_SIZE], s[KEY_SIZE:], True)

#
# PURPOSE:
# Given a string, extracts the key and message, and stores the message in messages[key]
#
# PARAMETERS:
# 's' is the string that will be used for the key and message extraction
#
# RETURN/SIDE EFFECTS:
# Returns OK_RESPONSE on success, ERROR_RESPONSE otherwise
#
# NOTES:
# To succeed, the string must be of format "KEYMSG" where KEY is of length KEY_SIZE
# and MSG does not exceed MAX_MSG_SIZE
#
def process_put(s):
    (key, msg, ok) = get_key(s)
    if (not ok) or (len(msg) > MAX_MSG_SIZE):
        return ERROR_RESPONSE

    # print("Saving", msg, "with key", key)
    messages[key] = msg

    return OK_RESPONSE

#
# PURPOSE:
# Given a string, extracts the key and message from it, and returns message[key]
#
# PARAMETERS:
# 's' is the string that will be used for the key and message extraction
#
# RETURN/SIDE EFFECTS:
# Returns the message if the extraction succeeded, and b'' otherwise
#
# NOTES:
# To succeed, the string must be of format "KEY" where KEY is of length KEY_SIZE
#
def process_get(s):
    (key, msg, ok) = get_key(s)
    if not ok or len(msg) != 0 or not key in messages:
        return b'\n'

    #print("Found", messages[key], "with key", key)
    return ('NO' + messages[key] + '\n').encode('utf-8')

#
# PURPOSE:
# Given a string, parses the string and implements the contained PUT or GET command
#
# PARAMETERS:
# 's' is the string that will be used for parsing
#
# RETURN/SIDE EFFECTS:
# Returns the result of the command if the extraction succeeded, ERROR_RESPONSE otherwise
#
# NOTES:
# The string is assumed to be of format "CMDKEYMSG" where CMD is either PUT_CMD or GET_CMD,
# KEY is of length KEY_SIZE, and MSG varies depending on the command. See process_put(s)
# and process_get(s) for details regarding what the commands do and their return values
#
def process_line(s):
    if s.startswith(PUT_CMD):
        return process_put(s[(len(PUT_CMD)):])
    elif s.startswith(GET_CMD):
        return process_get(s[(len(GET_CMD)):])
    else:
        return ERROR_RESPONSE

#
# PURPOSE:
# function called by a new connection that uses asyncio reader writer
#
# PARAMETERS:
# reader - The message sent from the connection is processed by an instance of reader
# writer - How asyncio sends a message to a client
#
# RETURN/SIDE EFFECTS:
# No return statement as it will handle error messaging on it's own with responses to clients
#
# NOTES:
# Is called as part of the start_server function.
#
async def ClientMessageBuffer(reader, writer):
    async with asyncio.Lock():
        data = await reader.readline()
        message = data.decode('utf-8')
        message = message.strip()
        # print(message[-8:])
        reply = process_line(message)
        # print(reply)
        writer.write(reply)
        writer.close()
        # print(messages)
        await writer.wait_closed()

#
# PURPOSE:
# Main function initializing the server and serving until the application exits
#
# NOTES:
# Calls the start_server fucntion that points to the ClientMessageBuffer the connected
# users are sent to for processing. Now using ipv6 localhost identifier.
#
async def main():
    server = await asyncio.start_server(ClientMessageBuffer, '::1', 12345)
    await server.serve_forever()

asyncio.run(main())