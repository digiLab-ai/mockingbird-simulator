def test_simulator_is_importable():
    import simulator


def test_simulator_is_runnable():
    from simulator import Simulator

    scenario_category = Simulator.list_scenario_categories()[0]
    scenario_name = Simulator.list_scenarios(scenario_category)[0]
    print(Simulator.scenario_info(scenario_category, scenario_name))
    sim = Simulator(scenario_category, scenario_name)
    print(sim.dynamic_data())
    sim.evolve(60.0)
    print(sim.dynamic_data())
