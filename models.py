from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class VisitRecord(db.Model):
    """访问记录模型"""
    __tablename__ = 'visit_records'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, comment='IP地址')
    user_agent = db.Column(db.Text, nullable=True, comment='用户代理')
    device_type = db.Column(db.String(50), nullable=True, comment='设备类型')
    browser = db.Column(db.String(100), nullable=True, comment='浏览器')
    os = db.Column(db.String(100), nullable=True, comment='操作系统')
    city = db.Column(db.String(100), nullable=True, comment='城市')
    province = db.Column(db.String(100), nullable=True, comment='省份')
    country = db.Column(db.String(100), nullable=True, comment='国家')
    visit_time = db.Column(db.DateTime, default=datetime.utcnow, comment='访问时间')
    page = db.Column(db.String(100), nullable=True, comment='访问页面')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'city': self.city,
            'province': self.province,
            'country': self.country,
            'timestamp': int(self.visit_time.timestamp()),
            'path': self.page
        } 