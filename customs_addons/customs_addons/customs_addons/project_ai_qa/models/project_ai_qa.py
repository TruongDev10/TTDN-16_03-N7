# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
import re
import urllib.request
import urllib.parse
import urllib.error


class ProjectAIQA(models.Model):
    _name = 'project.ai.qa'
    _description = 'AI Q&A về Dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # ========== THÔNG TIN CƠ BẢN ==========
    question = fields.Text(
        string='Câu hỏi',
        required=True,
        tracking=True,
        help='Câu hỏi của người dùng'
    )
    
    answer = fields.Html(
        string='Câu trả lời',
        readonly=True,
        help='Câu trả lời từ AI'
    )
    
    # ========== THÔNG TIN DỰ ÁN ==========
    project_id = fields.Many2one(
        'project.project',
        string='Dự án',
        ondelete='cascade',
        help='Dự án liên quan (nếu có)'
    )
    
    task_id = fields.Many2one(
        'project.task',
        string='Công việc',
        ondelete='cascade',
        help='Công việc liên quan (nếu có)'
    )
    
    # ========== TRẠNG THÁI ==========
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('processing', 'Đang xử lý'),
        ('done', 'Hoàn thành'),
        ('error', 'Lỗi')
    ], string='Trạng thái', default='draft', tracking=True)
    
    # ========== THÔNG TIN AI ==========
    ai_model = fields.Char(
        string='AI Model',
        default='gpt-3.5-turbo',
        help='Model AI được sử dụng'
    )
    
    tokens_used = fields.Integer(
        string='Tokens đã dùng',
        readonly=True,
        help='Số tokens đã sử dụng'
    )
    
    # ========== ORM METHODS ==========
    def action_ask_ai(self):
        """Gửi câu hỏi đến AI và nhận câu trả lời"""
        for record in self:
            record.write({'state': 'processing'})
            try:
                # Lấy dữ liệu dự án liên quan
                context_data = self._get_project_context(record.project_id, record.task_id)
                
                # Gọi AI API (cần cấu hình API key trong settings)
                answer = self._call_ai_api(record.question, context_data)
                
                record.write({
                    'answer': answer,
                    'state': 'done'
                })
            except Exception as e:
                record.write({
                    'answer': f'<p>Lỗi: {str(e)}</p>',
                    'state': 'error'
                })
    
    def _get_project_context(self, project_id=None, task_id=None):
        """Lấy dữ liệu context về dự án để cung cấp cho AI"""
        context = {}
        
        if project_id:
            # Sử dụng getattr để tránh lỗi nếu field không tồn tại
            project_data = {
                'name': project_id.name,
                'code': getattr(project_id, 'code', ''),
                'state': project_id.state,
                'progress': project_id.progress,
                'date_start': str(project_id.date_start) if project_id.date_start else None,
                'date_end': str(project_id.date_end) if project_id.date_end else None,
            }
            
            # Lấy danh sách nhân viên
            if hasattr(project_id, 'employee_ids') and project_id.employee_ids:
                project_data['employees'] = [
                    {
                        'name': emp.name,
                        'job_title': emp.job_id.name if emp.job_id else '',
                        'department': emp.department_id.name if emp.department_id else '',
                    }
                    for emp in project_id.employee_ids
                ]
                project_data['employee_count'] = len(project_id.employee_ids)
            
            # Lấy danh sách công việc
            if hasattr(project_id, 'task_ids') and project_id.task_ids:
                tasks = []
                for task in project_id.task_ids:
                    task_info = {
                        'name': task.name,
                        'state': task.state,
                        'progress': task.progress,
                    }
                    # Lấy nhân viên trong task
                    if hasattr(task, 'employee_ids') and task.employee_ids:
                        task_info['employees'] = [emp.name for emp in task.employee_ids]
                    tasks.append(task_info)
                project_data['tasks'] = tasks
                project_data['task_count'] = len(tasks)
            
            # Thêm các field từ module khác nếu có
            if hasattr(project_id, 'total_hours'):
                project_data['total_hours'] = project_id.total_hours
            if hasattr(project_id, 'total_cost'):
                project_data['total_cost'] = project_id.total_cost
            
            context['project'] = project_data
        
        if task_id:
            # Sử dụng getattr để tránh lỗi nếu field không tồn tại
            task_data = {
                'name': task_id.name,
                'state': task_id.state,
                'progress': task_id.progress,
            }
            
            # Lấy nhân viên trong task
            if hasattr(task_id, 'employee_ids') and task_id.employee_ids:
                task_data['employees'] = [
                    {
                        'name': emp.name,
                        'job_title': emp.job_id.name if emp.job_id else '',
                    }
                    for emp in task_id.employee_ids
                ]
            
            # Lấy thông tin dự án của task
            if hasattr(task_id, 'project_id') and task_id.project_id:
                task_data['project_name'] = task_id.project_id.name
            
            # Thêm các field từ module khác nếu có
            if hasattr(task_id, 'planned_hours'):
                task_data['planned_hours'] = task_id.planned_hours
            if hasattr(task_id, 'effective_hours'):
                task_data['effective_hours'] = task_id.effective_hours
            if hasattr(task_id, 'total_cost'):
                task_data['total_cost'] = task_id.total_cost
            
            context['task'] = task_data
        
        return json.dumps(context, ensure_ascii=False, indent=2)
    
    def _call_ai_api(self, question, context_data):
        """Gọi AI API để nhận câu trả lời"""
        # Lấy API key và type từ system parameters
        api_key = self.env['ir.config_parameter'].sudo().get_param('project_ai_qa.api_key', '')
        api_type = self.env['ir.config_parameter'].sudo().get_param('project_ai_qa.api_type', 'gemini')
        api_url = self.env['ir.config_parameter'].sudo().get_param('project_ai_qa.api_url', '')
        
        if not api_key:
            return '<p>Vui lòng cấu hình API key trong Settings > Technical > Parameters > System Parameters</p>'
        
        # Chuẩn bị prompt
        system_prompt = """Bạn là trợ lý AI chuyên về quản lý dự án trên Odoo 15. 
Bạn có nhiệm vụ trả lời các câu hỏi về dự án dựa trên dữ liệu được cung cấp.

QUAN TRỌNG:
- Trả lời bằng tiếng Việt
- Chỉ sử dụng thông tin có trong dữ liệu được cung cấp
- Nếu dữ liệu không có thông tin, hãy nói rõ "Không có thông tin trong dữ liệu"
- Trả lời ngắn gọn, rõ ràng, dễ hiểu
- Khi liệt kê nhân viên, hãy liệt kê đầy đủ tên từng người"""
        
        user_prompt = f"""Dữ liệu dự án (JSON):
{context_data}

Câu hỏi của người dùng: {question}

Yêu cầu: Hãy phân tích dữ liệu JSON trên và trả lời câu hỏi một cách chính xác. 
Nếu câu hỏi về nhân viên, hãy liệt kê đầy đủ tên các nhân viên từ trường 'employees' trong dữ liệu."""
        
        # Gọi API theo loại (Gemini hoặc OpenAI)
        if api_type == 'gemini':
            return self._call_gemini_api(api_key, api_url, system_prompt, user_prompt)
        else:
            return self._call_openai_api(api_key, api_url, system_prompt, user_prompt)
    
    def _test_gemini_model(self, api_key, model_name):
        """Test xem model Gemini có hoạt động không"""
        try:
            url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}'
            test_data = {
                'contents': [{
                    'parts': [{'text': 'test'}]
                }]
            }
            headers = {'Content-Type': 'application/json'}
            data_bytes = json.dumps(test_data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if 'candidates' in result and len(result['candidates']) > 0:
                    return True
                return False
        except:
            return False
    
    def _find_working_gemini_model(self, api_key):
        """Tự động tìm model Gemini hoạt động"""
        # Danh sách các model để thử (theo thứ tự ưu tiên)
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-1.5-flash-8b',
            'gemini-pro',
        ]
        
        for model in models_to_try:
            if self._test_gemini_model(api_key, model):
                # Lưu model hoạt động vào system parameter
                self.env['ir.config_parameter'].sudo().set_param('project_ai_qa.model_name', model)
                return model
        
        return None
    
    def _call_gemini_api(self, api_key, api_url, system_prompt, user_prompt):
        """Gọi Gemini API"""
        # Lấy model name từ system parameter
        model_name = self.env['ir.config_parameter'].sudo().get_param('project_ai_qa.model_name', 'gemini-1.5-flash')
        
        # Test model trước khi dùng
        if not self._test_gemini_model(api_key, model_name):
            # Nếu model không hoạt động, tự động tìm model khác
            working_model = self._find_working_gemini_model(api_key)
            if working_model:
                model_name = working_model
            else:
                return '<p>Lỗi: Không tìm thấy model Gemini nào hoạt động. Vui lòng kiểm tra API key và kết nối mạng.</p>'
        
        # Xây dựng URL
        api_url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent'
        full_url = f"{api_url}?key={api_key}"
        
        # Chuẩn bị prompt cho Gemini (kết hợp system và user prompt)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Format request cho Gemini
        data = {
            'contents': [{
                'parts': [{
                    'text': full_prompt
                }]
            }],
            'generationConfig': {
                'temperature': 0.3,
                'maxOutputTokens': 1000,
            }
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(full_url, data=data_bytes, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        answer = candidate['content']['parts'][0].get('text', '')
                        # Lấy token count nếu có
                        if 'usageMetadata' in result:
                            tokens = result['usageMetadata'].get('totalTokenCount', 0)
                            self.tokens_used = tokens
                        return f'<p>{answer}</p>'
                    else:
                        return '<p>Không nhận được phản hồi từ AI</p>'
                else:
                    error_msg = result.get('error', {}).get('message', 'Không nhận được phản hồi từ AI')
                    return f'<p>Lỗi: {error_msg}</p>'
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('error', {}).get('message', str(e))
                # Nếu lỗi do model, thử tìm model khác
                if 'not found' in error_msg.lower() or 'not supported' in error_msg.lower():
                    working_model = self._find_working_gemini_model(api_key)
                    if working_model:
                        # Thử lại với model mới
                        return self._call_gemini_api(api_key, None, system_prompt, user_prompt)
            except:
                error_msg = str(e)
            return f'<p>Lỗi kết nối API: {error_msg}</p>'
        except Exception as e:
            return f'<p>Lỗi kết nối API: {str(e)}</p>'
    
    def _call_openai_api(self, api_key, api_url, system_prompt, user_prompt):
        """Gọi OpenAI API"""
        # Nếu không có URL, dùng default
        if not api_url:
            api_url = 'https://api.openai.com/v1/chat/completions'
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.ai_model or 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 1000
        }
        
        try:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(api_url, data=data_bytes, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', 0)
                    self.tokens_used = tokens
                    return f'<p>{answer}</p>'
                else:
                    return '<p>Không nhận được phản hồi từ AI</p>'
        except Exception as e:
            return f'<p>Lỗi kết nối API: {str(e)}</p>'
    
    def action_test_api(self):
        """Test API connection và tìm model hoạt động"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('project_ai_qa.api_key', '')
        if not api_key:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Lỗi',
                    'message': 'Vui lòng cấu hình API key trước',
                    'type': 'danger',
                    'sticky': False,
                }
            }
        
        working_model = self._find_working_gemini_model(api_key)
        if working_model:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành công',
                    'message': f'Đã tìm thấy model hoạt động: {working_model}',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Lỗi',
                    'message': 'Không tìm thấy model Gemini nào hoạt động. Vui lòng kiểm tra API key.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
    
    @api.model
    def create(self, vals):
        """Tự động gọi AI khi tạo câu hỏi mới"""
        record = super(ProjectAIQA, self).create(vals)
        if vals.get('question'):
            record.action_ask_ai()
        return record
