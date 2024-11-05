class SummaryScoreRecord:
    def __init__(self, id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank):
        self.id = id
        self.submission_time = submission_time
        self.total_absolute_score = total_absolute_score
        self.total_relative_score = total_relative_score
        self.invalid_score_count = invalid_score_count
        self.relative_rank = relative_rank
    
    def add_score(self, detail_record, relative_score):
        if (detail_record.absolute_score is not None):
            self.total_absolute_score += detail_record.absolute_score
        else:
            self.invalid_score_count += 1

        self.total_relative_score += relative_score

class SummaryScoreRecords:
    def __init__(self, records):
        self.records = records