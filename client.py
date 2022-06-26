import socket
import sys
import json

HOST = sys.argv[1]
PORT = sys.argv[2]


def start_client():
    global cmd
    cmd = sys.argv[3]
    inputs = []
    if cmd == 'publish' or cmd == 'subscribe' or cmd == 'ping':
        inputs = sys.argv[4:]
    else:
        print("Please enter valid command!")
        exit(-1)
    # check the command:
    if cmd == "publish":
        topic = inputs[0]
        message = inputs[1]
        msg_to_send = {"command": cmd, "topic": topic, "massage": message}
        j_msg_to_send = json.dumps(msg_to_send)
        conn.send(bytes(j_msg_to_send, encoding="utf-8"))
    elif cmd == "subscribe":
        msg_to_send = {"command": cmd, "topics": inputs}
        j_msg_to_send = json.dumps(msg_to_send)
        conn.send(bytes(j_msg_to_send, encoding="utf-8"))
    elif cmd == "ping":
        msg_to_send = {"command": "ping"}
        j_msg_to_send = json.dumps(msg_to_send)
        conn.send(bytes(j_msg_to_send, encoding="utf-8"))
    try:
        run_client()
    except socket.error:
        print("Socket Error!")


# client starts listening for commands:
def run_client():
    #conn.settimeout(10.0)
    while True:
        msg = conn.recv(1024)
        if not msg:
            continue
        msg = msg.decode("utf-8")
        # to convert json data to dictionary:
        msg = json.loads(msg)
        if msg['command'] == 'Message':
            print(msg['topic'] + " -> " + msg['message'])
        elif msg['command'] == 'SubAck':
            success_topics = msg['topics']
            print("Subscribing on " + ' '.join(str(t) for t in msg['topics']))
        elif msg['command'] == 'PubAck':
            print("Published Successfully!")
        elif msg['command'] == 'ping':
            msg_to_send = {"command": "pong"}
            j_msg_to_send = json.dumps(msg_to_send)
            conn.send(bytes(j_msg_to_send, encoding="utf-8"))
        elif msg['command'] == 'pong':
            print("Ping Ponged Successfully!")
        else:
            print("No valid msg!")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, int(PORT)))
conn = s
start_client()