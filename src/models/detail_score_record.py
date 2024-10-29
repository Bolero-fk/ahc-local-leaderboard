class DetailScoreRecord:
    def __init__(self, input_test_case, absolute_score, top_score):
        self.input_test_case = input_test_case
        self.absolute_score = absolute_score
        self.top_score = top_score

class TopDetailScoreRecord(DetailScoreRecord):
    def __init__(self, input_test_case, top_score, id):
        super().__init__(input_test_case, top_score, top_score)
        self.id = id

class DetailScoreRecords:
    def __init__(self, id, records):
        self.id = id
        self.records = records
