from mies.residents.acting.action_status import ManageActionBehavior
from mies.residents.acting.flow import ActingBehavior


class Resident(dict, ActingBehavior, ManageActionBehavior):
    def __init__(self, data):
        self.update(data)
