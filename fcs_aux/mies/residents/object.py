from mies.residents.acting.flow import ActingBehavior


class Resident(dict, ActingBehavior):
    def __init__(self, data):
        self.update(data)
