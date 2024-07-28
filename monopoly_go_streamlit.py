
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Define the Monopoly board
board_size = 40
railroads = [5, 15, 25, 35]
chance_spaces = [7, 22, 36]
go_space = 0
tax_spaces = [4, 38]
corner_spaces = [10, 20, 30]
community_spaces = [2, 17, 33]
utility_spaces = [12, 28]
normal_spaces = [i for i in range(board_size) if i not in railroads + chance_spaces + tax_spaces + corner_spaces + community_spaces + [go_space]]
thresholds = [0, 30, 50, 100, 300, 800, 2000]
strategies = ['tiered', 'safe', 'risky', 'half', 'tiered_minus_one', 'tiered_minus_two', 'tiered_plus_one', 'tiered_plus_two', 'random', 'scaled']
chance_advance_probability = 1/16

# Computes the probability of landing on an ideal space given a list of positions 2 through 12
def get_score(arr):
  sum = 0
  sum += arr[0] + arr[10]
  sum += 2*(arr[1] + arr[9])
  sum += 3*(arr[2] + arr[8])
  sum += 4*(arr[3] + arr[7])
  sum += 5*(arr[4] + arr[6])
  sum += 6*arr[5]
  return sum


# Creates the input to get_prob based on current position on the board; outputs the respective probability
def current_score(position, special_event_spaces):
  space_options = range((position+2), (position+13))
  arr = []
  for i in range(len(space_options)):
    if space_options[i]%board_size in tax_spaces:
      arr.append(-2)
    elif space_options[i]%board_size in corner_spaces:
      arr.append(-1)
    elif space_options[i]%board_size in chance_spaces:
      arr.append(1)
    elif space_options[i]%board_size in railroads:
      arr.append(3)
    else:
      arr.append(0)

  for i in range(len(space_options)):
    if space_options[i]%board_size in special_event_spaces:
      if arr[i] < 0:
        arr[i] = 2
      else:
        arr[i] += 2

  return get_score(arr)

# Finds the score distribution for all positions on the board given the current ideal spaces and sorts the distribution from lowest to highest score
def get_score_distribution(special_event_spaces):
  scores = []
  for position in range(board_size):
    score = current_score(position, special_event_spaces)
    scores.append(score)
  scores.sort()
  return scores

# Sets the parameters for available multipliers and returns multiplier value based on chosen strategy. Primary output for the user
def multiplier_options(dist, score, rolls_left, choice):
  if rolls_left >= 2000:
    num_of_mults = 8
    multipliers = [1, 2, 3, 5, 10, 20, 50, 100]
  elif rolls_left >= 800:
    num_of_mults = 7
    multipliers = [1, 2, 3, 5, 10, 20, 50]
  elif rolls_left >= 300:
    num_of_mults = 6
    multipliers = [1, 2, 3, 5, 10, 20]
  elif rolls_left >= 100:
    num_of_mults = 5
    multipliers = [1, 2, 3, 5, 10]
  elif rolls_left >= 50:
    num_of_mults = 4
    multipliers = [1, 2, 3, 5]
  else:
    num_of_mults = 3
    multipliers = [1, 2, 3]

  # Always applies the minimum multiplier
  def safe_multiplier():
    return 1

  # Always applies the maximum multiplier
  def risky_multiplier():
    return multipliers[-1]

  # Applies a random multiplier
  def random_multiplier():
    return random.choice(multipliers)

  # Divides the sorted probability distribution into sections equal to the number of available multipliers
  # Returns the multiplier corresponding to the section where the current probability lies
  def tiered_multiplier():
    num_of_separators = int(len(dist)/num_of_mults)
    score_thresholds = []
    for i in range(num_of_mults):
      score_thresholds.append(dist[len(dist) - 1 - num_of_separators*i])
    for i in range(len(score_thresholds)):
      if score <= score_thresholds[-(i+1)]:
        return multipliers[i]
    return multipliers[-1]

  def scaled_multiplier():
    scaled_dist = [x/dist[-1]*multipliers[-1] for x in dist]
    scaled_score = score/dist[-1]*multipliers[-1]
    for i in range(num_of_mults-1):
      avg = (multipliers[i] + multipliers[i+1])/2
      if multipliers[i] <= scaled_score < multipliers[i+1]:
        if scaled_score < avg:
          return multipliers[i]
        else:
          return multipliers[i+1]
    return multipliers[-1]
    

  #Returns lowest multiplier if the current probability is in the lower half of the sorted distribution
  #Returns highest multiplier if the current probability is in the upper half of the sorted distribution
  def half_multiplier():
    if score < (dist[0]-dist[-1])/2:
      return 1
    else:
      return multipliers[-1]

  # Removes the highest multiplier option for the tiered distribution
  def tiered_multiplier_minus_one():
    nonlocal num_of_mults
    nonlocal multipliers
    num_of_mults -= 1
    del multipliers[-1]
    return tiered_multiplier()

  # Removes the highest two multiplier options for the tiered distribution
  def tiered_multiplier_minus_two():
    nonlocal num_of_mults
    nonlocal multipliers
    num_of_mults -= 2
    del multipliers[-2:]
    return tiered_multiplier()

  # Removes the lowest multiplier option for the tiered distribution
  def tiered_multiplier_plus_one():
    nonlocal num_of_mults
    nonlocal multipliers
    num_of_mults -= 1
    del multipliers[0]
    return tiered_multiplier()

  # Removes the lowest two multiplier options for the tiered distribution
  def tiered_multiplier_plus_two():
    nonlocal num_of_mults
    nonlocal multipliers
    num_of_mults -= 2
    del multipliers[0:2]
    return tiered_multiplier()

  # Returns the output of the selected multiplier
  if choice == 'tiered':
    return tiered_multiplier()
  elif choice == 'safe':
    return safe_multiplier()
  elif choice == 'risky':
    return risky_multiplier()
  elif choice == 'half':
    return half_multiplier()
  elif choice == 'tiered_minus_one':
    return tiered_multiplier_minus_one()
  elif choice == 'tiered_minus_two':
    return tiered_multiplier_minus_two()
  elif choice == 'tiered_plus_one':
    return tiered_multiplier_plus_one()
  elif choice == 'tiered_plus_two':
    return tiered_multiplier_plus_two()
  elif choice == 'random':
    return random_multiplier()
  elif choice == 'scaled':
    return scaled_multiplier()
  else:
    print("Invalid choice")
    return None

def initialize(thresholds, strategies, chance_advance_probability):
    special_event_spaces = []
    special_event_input = st.text_input('What kind of spaces (other than RR and chance) are special event spaces (corner, tax, utility, random)? Separate answers with a space').split()

    if special_event_input[0] == 'exit':
        st.stop()

    if special_event_input[0] == 'random' and len(special_event_input) == 1:
        event = 'random'
        event_query = st.text_input('Enter all the special event spaces (numbers 1 through 39): ')
        if event_query == 'exit':
            st.stop()
        elif all(x.isdigit() and int(x) in range(40) for x in event_query.split()):
            special_event_spaces = [int(x) for x in event_query.split()]
            special_event_spaces.sort()
        else:
            st.write('Invalid input')
            st.stop()
    else:
        event = 'normal'
        for space in special_event_input:
            if space == 'corner':
                special_event_spaces.extend(corner_spaces)
            elif space == 'tax':
                special_event_spaces.extend(tax_spaces)
            elif space == 'utility':
                special_event_spaces.extend(utility_spaces)
            else:
                st.write('Invalid space')
                st.stop()

    dist = get_score_distribution(special_event_spaces)

    initial_rolls = st.text_input('Enter number of rolls: ')
    if initial_rolls.isdigit():
        initial_rolls = int(initial_rolls)
    else:
        st.write('Invalid input')
        st.stop()

    if initial_rolls < 50:
        roll_limits = [0, 10, 20, 30, 40]
    elif initial_rolls < 100:
        roll_limits = thresholds[:3]
    elif initial_rolls < 300:
        roll_limits = thresholds[:4]
    elif initial_rolls < 800:
        roll_limits = thresholds[:5]
    elif initial_rolls < 2000:
        roll_limits = thresholds[:6]
    else:
        roll_limits = thresholds

    query = st.text_input('Enter current row and space: ')
    if all(x.isdigit() for x in query.split()):
        row, space = [int(x) for x in query.split()]
        if row not in range(1, 5) or space not in range(1, 11):
            st.write('Invalid row or space')
            st.stop()
        position = (row - 1) * 10 + space
    else:
        st.write('Invalid input')
        st.stop()

    best_strategy = 'tiered'
    best_roll_limit = roll_limits[-1]

    return event, initial_rolls, dist, special_event_spaces, best_strategy, best_roll_limit, query

def finally_play_monopoly_go(thresholds, strategies, chance_advance_probability):
    st.title('Monopoly Go! Strategy Optimizer')

    if 'initialized' not in st.session_state:
        st.session_state.event, st.session_state.initial_rolls, st.session_state.dist, st.session_state.special_event_spaces, st.session_state.best_strategy, st.session_state.best_roll_limit, st.session_state.query = initialize(thresholds, strategies, chance_advance_probability)
        st.session_state.initialized = True

    if st.session_state.query == 'exit':
        return

    next_roll_update = False

    if st.session_state.event == 'normal':
        create_event_table(st.session_state.event, st.session_state.initial_rolls, st.session_state.dist, st.session_state.special_event_spaces, st.session_state.best_strategy, st.session_state.best_roll_limit, initialized=True)

    while st.session_state.event == 'random':
        if st.session_state.query == 'exit':
            break

        elif st.session_state.query == 'new threshold':
            st.session_state.initial_rolls = st.text_input('Enter number of rolls: ')
            if st.session_state.initial_rolls.isdigit():
                st.session_state.initial_rolls = int(st.session_state.initial_rolls)
                old_best_roll_limit_index = thresholds.index(st.session_state.best_roll_limit)

                for threshold in thresholds:
                    if st.session_state.initial_rolls >= threshold:
                        st.session_state.best_roll_limit = threshold

                st.write(f'To achieve the best overall results, try not to let your dice fall below {st.session_state.best_roll_limit}.')
                st.session_state.query = st.text_input('Enter current row and space: ')
                continue
            else:
                st.write('Invalid input')
                continue

        elif all(x.isdigit() for x in st.session_state.query.split()):
            row, space = [int(x) for x in st.session_state.query.split()]
            position = (row - 1) * 10 + space

            if position in st.session_state.special_event_spaces:
                if next_roll_update:
                    st.write('You landed on a token! The board has been updated for you.')
                    st.write(f'Previous token spots: {st.session_state.special_event_spaces}')

                    st.session_state.special_event_spaces.remove(position)
                    st.session_state.special_event_spaces.append(old_position)
                    st.session_state.special_event_spaces.sort()

                    st.write(f'New token spots: {st.session_state.special_event_spaces}')
                    new_token = st.text_input('Any other new token spots? (y/n) ')

                if not next_roll_update or new_token == 'y':
                    if not next_roll_update:
                        st.write("You landed on a token! Let's keep track of where it moved to.")
                        st.write(f"Previous token spots: {st.session_state.special_event_spaces}")

                    while True:
                        new_token = st.text_input('Enter new token spot (Enter 100 if not applicable): ')
                        if new_token == 'exit':
                            st.session_state.query = 'exit'
                            break
                        elif int(new_token) in range(40):
                            if not next_roll_update:
                                st.session_state.special_event_spaces.remove(position)
                            else:
                                next_roll_update = False
                            st.session_state.special_event_spaces.append(int(new_token))
                            break
                        elif new_token == '100':
                            st.session_state.special_event_spaces.remove(position)
                            next_roll_update = True
                            old_position = position
                            break
                        else:
                            st.write('Invalid input')

                    st.session_state.special_event_spaces.sort()
                    st.write(f'New token spots: {st.session_state.special_event_spaces}')
                    old_dist = st.session_state.dist.copy()
                    st.session_state.dist = get_score_distribution(st.session_state.special_event_spaces)
                    if old_dist == st.session_state.dist:
                        st.write('No change in distribution. The code needs fixing.')
                        break

            elif next_roll_update:
                st.session_state.special_event_spaces.append(old_position)
                st.write('A new token has spawned. The board has been updated for you.')
                st.session_state.special_event_spaces.sort()
                st.write(f'New token spots: {st.session_state.special_event_spaces}')
                old_dist = st.session_state.dist.copy()
                st.session_state.dist = get_score_distribution(st.session_state.special_event_spaces)
                if old_dist == st.session_state.dist:
                    st.write('No change in distribution')
                    break
                next_roll_update = False

            score = current_score(position, st.session_state.special_event_spaces)
            st.write(f'Distribution range: ({st.session_state.dist[0]}, {st.session_state.dist[-1]})')
            st.write(f'Score: {score}')

            multiplier = multiplier_options(st.session_state.dist, score, st.session_state.initial_rolls, st.session_state.best_strategy)
            st.write(multiplier)

            st.session_state.query = st.text_input('Enter current row and space: ')

        else:
            st.write('Invalid input')
            continue

    return st.session_state.event, st.session_state.initial_rolls, st.session_state.dist, score, st.session_state.best_strategy, st.session_state.best_roll_limit, st.session_state.query

finally_play_monopoly_go(thresholds, strategies, chance_advance_probability)
