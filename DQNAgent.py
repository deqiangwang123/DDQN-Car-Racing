from keras.layers import Dense, Activation
from keras.models import Sequential, load_model
from keras.optimizers import Adam
import numpy as np
import tensorflow as tf
from collections import deque
import random
from keras.models import load_model

REPLAY_MEMORY_SIZE = 10000
MIN_REPLAY_MEMORY_SIZE = 10000
MINIBATCH_SIZE = 512


# REPLAY_MEMORY_SIZE = 100
# MIN_REPLAY_MEMORY_SIZE = 100
# MINIBATCH_SIZE = 50

DISCOUNT = 0.99
PREDICTION_BATCH_SIZE = 1
TRAINING_BATCH_SIZE = MINIBATCH_SIZE

NUM_ACTION = 9
STATE_DIM = 19

EPSILON_INIT = 1
EPSILON_DECAY = 0.9995 ## 0.9975 99975
MIN_EPSILON = 0.05

UPDATE_TARGET_EVERY = 50

FILE_NAME = 'dqn_model.h5'

class DQNAgent:
    def __init__(self):
        self.model = self.create_model()
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

        # self.tensorboard = ModifiedTensorBoard(log_dir=f"logs/{MODEL_NAME}-{int(time.time())}")
        self.target_update_counter = 0
        # self.graph = tf.get_default_graph()

        self.terminate = False
        self.last_logged_episode = 0
        self.training_initialized = False

        self.epsilon = EPSILON_INIT
        self.model_file = FILE_NAME

    def create_model(self):
        model = tf.keras.Sequential()
        model.add(tf.keras.Input(shape=(STATE_DIM,)))
        model.add(tf.keras.layers.Dense(256, activation=tf.nn.relu)) #prev 256 
        model.add(tf.keras.layers.Dense(32, activation=tf.nn.relu)) #prev 256
        model.add(tf.keras.layers.Dense(NUM_ACTION, activation=tf.nn.softmax))
        model.compile(loss = "mse", optimizer="adam")
        return model

    def update_replay_memory(self, transition):
        # transition = (current_state, action, reward, new_state, done)
        self.replay_memory.append(transition)

    def choose_action(self, state):

        state = np.array(state)
        state = state[np.newaxis, :]

        rand = np.random.random()
        if rand < self.epsilon:
            action = np.random.choice([i for i in range(NUM_ACTION)])
        else:
            actions = self.model.predict(state)
            action = np.argmax(actions)

        return action

    def train(self):
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)

        current_states = np.array([transition[0] for transition in minibatch])
        # with self.graph.as_default():
        current_qs_list = self.model.predict(current_states, PREDICTION_BATCH_SIZE)

        new_current_states = np.array([transition[3] for transition in minibatch])
        # with self.graph.as_default():
        future_qs_list = self.target_model.predict(new_current_states, PREDICTION_BATCH_SIZE)

        X = []
        y = []

        for index, (current_state, action, reward, new_state, done) in enumerate(minibatch):
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            X.append(current_state)
            y.append(current_qs)

        log_this_step = False
        # if self.tensorboard.step > self.last_logged_episode:
        #     log_this_step = True
        #     self.last_log_episode = self.tensorboard.step

        # with self.graph.as_default():
        self.model.fit(np.array(X), np.array(y), batch_size=TRAINING_BATCH_SIZE, verbose=0, shuffle=False, callbacks=[self.tensorboard] if log_this_step else None)

        self.epsilon = self.epsilon* EPSILON_DECAY  if self.epsilon > MIN_EPSILON  else MIN_EPSILON 

        if log_this_step:
            self.target_update_counter += 1

        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

    def get_qs(self, state):
        return self.model.predict(np.array(state).reshape(-1, *state.shape)/255)[0]
    
    def update_network_parameters(self):
        self.brain_target.copy_weights(self.brain_eval)

    def save_model(self):
        self.model.save(self.model_file)
        
    def load_model(self):
        self.model = load_model(self.model_file)
        self.target_model = load_model(self.model_file)
       
        if self.epsilon == 0.0:
            self.update_network_parameters()
    # def train_in_loop(self):
    #     X = np.random.uniform(size=(1, IM_HEIGHT, IM_WIDTH, 3)).astype(np.float32)
    #     y = np.random.uniform(size=(1, 3)).astype(np.float32)
    #     with self.graph.as_default():
    #         self.model.fit(X,y, verbose=False, batch_size=1)

    #     self.training_initialized = True

    #     while True:
    #         if self.terminate:
    #             return
    #         self.train()
    #         time.sleep(0.01)