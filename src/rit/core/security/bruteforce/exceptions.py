class BruteForceException(Exception):
    pass


class AttackerNotRecognized(BruteForceException):
    pass


class DuplicatedBruteForceResourceDetected(BruteForceException):
    pass


class AttackerDetected(BruteForceException):
    pass
