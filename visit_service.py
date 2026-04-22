import requests
import json
from user_agents import parse
from models import db, VisitRecord
from datetime import datetime

class VisitService:
    @staticmethod
    def get_client_ip(request):
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    @staticmethod
    def parse_user_agent(user_agent_string):
        if not user_agent_string:
            return {
                'device_type': 'Unknown',
                'browser': 'Unknown',
                'os': 'Unknown'
            }
        
        user_agent = parse(user_agent_string)
        
        if user_agent.is_mobile:
            device_type = 'Mobile'
        elif user_agent.is_tablet:
            device_type = 'Tablet'
        elif user_agent.is_pc:
            device_type = 'Desktop'
        else:
            device_type = 'Other'
        
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        
        os = f"{user_agent.os.family} {user_agent.os.version_string}"
        
        return {
            'device_type': device_type,
            'browser': browser,
            'os': os
        }
    
    @staticmethod
    def get_location_info(ip_address):
        try:
            url = f"http://ip.taobao.com/outGetIpInfo?ip={ip_address}&accessKey=alibaba-inc"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    result = data.get('data', {})
                    return {
                        'city': result.get('city', ''),
                        'province': result.get('region', ''),
                        'country': result.get('country', '')
                    }
            
            url2 = f"http://ip-api.com/json/{ip_address}?lang=zh-CN"
            response2 = requests.get(url2, timeout=5)
            
            if response2.status_code == 200:
                data2 = response2.json()
                if data2.get('status') == 'success':
                    return {
                        'city': data2.get('city', ''),
                        'province': data2.get('regionName', ''),
                        'country': data2.get('country', '')
                    }
            
            return {
                'city': '未知',
                'province': '未知',
                'country': '未知'
            }
            
        except Exception as e:
            print(f"获取地理位置信息失败: {e}")
            return {
                'city': '未知',
                'province': '未知',
                'country': '未知'
            }
    
    @staticmethod
    def record_visit(request, page='/'):
        """记录访问信息"""
        try:
            ip_address = VisitService.get_client_ip(request)
            
            user_agent_string = request.headers.get('User-Agent', '')
            device_info = VisitService.parse_user_agent(user_agent_string)
            
            location_info = VisitService.get_location_info(ip_address)
            
            visit_record = VisitRecord(
                ip_address=ip_address,
                user_agent=user_agent_string,
                device_type=device_info['device_type'],
                browser=device_info['browser'],
                os=device_info['os'],
                city=location_info['city'],
                province=location_info['province'],
                country=location_info['country'],
                page=page
            )
            
            db.session.add(visit_record)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"记录访问信息失败: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_visit_records(limit=50, offset=0):
        """获取访问记录列表"""
        try:
            records = VisitRecord.query.order_by(VisitRecord.visit_time.desc()).limit(limit).offset(offset).all()
            return [record.to_dict() for record in records]
        except Exception as e:
            print(f"获取访问记录失败: {e}")
            return []
    
    @staticmethod
    def get_visit_stats():
        """获取访问统计信息"""
        try:
            total_visits = VisitRecord.query.count()
            
            today = datetime.now().date()
            today_visits = VisitRecord.query.filter(
                db.func.date(VisitRecord.visit_time) == today
            ).count()
            
            device_stats = db.session.query(
                VisitRecord.device_type,
                db.func.count(VisitRecord.id)
            ).group_by(VisitRecord.device_type).all()
            
            city_stats = db.session.query(
                VisitRecord.city,
                db.func.count(VisitRecord.id)
            ).group_by(VisitRecord.city).order_by(db.func.count(VisitRecord.id).desc()).limit(10).all()
            
            return {
                'total_visits': total_visits,
                'today_visits': today_visits,
                'device_stats': dict(device_stats),
                'city_stats': dict(city_stats)
            }
            
        except Exception as e:
            print(f"获取访问统计失败: {e}")
            return {
                'total_visits': 0,
                'today_visits': 0,
                'device_stats': {},
                'city_stats': {}
            } 