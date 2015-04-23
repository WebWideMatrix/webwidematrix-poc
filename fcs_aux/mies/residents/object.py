from mies.residents.acting.flow import ActingBehavior


class Resident(dict, ActingBehavior):
    def __init__(self, data, **kwargs):
        super(Resident, self).__init__(**kwargs)
        self.update(data)
