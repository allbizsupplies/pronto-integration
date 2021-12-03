
class ValidationError(BaseException):
    pass


class SubmitError(BaseException):
    pass


class OrderNotFoundException(BaseException):

    def __init__(self, oid):
        super().__init__("Order ID {} not found".format(oid))


class SaleNotOpenException(BaseException):

    def __init__(self):
        super().__init__("You need to have a sale open in POS and ready to enter items.")


class ProntoStatusException(Exception):

    def __init__(self, expected_status, actual_status):
        super().__init__(
            "Expected status: `{}`, actual status: {}". format(
                expected_status, actual_status))


class ProntoStatusBarException(Exception):

    def __init__(self, expected_status, actual_status):
        super().__init__(
            "Unable to find Pronto window.". format(
                expected_status, actual_status))
