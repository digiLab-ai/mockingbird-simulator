The structure of actions and what actions mean what.

Actions are loaded in from an actions.csv file titled as such in the state.py by the \_load_actions function, then queued up by queue_actions. The function process_action_queue in state.py finds and queues up actions in preparation to be implemented in the simulation. Actions are handled then by the function \_handle_action, which identify which of the actions are to be carried out, and implement the relevant change for the simulation. Running the simulation with run.py can introduce additional actions and flights for the simulation via a Python dictionary.

state.py then has six further functions to evolve the aircraft, either organically as time passes in the simulation or as specified in the action dictionary: accelerating the aircraft relative to time annd its speed; evolving the latitudinal and longitudinal position of the plane; evolving the flight levels of the aircraft, evolving the heading of the aircraft, and then two final functions to smooth these changes, so that they are not abrupt and discrete changes but more realistic gradual actions.

At time of documentation writing, there are four available actions with two types of possible implementation:

- flight_level
- speed
- heading

Implementation can either be absolute or relative.

|              | relative                                                          | absolute                                                                                                                                   |
| ------------ | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| flight_level | Increase/decrease the flight_level by the specified value amount. | Replace the flight_level with the specified value amount as the new target flight_level; flight_level will adjust to the new target value. |
| speed        | Increase/decrease the speed by the specified value amount.        | Replace the target_speed with the specified value amount; speed will adjust to the new target value.                                       |
| heading      | Increase/decrease the heading by the specified value amount.      | Replace the heading with the specified value amount as the new target heading; heading will adjust to the new target value.                |

Bays are also a possible action; this moves the aircraft across the user's strip board.
