# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class AIQAController(http.Controller):

    @http.route('/project_ai_qa/ask', type='json', auth='user', methods=['POST'])
    def ask_ai(self, question, project_id=None, task_id=None):
        """API endpoint để hỏi AI"""
        try:
            qa_record = request.env['project.ai.qa'].create({
                'question': question,
                'project_id': project_id,
                'task_id': task_id,
            })
            
            return {
                'success': True,
                'answer': qa_record.answer,
                'state': qa_record.state,
                'id': qa_record.id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/project_ai_qa/history', type='json', auth='user', methods=['POST'])
    def get_history(self, project_id=None, task_id=None, limit=10):
        """Lấy lịch sử câu hỏi"""
        domain = []
        if project_id:
            domain.append(('project_id', '=', project_id))
        if task_id:
            domain.append(('task_id', '=', task_id))
        
        records = request.env['project.ai.qa'].search(domain, limit=limit, order='create_date desc')
        
        return {
            'success': True,
            'history': [{
                'id': r.id,
                'question': r.question,
                'answer': r.answer,
                'create_date': r.create_date.strftime('%Y-%m-%d %H:%M:%S') if r.create_date else '',
            } for r in records]
        }
