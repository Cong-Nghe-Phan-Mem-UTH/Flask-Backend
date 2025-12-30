from flask import jsonify
from infrastructure.databases import get_session
from infrastructure.models.table_model import TableModel
from infrastructure.models.guest_model import GuestModel
from domain.exceptions import EntityError
from utils.helpers import random_id
from sqlalchemy.exc import IntegrityError

def get_table_list_service():
    """Get all tables"""
    session = get_session()
    try:
        tables = session.query(TableModel).order_by(TableModel.created_at.desc()).all()
        return jsonify({
            'data': [table.to_dict() for table in tables],
            'message': 'Lấy danh sách bàn thành công!'
        }), 200
    finally:
        session.close()

def get_table_detail_service(table_number):
    """Get table detail"""
    session = get_session()
    try:
        table = session.query(TableModel).get_or_404(table_number)
        return jsonify({
            'data': table.to_dict(),
            'message': 'Lấy thông tin bàn thành công!'
        }), 200
    finally:
        session.close()

def create_table_service(body):
    """Create table"""
    session = get_session()
    try:
        token = random_id()
        table = TableModel(
            number=body['number'],
            capacity=body['capacity'],
            status=body.get('status', 'Available'),
            token=token
        )
        session.add(table)
        session.commit()
        session.refresh(table)
        return jsonify({
            'data': table.to_dict(),
            'message': 'Tạo bàn thành công!'
        }), 200
    except IntegrityError:
        session.rollback()
        raise EntityError([{'field': 'number', 'message': 'Số bàn này đã tồn tại'}])
    finally:
        session.close()

def update_table_service(table_number, body):
    """Update table"""
    session = get_session()
    try:
        table = session.query(TableModel).get_or_404(table_number)
        
        if body.get('changeToken'):
            token = random_id()
            table.token = token
            # Clear guest refresh tokens
            session.query(GuestModel).filter_by(table_number=table_number).update({
                'refresh_token': None,
                'refresh_token_expires_at': None
            })
        
        table.status = body.get('status', table.status)
        table.capacity = body.get('capacity', table.capacity)
        session.commit()
        session.refresh(table)
        return jsonify({
            'data': table.to_dict(),
            'message': 'Cập nhật bàn thành công!'
        }), 200
    finally:
        session.close()

def delete_table_service(table_number):
    """Delete table"""
    session = get_session()
    try:
        table = session.query(TableModel).get_or_404(table_number)
        session.delete(table)
        session.commit()
        return jsonify({
            'data': table.to_dict(),
            'message': 'Xóa bàn thành công!'
        }), 200
    finally:
        session.close()

