from time import sleep


def both_blinds_freeze(config):
    config['pins']['freeze_left'].set_for_time()
    config['pins']['freeze_right'].set_for_time()


def both_blinds_down(config):
    config['pins']['down_left'].set_for_time()
    config['pins']['down_right'].set_for_time()


def both_blinds_up(config):
    config['pins']['up_left'].set_for_time()
    config['pins']['up_right'].set_for_time()
