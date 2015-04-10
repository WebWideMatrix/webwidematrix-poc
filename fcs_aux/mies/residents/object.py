from mies.residents.acting.flow import ActingBehavior


class Resident(object, ActingBehavior):
    def __init__(self, data):
        self.data = data
