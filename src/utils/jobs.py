def both_blinds_freeze(config):
    config['pins']['freeze_left'].on()
    config['pins']['freeze_right'].on()
    time.sleep(0.3)
    config['pins']['freeze_left'].off()
    config['pins']['freeze_right'].off()


def both_blinds_down(config):
    config['pins']['down_left'].on()
    config['pins']['down_right'].on()
    time.sleep(0.3)
    config['pins']['down_left'].off()
    config['pins']['down_right'].off()


def both_blinds_up(config):
    config['pins']['up_left'].on()
    config['pins']['up_right'].on()
    time.sleep(0.3)
    config['pins']['up_left'].off()
    config['pins']['up_right'].off()
