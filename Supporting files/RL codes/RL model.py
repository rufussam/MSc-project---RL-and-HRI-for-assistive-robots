import gym
from gym import Env
from gym.spaces import Discrete, Box, Dict, Tuple, MultiBinary, MultiDiscrete
import numpy as np
import random
import os
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.vec_env import VecFrameStack
from stable_baselines3.common.evaluation import evaluate_policy
import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
# host='169.254.18.107'
host = '192.168.0.2'
# host = '127.0.0.1'
port = 9999

s.bind((host, port))
s.listen(3)
c_messg = ''

# Client for Naomarks
print("waiting to connect- 2 pending")
conn, addr = s.accept()
conn.send("C1 connected".encode())
print("Naomarks program connected")

# Client for tablet
print("waiting to connect- 1 pending")
conn1, addr1 = s.accept()
conn1.send("C2 connected".encode())
print("tablet program connected")

# Ask for which mode of interaction
print("Enter the mode of interaction")
recv_message = conn1.recv(1024)
if recv_message.decode() == "no":
    print("Participans says Tablet")
else:
    print("Participants says Naomarks")
if (recv_message.decode() == str('no')):
    m = 0
elif (recv_message.decode() == str('yes')):
    m = 1
else:
    m = 5
conn.send("activate_yesnoimg".encode())
if m == 1:
    conn.send("activate_naomarks".encode())
    print("activate_naomarks")
    recv_message = conn.recv(1024)
    print("Activate naomarks message received by C1 ")
else:
    conn.send("activate_tablet".encode())
    print("activate_tablet")
    recv_message = conn.recv(1024)
    print("Activate tablet message received by C1 ")

result = 0


class obj_guess_test(Env):
    def __init__(self):
        self.action_space = Discrete(5)  # 4 states->0-start state 1,2,3-Objects
        self.observation_space = Box(low=0, high=5,
                                     shape=(1,))  # (direction of robot towards the object) co-ordinates: game related
        # self.observation_space = Discrete(4)
        self.state = 0
        self.no_obj = 5
        # self.user_obj = random.randint(1,3)
        self.p_counter = 0
        self.n_counter = 0
        self.done_dup = False

    def step(self, action):
        global c_messg

        # code of naomarks
        if m == 1:
            while True:

                global result
                if self.no_obj == 5:
                    self.user_obj = random.randint(1, 5)
                    #self.user_obj = input("Enter the input")
                    #self.user_obj = 5
                self.state = action + 1
                print("target=" + str(self.user_obj))
                print("Robot guess=" + str(self.state))
                # result = self.state
                # print("result=" + str(result))
                '''
                if self.user_obj==self.state:
                   compare='yes'
                else:
                    compare='No'
                '''
                if self.no_obj != 1:
                    messg = "Is the object you guessed is " + str(self.state) + "?"
                    conn.send(messg.encode())
                    print("waiting for response")
                    c_messg = conn.recv(1024)
                    compare = c_messg.decode()
                    print("User response is", compare)
                    print("self.no_obj value is" + str(self.no_obj))
                else:
                    messg = "The object you guessed is " + str(
                        self.state) + "right?. I will remember it the next time. But, please confirm it once"
                    conn.send(messg.encode())
                    print("waiting for response")
                    c_messg = conn.recv(1024)
                    compare = c_messg.decode()
                    print("User response is", compare)
                    print("self.no_obj value is" + str(self.no_obj))

                if str(compare) == 'no' and self.no_obj == 1:
                    self.p_counter += 1
                    reward = self.p_counter * 5
                    self.done_dup = True
                    print("Found successfully")
                    messg = "terminate1"
                    conn.send(messg.encode())
                    c_messg = conn.recv(1024)
                    print("Pepper says:", c_messg.decode())
                    messg = self.state
                    conn.send(str(messg).encode())
                    conn.close()

                if str(compare) == 'yes' or self.no_obj == 1:
                    self.p_counter += 1
                    reward = self.p_counter * 5
                    self.done_dup = True
                    print("Found successfully")
                    messg = "terminate"
                    conn.send(messg.encode())
                    c_messg = conn.recv(1024)
                    print("Pepper says:", c_messg.decode())
                    messg = self.state
                    conn.send(str(messg).encode())
                    conn.close()
                else:
                    self.n_counter -= 1
                    reward = self.n_counter * 10
                self.no_obj -= 1  # no of chances is equal to no. of objects
                if self.no_obj == 0 or self.done_dup == True:
                    done = True
                else:
                    done = False
                info = {}

                return self.state, reward, done, info
        # code for tablet
        if m == 0:
            while True:

                global result
                if self.no_obj == 5:
                    self.user_obj = random.randint(1, 5)
                    #self.user_obj = input("Enter the input")
                self.state = action + 1
                print("target=" + str(self.user_obj))
                print("Robot guess=" + str(self.state))
                # result = self.state
                # print("result=" + str(result))
                '''
                if self.user_obj==self.state:
                   compare='yes'
                else:
                    compare='No'
                '''
                compare = ''
                if (self.no_obj != 1):
                    messg = "Is the object you guessed is " + str(self.state) + "?"
                    conn.send(messg.encode())
                    print("waiting for response")
                    c_messg = conn1.recv(1024)
                    # print(conn1.recv(1024))
                    compare = c_messg.decode()
                else:
                    messg = "The object you guessed is " + str(
                        self.state) + "? I will definitely remember it the next time. Confirm once please"
                    conn.send(messg.encode())
                    print("waiting for response")
                    c_messg = conn1.recv(1024)
                    compare = c_messg.decode()
                print("User response is", compare)
                if str(compare) == 'no' and self.no_obj == 1:
                    self.p_counter += 1
                    reward = self.p_counter * 5
                    self.done_dup = True
                    print("Found successfully")
                    messg = "terminate1"
                    conn.send(messg.encode())
                    msg = conn.recv(1024)
                    print(msg.decode())
                    # time.sleep(3)
                    messg = self.state
                    # time.sleep(3)
                    conn.send(str(messg).encode())
                    conn.close()
                if str(compare) == 'yes' or self.no_obj == 1:
                    # time.sleep(3)
                    # print("self.no_obj value is" + str(self.no_obj))
                    self.p_counter += 1
                    reward = self.p_counter * 5
                    self.done_dup = True
                    print("Found successfully")
                    messg = "terminate"
                    conn.send(messg.encode())
                    msg = conn.recv(1024)
                    print(msg.decode())
                    # time.sleep(3)
                    messg = self.state
                    # time.sleep(3)
                    conn.send(str(messg).encode())
                    conn.close()
                else:
                    self.n_counter -= 1
                    messg = "upd_conf"
                    conn.send(messg.encode())
                    msg = conn.recv(1024)
                    print(msg.decode())
                    reward = self.n_counter * 10
                self.no_obj -= 1  # no of chances is equal to no. of objects
                if self.no_obj == 0 or self.done_dup == True:
                    done = True
                else:
                    done = False
                info = {}

                return self.state, reward, done, info

    def render(self):
        # Implement viz
        pass

    def reset(self):
        self.state = 0
        self.no_obj = 5
        self.p_counter = 0
        self.n_counter = 0
        self.done_dup = False
        return self.state


env_test = obj_guess_test()

model = PPO.load(r'C:\Users\Rufus Sam A\Downloads\project gym\obj_pick_200000_5obj', env_test)

evaluate_policy(model, env_test, n_eval_episodes=1, render=False)
