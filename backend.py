from flask import Flask, request
import os
import json
import csv

app = Flask(__name__)


@app.route('/receive', methods=['POST'])
def receive_data():
    try:
        data = request.get_data(as_text=True)
        start_index = data.find('sessionJSON=')
        if start_index != -1:
            json_str = data[start_index + len('sessionJSON='):]
            try:
                json_data = json.loads(json_str)
                test_id = json_data.get('testId')
                if not test_id:
                    return '未找到 testId', 400

                folder_path = f'{test_id}'
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                csv_path = os.path.join(folder_path, 'data.csv')
                with open(csv_path, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    if file.tell() == 0:
                        writer.writerow([
                            'session_test_id', 'email', 'age', 'gender',
                          'session_uuid', 'trial_id', 'rating_stimulus',
                            'rating_score', 'rating_time', 'rating_comment'
                        ])

                    email = json_data['participant']['response'][0]
                    age = json_data['participant']['response'][1]
                    gender = json_data['participant']['response'][2]
                    uuid = json_data['uuid']

                    for trial in json_data['trials']:
                        trial_id = trial['id']
                        for response in trial['responses']:
                            stimulus = response['stimulus']
                            score = response['score']
                            time = response['time']
                            comment = response.get('comment', '')
                            writer.writerow([
                                test_id, email, age, gender,
                                uuid, trial_id, stimulus,
                                score, time, comment
                            ])

                return '数据保存成功', 200
            except json.JSONDecodeError:
                return 'JSON 解析错误', 400
        else:
            return '未找到 sessionJSON 数据', 400
    except Exception as e:
        return f'发生错误: {str(e)}', 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    