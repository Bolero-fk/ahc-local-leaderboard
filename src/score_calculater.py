import os
import subprocess

class TestCaseScore:
    """テストケースのスコアを管理するクラス"""
    def __init__(self, file_name, score):
        self.file_name = file_name
        self.score = score

    def __repr__(self):
        return f"TestCaseScore(file_name='{self.file_name}', score={self.score})"
    
def is_valid_output(stdout):
    """標準出力が期待するフォーマットか確認する関数"""
    return len(stdout.decode('utf-8').split('\n')) == 2

def calculate_all_scores():
    """全てのテストケースのスコアを計算する関数"""
    test_case_scores = []
    input_file_paths = os.listdir('in')
    input_file_paths.sort()

    for sample_path in input_file_paths:
        # 入力ファイルと出力ファイルのパスを設定
        input_file = 'in/' + sample_path
        output_file = 'out/' + sample_path

        # スコア計算機を実行
        with open(input_file) as fin:
            try:
                with open(output_file) as fout:
                    score_process = subprocess.run(
                        ['cargo', 'run', '-r', '--bin', 'vis', fin.name, fout.name], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.DEVNULL
                    )

                    if(not is_valid_output(score_process.stdout)):
                        raise Exception("Error: calculate score ", input_file)

                    score = float(score_process.stdout.decode('utf-8').split(' ')[-1].strip())
            except:
                score = None
            test_case_scores.append(TestCaseScore(sample_path, score))

    return test_case_scores
                

def execute():
    return calculate_all_scores()

if __name__ == "__main__":
    execute()