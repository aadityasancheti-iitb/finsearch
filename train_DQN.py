import sys

from utils import *
from agents.DQN import Agent


if len(sys.argv) != 4:
    print("Usage: python train.py [stock] [window] [episodes]")
    exit()

stock_name, window_size, episode_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
stock_prices = stock_close_prices(stock_name)
trading_period = len(stock_prices) - 1
batch_size = 32
initial_funding = 50000

agent = Agent(window_size, balance=initial_funding)

for e in range(1, episode_count + 1):
    print('\nEpisode: {}/{}'.format(e, episode_count))
    state = generate_state(stock_prices, 0, window_size + 1)

    agent.balance = initial_funding
    total_profit = 0
    agent.inventory = []

    for t in range(trading_period):
        if t % 100 == 0:
            print('-------------------Period: {}/{}-------------------'.format(t + 1, trading_period))
        reward = 0
        action = agent.act(state)

        next_state = generate_state(stock_prices, t + 1, window_size + 1)
        previous_portfolio_value = len(agent.inventory) * stock_prices[t] + agent.balance

        # buy
        if action == 1:
            if agent.balance > stock_prices[t]:
                agent.balance -= stock_prices[t]
                agent.inventory.append(stock_prices[t])
                print('Buy: ${:.2f}'.format(stock_prices[t]))
        # sell
        elif action == 2:
            if len(agent.inventory) > 0:
                agent.balance += stock_prices[t]
                bought_price = agent.inventory.pop(0)
                profit = stock_prices[t] - bought_price
                reward = max(profit, 0)
                print('Sell: ${:.2f} | Profit: ${:.2f}'.format(stock_prices[t], profit))
        # hold
        else:
            pass  # do nothing

            current_portfolio_value = len(agent.inventory) * stock_prices[t + 1] + agent.balance
            agent.return_rates.append((current_portfolio_value - previous_portfolio_value) / previous_portfolio_value)
            agent.portfolio_values.append(current_portfolio_value)

        done = True if t == trading_period - 1 else False
        agent.remember(state, action, reward, next_state, done)
        state = next_state

        if len(agent.memory) > batch_size:
            agent.experience_replay(batch_size)

        if done:
            evaluate_portfolio_performance(agent)

    if e % 10 == 0:
        agent.model.save('saved_models/DQN_ep' + str(e) + '.h5')
        print('model saved')
