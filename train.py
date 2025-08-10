from environment import HybridEnvironment
from qlearning import QLearningAgent

env = HybridEnvironment()
agent = QLearningAgent()

# Eğitim yoksa yapılır, varsa yüklenir
agent.train(env, episodes=10000)

# Test
state = env.reset()
done = False
while not done:
    action = agent.get_best_action(state)
    state, reward, done, _ = env.step(action)
