import requests
import time
from datetime import datetime, timedelta
import json
import urllib3

from config_encrypt import get_api_url, get_keno_url

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_NBR = 25

ALGORITHMS = [
    (1, 'CI算法1'), (2, 'CI算法2'), (3, 'CI算法3'),
    (4, 'CI算法4'), (5, 'CI算法5'), (6, 'CI算法6'),
    (7, 'CI算法7'), (8, 'CI算法8')
]

class LotteryAPI:
    def __init__(self):
        self.base_url = get_api_url()
        self.current_algorithm = 1  
        
    def format_lottery_data(self, draw_data):

        numbers = [
            str(draw_data['first']),
            str(draw_data['second']),
            str(draw_data['third'])
        ]
        total = sum(map(int, numbers))
        size = '大' if total >= 14 else '小'
        odd_even = '双' if total % 2 == 0 else '单'
        
        return {
            'issue': draw_data['expect'],
            'time': datetime.fromtimestamp(int(draw_data['opentimestamp'])).strftime('%H:%M:%S'),
            'numbers': f"{numbers[0]}+{numbers[1]}+{numbers[2]}={total}",
            'size': size,
            'odd_even': odd_even
        }

    def get_lottery_result(self):

        try:
            params = {
                'nbr': API_NBR
            }

            response = requests.get(
                get_api_url(),
                params=params,
                verify=False,
                timeout=15
            )

            if response.status_code == 200:
                try:
                    data = response.json()

                    if data.get('message') == 'success' and data.get('data'):
                        history = []
                        all_draws = data['data']

                        for i, draw in enumerate(all_draws):
                            num_value = draw.get('num', '0')
                            try:
                                total = int(num_value)
                            except:
                                total = 0

                            size = '大' if total >= 14 else '小'
                            combination = draw.get('combination', '')
                            odd_even = '双' if combination.endswith('双') else '单'

                            formatted_data = {
                                'issue': draw.get('nbr', ''),
                                'time': draw.get('time', ''),
                                'numbers': f"{draw.get('number', '0+0+0')}={total}",
                                'size': size,
                                'odd_even': odd_even
                            }

                            if i < len(all_draws) - 1:
                                predicted_numbers = self.get_numbers_by_algorithm(
                                    self.current_algorithm,
                                    all_draws[i+1] if i+1 < len(all_draws) else all_draws[i],
                                    all_draws[i] if i < len(all_draws) else all_draws[0],
                                    all_draws[i] if i < len(all_draws) else all_draws[0]
                                )
                                pred_total = sum(map(int, predicted_numbers))
                                prediction = {
                                    'size': '大' if pred_total >= 14 else '小',
                                    'odd_even': '双' if pred_total % 2 == 0 else '单'
                                }
                                formatted_data['prediction'] = f"{prediction['size']}{prediction['odd_even']}"

                            history.append(formatted_data)

                        latest_result = history[0]

                        next_time = None
                        countdown = 180

                        try:
                            keno_response = requests.get(
                                get_keno_url(),
                                params={'nbr': 1},
                                verify=False,
                                timeout=10
                            )
                            if keno_response.status_code == 200:
                                keno_data = keno_response.json()
                                if keno_data.get('message') == 'success':
                                    countdown_str = keno_data.get('countdown', '03:00')
                                    parts = countdown_str.split(':')
                                    countdown = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                                    countdown = min(max(countdown, 10), 300)
                                    next_time = countdown
                        except Exception as e:
                            print(f"获取keno倒计时失败: {e}")
                            countdown = 180
                            next_time = countdown

                        return {
                            'success': True,
                            'data': {
                                'issue': latest_result['issue'],
                                'time': latest_result['time'],
                                'numbers': latest_result['numbers'],
                                'next_time': next_time,
                                'countdown': countdown,
                                'history': history,
                                'api_info': {
                                    'source': 'pc28.ai',
                                    'message': data.get('message')
                                }
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'API返回错误: {data.get("message", "未知错误")}'
                        }
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {str(e)}")
                    return {
                        'success': False,
                        'error': '解析JSON数据失败',
                        'raw_response': response.text
                    }
            else:
                print(f"Request failed with status code: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API请求失败，状态码：{response.status_code}'
                }
                
        except requests.RequestException as e:
            print(f"Request exception: {str(e)}")
            return {
                'success': False,
                'error': f'请求异常：{str(e)}'
            }
    
    def get_numbers_by_algorithm(self, alg_id, first_draw, second_draw, third_draw):

        def extract_numbers(draw):
            number_str = draw.get('number', '0+0+0')
            try:
                parts = number_str.split('+')
                if len(parts) == 3:
                    return (int(parts[0]), int(parts[1]), int(parts[2]))
            except:
                pass
            num = int(draw.get('num', 0))
            return (num // 9, (num // 3) % 3, num % 3)

        f1, f2, f3 = extract_numbers(first_draw)
        s1, s2, s3 = extract_numbers(second_draw)
        t1, t2, t3 = extract_numbers(third_draw)

        if alg_id == 1:
            return (f1, s1, t1)
        elif alg_id == 2:
            return (f1, s2, t2)
        elif alg_id == 3:
            return (s2, s2, t3)
        elif alg_id == 4:
            return (t3, t3, f1)
        elif alg_id == 5:
            return (f1, t3, s2)
        elif alg_id == 6:
            return (s2, f1, t3)
        elif alg_id == 7:
            return (t3, s2, f1)
        elif alg_id == 8:
            return (s2, t3, t3)
        return (f1, s1, t1)

    def analyze_numbers(self, numbers):

        total = sum(map(int, numbers))
        size = '大' if total >= 14 else '小'
        odd_even = '双' if total % 2 == 0 else '单'
        return {
            'numbers': numbers,
            'sum': total,
            'size': size,
            'odd_even': odd_even
        }

    def predict_next_number(self, historical_data):
        try:
            params = {'nbr': 25}
            response = requests.get(
                get_api_url(),
                params=params,
                verify=False,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('message') == 'success' and len(data.get('data', [])) >= 3:
                    last_three = data['data'][:3]

                    predicted_numbers = self.get_numbers_by_algorithm(
                        self.current_algorithm,
                        last_three[0],
                        last_three[1],
                        last_three[2]
                    )

                    analysis = self.analyze_numbers(predicted_numbers)

                    numbers_str = '+'.join(map(str, analysis['numbers']))
                    prediction_text = f"{numbers_str}={analysis['sum']}({analysis['size']}{analysis['odd_even']})"

                    next_issue = None
                    if len(data.get('data', [])) > 0:
                        latest_nbr = data['data'][0].get('nbr', '0')
                        try:
                            next_issue = str(int(latest_nbr) + 1)
                        except:
                            next_issue = None

                    return {
                        'prediction': prediction_text,
                        'next_issue': next_issue,
                        'next_time': None
                    }

            return {
                'prediction': "暂无预测",
                'next_issue': None,
                'next_time': None
            }

        except Exception as e:
            print(f"预测出错: {str(e)}")
            return {
                'prediction': "预测失败",
                'next_issue': None,
                'next_time': None
            }

    def set_algorithm(self, alg_id):

        if 1 <= alg_id <= 8:
            self.current_algorithm = alg_id
            return True
        return False 