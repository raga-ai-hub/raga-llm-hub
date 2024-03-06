from signal import SIGTERM  # or SIGKILL

from psutil import process_iter


def killport(port: int):
    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port == port:
                proc.send_signal(SIGTERM)  # or SIGKILL


def pick_matching_keys_from_dict(target_dict: dict, keys: list[str] = None):
    if keys is None or len(keys) < 1:
        return target_dict
    result = {}
    for k in list(filter(None, keys)):
        for dk in target_dict:
            if dk.startswith(k):
                result[dk] = target_dict[dk]
    return result


def group_by_data_point_id(results: list):
    groups = {}
    for result in results:
        data_point_id = result.get('dataset_id')
        if data_point_id not in groups:
            groups[data_point_id] = []
        groups[data_point_id].append(result)
    result = []
    for data_point_id, tests in groups.items():
        row = {}
        row['data_point_id'] = data_point_id
        for test in tests:
            row['prompt'] = test.get('prompt', row.get('prompt'))
            row['response'] = test.get('response', row.get('response'))
            row['context'] = test.get('context', row.get('context'))
            row['expected_response'] = test.get(
                'expected_response', row.get('expected_response'))
            if 'dynamic' not in row:
                row['dynamic'] = []

            score = test.get('score')
            if score is not None:
                if isinstance(test.get('score'), dict):
                    score = ', '.join(map(lambda x: '%.3f'%(x), test.get('score').values()))
                else:
                    score = float('%.3f'%(test.get('score')))
            row['dynamic'].append({
                'test_name': test.get('test_name'),
                'test_run_id': test.get('test_run_id'),
                'is_passed': test.get('is_passed'),
                'threshold': test.get('threshold'),
                'score': score,
                'evaluated_with': test.get('evaluated_with'),
            })
        result.append(row)
    return result


def get_test_for_test_run_id(jsonData, testRunId):
    for d in jsonData:
        if d.get('test_run_id') == testRunId:
            return d

def get_test_name_for_test_run_id(jsonData, testRunId):
    return get_test_for_test_run_id(jsonData, testRunId).get('test_name')
