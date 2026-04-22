from flask import Flask, render_template, jsonify, send_from_directory, request
from lottery_api import LotteryAPI, ALGORITHMS
from models import db, VisitRecord
from visit_service import VisitService
import time
import os

app = Flask(__name__, static_folder='static')

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visit_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

lottery_api = LotteryAPI()

# 创建数据库表
with app.app_context():
    db.create_all()

@app.before_request
def before_request():
    """请求前记录访问信息"""
    # 排除静态文件和API请求
    if not request.path.startswith('/static') and not request.path.startswith('/api'):
        VisitService.record_visit(request, request.path)

@app.route('/')
def index():
    # 获取当前选择的算法ID
    alg_id = int(request.args.get('alg', 1))
    lottery_api.set_algorithm(alg_id)
    return render_template('index.html', alg_id=alg_id, algorithms=ALGORITHMS)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/get_latest')
def get_latest():
    """获取最新开奖结果"""
    result = lottery_api.get_lottery_result()
    return jsonify(result)

@app.route('/api/predict')
def predict():
    """获取预测结果"""
    # 首先获取最新数据
    result = lottery_api.get_lottery_result()
    if result['success']:
        prediction = lottery_api.predict_next_number(result['data'])
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    return jsonify({
        'success': False,
        'error': '无法获取数据进行预测'
    })

@app.route('/api/set_algorithm')
def set_algorithm():
    """设置预测算法"""
    try:
        alg_id = int(request.args.get('alg', 1))
        success = lottery_api.set_algorithm(alg_id)
        return jsonify({
            'success': success,
            'message': '算法设置成功' if success else '无效的算法ID'
        })
    except ValueError:
        return jsonify({
            'success': False,
            'message': '无效的算法ID'
        })

@app.route('/admin')
def admin_page():
    """管理员页面"""
    return render_template('admin.html')

@app.route('/api/visits')
def get_visits():
    """获取访问记录API"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        records = VisitService.get_visit_records(limit=per_page, offset=offset)
        stats = VisitService.get_visit_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'records': records,
                'stats': stats,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': stats['total_visits']
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/visits/stats')
def get_visit_stats():
    """获取访问统计API"""
    try:
        stats = VisitService.get_visit_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=28288, debug=True) 