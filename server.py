import socket
import threading
import json
import time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 1373  # Port to listen on (non-privileged ports are > 1023)

# we have a dictionary which contains clients subscribing for each topic:
t_clients = {}
# keeps the numbers of times each client has been pinged:
clients = {}


def handler(conn, addr):
    print('Connected by', addr)
    while True:
        try:
            msg = conn.recv(1024)
            if not msg:
                continue
            # now we convert data recieved into a python dictionary:
            msg = msg.decode("utf-8")
            msg = json.loads(msg)
            # run server
            run_server(msg, conn)
        except:
            delete_client(conn)
            print('Disconnected by', addr)
            break


def run_server(msg, conn):
    if msg["command"] == "publish":
        # publish
        publish(msg["topic"], msg["massage"], conn)
    if msg["command"] == "subscribe":
        # subscribe
        subscribe(msg["topics"], conn)
    if msg["command"] == "ping":
        # do pong
        ping_msg = {"command": "pong"}
        ping_msg_j = json.dumps(ping_msg)
        conn.send(bytes(ping_msg_j, encoding="utf-8"))
    if msg["command"] == "pong":
        clients[conn] = 0


def delete_client(c):
    # first delete it from every topic it used to subscribe:
    for t in t_clients:
        if c in t_clients[t]:
            t_clients[t].remove(c)
    clients.pop(c)
    c.close()


def publish(topic, msg, conn):
    # send ack:
    ack_msg = {"command": "PubAck"}
    ack_msg_j = json.dumps(ack_msg)
    conn.send(bytes(ack_msg_j, encoding="utf-8"))
    # publish to users:
    pub_msg = {"command": "Message", "topic": topic, "message": msg}
    pub_msg_j = json.dumps(pub_msg)
    for c in t_clients[topic]:
        try:
            c.send(bytes(pub_msg_j, encoding="utf-8"))
        except:
            delete_client(c)


def subscribe(topics, conn):
    for t in topics:
        if t in t_clients:
            if conn not in t_clients[t]:
                t_clients[t].append(conn)
        else:
            t_clients[t] = [conn]
    print(t_clients)
    # send ack:
    ack_msg = {"command": "SubAck", "topics": topics}
    ack_msg_j = json.dumps(ack_msg)
    conn.send(bytes(ack_msg_j, encoding="utf-8"))


def check_ping():
    for c in clients:
        if clients[c] == 3:
            delete_client(c)
        else:
            clients[c] = clients[c] + 1
            ping_msg = {"command": "ping"}
            ping_msg_j = json.dumps(ping_msg)
            conn.send(bytes(ping_msg_j, encoding="utf-8"))
    print(clients)
    print('pinging!')
    time.sleep(10)
    check_ping()


# we don't use with cause server doesnt close any connections.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
threading.Thread(target=check_ping).start()
while True:
    conn, addr = s.accept()
    clients[conn] = 0
    threading.Thread(target=handler, args=(conn, addr)).start()
