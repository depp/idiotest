@test
def skip_this():
    skip()

@test
def pass_this():
    pass

@test
def skip_rest():
    skip_module()

@test
def fail_this():
    fail("shouldn't get here")
