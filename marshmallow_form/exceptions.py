from marshmallow.exceptions import MarshmallowError


class MarshmallowFormError(MarshmallowError):
    pass


class LayoutTooFew(MarshmallowFormError):
    pass


class LayoutTooMany(MarshmallowFormError):
    pass
