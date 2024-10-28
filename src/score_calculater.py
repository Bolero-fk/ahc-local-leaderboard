import os
import subprocess

from test_case import TestCase

def is_valid_output(stdout):
    """標準出力が期待するフォーマットか確認する関数"""
    return len(stdout.decode('utf-8').split('\n')) == 2

def calculate_all_scores(submit_file):
    """全てのテストケースのスコアを計算する関数"""
    test_case_scores = []
    input_file_paths = os.listdir('in')
    input_file_paths.sort()

    for sample_path in input_file_paths:
        # 入力ファイルと出力ファイルのパスを設定
        input_file = 'in/' + sample_path
        output_file = submit_file + '/' + sample_path

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

                    score = int(score_process.stdout.decode('utf-8').split(' ')[-1].strip())
            except:
                score = None
            test_case_scores.append(TestCase(sample_path, score))

    return test_case_scores
                

def execute(submit_file='out'):
    return calculate_all_scores(submit_file)

if __name__ == "__main__":
    execute()