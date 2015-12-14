def includeme(config):
    # look into following modules' includeme function
    # in order to register routes
    config.include(__name__ + '.camera')
    #config.include(__name__ + '.live')
    config.scan()             # scan to register view callables, must be last statement