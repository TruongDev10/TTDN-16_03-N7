# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import json
import re
import urllib.request
import urllib.error


class ProjectAIEvaluation(models.Model):
    _name = 'project.ai.evaluation'
    _description = 'Đánh giá Tiến độ bằng AI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'evaluation_date desc'

    # ========== THÔNG TIN CƠ BẢN ==========
    name = fields.Char(
        string='Tên đánh giá',
        required=True,
        default=lambda self: f'Đánh giá {fields.Datetime.now().strftime("%d/%m/%Y %H:%M")}',
        tracking=True
    )
    
    evaluation_date = fields.Datetime(
        string='Ngày đánh giá',
        default=fields.Datetime.now,
        required=True,
        tracking=True
    )
    
    # ========== QUAN HỆ ==========
    project_id = fields.Many2one(
        'project.project',
        string='Dự án',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Dự án được đánh giá'
    )
    
    task_id = fields.Many2one(
        'project.task',
        string='Công việc',
        ondelete='cascade',
        tracking=True,
        help='Công việc được đánh giá (nếu đánh giá theo task)'
    )
    
    # ========== THÔNG TIN TIẾN ĐỘ ==========
    current_progress = fields.Float(
        string='Tiến độ hiện tại (%)',
        compute='_compute_progress',
        store=True,
        help='Tiến độ hiện tại của dự án/công việc'
    )
    
    deadline_date = fields.Date(
        string='Ngày deadline',
        compute='_compute_deadline',
        store=True,
        help='Ngày deadline của dự án/công việc'
    )
    
    days_remaining = fields.Integer(
        string='Số ngày còn lại',
        compute='_compute_days_remaining',
        store=True,
        help='Số ngày còn lại đến deadline'
    )
    
    is_overdue = fields.Boolean(
        string='Quá hạn',
        compute='_compute_days_remaining',
        store=True,
        help='Có quá hạn deadline không'
    )
    
    # ========== THÔNG TIN THÀNH VIÊN ==========
    team_members = fields.Text(
        string='Thành viên',
        compute='_compute_team_members',
        store=True,
        help='Danh sách thành viên tham gia'
    )
    
    member_count = fields.Integer(
        string='Số lượng thành viên',
        compute='_compute_team_members',
        store=True
    )
    
    # ========== ĐÁNH GIÁ AI ==========
    ai_evaluation = fields.Html(
        string='Đánh giá của AI',
        readonly=True,
        help='Đánh giá tiến độ từ AI'
    )
    
    ai_score = fields.Float(
        string='Điểm đánh giá (0-100)',
        help='Điểm đánh giá từ AI (0-100)',
        tracking=True
    )
    
    ai_recommendations = fields.Text(
        string='Khuyến nghị',
        help='Khuyến nghị từ AI'
    )
    
    # Chỉ số chi tiết (Enterprise Pro)
    score_time = fields.Integer(string='Điểm tiến độ', default=0)
    score_quality = fields.Integer(string='Điểm chất lượng', default=0)
    score_risk = fields.Integer(string='Chỉ số rủi ro', default=0)
    
    # ========== TRẠNG THÁI ==========
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('processing', 'Đang xử lý'),
        ('done', 'Hoàn thành'),
        ('error', 'Lỗi')
    ], string='Trạng thái', default='draft', tracking=True)
    
    # ========== CÔNG KHAI ==========
    is_public = fields.Boolean(
        string='Công khai',
        default=True,
        tracking=True,
        help='Cho phép công khai tiến độ và thành viên'
    )
    
    # ========== COMPUTE ==========
    @api.depends('project_id', 'task_id', 'project_id.state', 'task_id.state')
    def _compute_progress(self):
        """Tính tiến độ hiện tại"""
        for record in self:
            if record.task_id:
                if record.task_id.state == 'done':
                    record.current_progress = 100.0
                else:
                    record.current_progress = record.task_id.progress
            elif record.project_id:
                if record.project_id.state == 'done':
                    record.current_progress = 100.0
                else:
                    record.current_progress = record.project_id.progress
            else:
                record.current_progress = 0.0
    
    @api.depends('project_id', 'task_id')
    def _compute_deadline(self):
        """Tính deadline"""
        for record in self:
            if record.task_id and record.task_id.date_deadline:
                record.deadline_date = record.task_id.date_deadline
            elif record.project_id and record.project_id.date_end:
                record.deadline_date = record.project_id.date_end
            else:
                record.deadline_date = False
    
    @api.depends('deadline_date', 'evaluation_date')
    def _compute_days_remaining(self):
        """Tính số ngày còn lại"""
        today = fields.Date.today()
        for record in self:
            if record.deadline_date:
                delta = (record.deadline_date - today).days
                record.days_remaining = delta
                record.is_overdue = delta < 0
            else:
                record.days_remaining = 0
                record.is_overdue = False
    
    @api.depends('project_id', 'task_id')
    def _compute_team_members(self):
        """Tính danh sách thành viên"""
        for record in self:
            members = []
            if record.task_id and hasattr(record.task_id, 'employee_ids'):
                members = [emp.name for emp in record.task_id.employee_ids]
            elif record.project_id and hasattr(record.project_id, 'employee_ids'):
                members = [emp.name for emp in record.project_id.employee_ids]
            
            record.team_members = ', '.join(members) if members else 'Chưa có thành viên'
            record.member_count = len(members)
    
    # _compute_ai_evaluation removed: fields are now stored and updated by action_evaluate
    
    # ========== ORM METHODS ==========
    def action_evaluate(self):
        """Gọi AI để đánh giá tiến độ"""
        for record in self:
            record.write({'state': 'processing'})
            try:
                # Thu thập dữ liệu
                evaluation_data = self._collect_evaluation_data(record.project_id, record.task_id)
                
                # Gọi AI
                ai_response = self._call_ai_evaluation(evaluation_data)
                
                record.write({
                    'ai_evaluation': ai_response,
                    'state': 'done'
                })
                
                # Parse và cập nhật điểm số
                record._parse_ai_response(ai_response)
                # Cập nhật lại để lưu điểm số
                record.write({
                    'ai_score': record.ai_score,
                    'score_time': record.score_time,
                    'score_quality': record.score_quality,
                    'score_risk': record.score_risk,
                })
                
                # Post to Chatter (Enterprise Pro)
                self._post_ai_evaluation_to_chatter(record)
            except Exception as e:
                record.write({
                    'ai_evaluation': f'<p>Lỗi: {str(e)}</p>',
                    'state': 'error'
                })

    def _post_ai_evaluation_to_chatter(self, record):
        """Gửi thông báo đánh giá AI vào Chatter"""
        target = record.task_id or record.project_id
        if not target or not hasattr(target, 'message_post'):
            return
            
        # Nội dung tóm tắt
        color = "#d32f2f" if record.score_risk > 60 else "#388e3c"
        status_text = "CẢNH BÁO RỦI RO" if record.score_risk > 60 else "ĐÁNH GIÁ TỐT"
        
        body = f"""
            <div style="border-left: 4px solid {color}; padding-left: 10px;">
                <p><strong>AI EVALUATION - {status_text}</strong></p>
                <p><strong>Tổng điểm: {record.ai_score}/100</strong></p>
                <ul>
                    <li>Tiến độ: {record.score_time}/100</li>
                    <li>Chất lượng: {record.score_quality}/100</li>
                    <li>Rủi ro: {record.score_risk}/100</li>
                </ul>
                <p>Vui lòng kiểm tra tab <strong>Đánh giá AI</strong> để xem chi tiết.</p>
            </div>
        """
        target.message_post(body=body, message_type='comment', subtype_xmlid='mail.mt_note')

    
    def _collect_evaluation_data(self, project_id=None, task_id=None):
        """Thu thập dữ liệu để đánh giá"""
        data = {
            'evaluation_date': fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        if task_id:
            data['type'] = 'task'
            data['name'] = task_id.name
            data['progress'] = task_id.progress
            data['deadline'] = str(task_id.date_deadline) if task_id.date_deadline else None
            data['state'] = task_id.state
            data['description'] = re.sub('<[^<]+?>', '', task_id.description or '') # Strip HTML
            data['planned_hours'] = getattr(task_id, 'planned_hours', 0)
            data['effective_hours'] = getattr(task_id, 'effective_hours', 0)
            data['total_cost'] = getattr(task_id, 'total_cost', 0)
            
            # Thành viên
            if hasattr(task_id, 'employee_ids') and task_id.employee_ids:
                data['team_members'] = [emp.name for emp in task_id.employee_ids]
            
            # Subtask
            if hasattr(task_id, 'child_ids') and task_id.child_ids:
                data['subtasks'] = [
                    {
                        'name': st.name,
                        'progress': st.progress,
                        'state': st.state
                    }
                    for st in task_id.child_ids
                ]
            
            # Milestone
            if hasattr(task_id.project_id, 'milestone_ids'):
                # Tìm milestone gần nhất hoặc liên quan
                data['project_milestones'] = [
                    {'name': m.name, 'deadline': str(m.date_deadline), 'state': m.state}
                    for m in task_id.project_id.milestone_ids
                ]

        
        elif project_id:
            data['type'] = 'project'
            data['name'] = project_id.name
            data['partner'] = project_id.partner_id.name if project_id.partner_id else 'N/A'
            data['description'] = project_id.description or ''
            data['code'] = getattr(project_id, 'code', '')
            data['progress'] = project_id.progress
            data['deadline'] = str(project_id.date_end) if project_id.date_end else None
            data['state'] = project_id.state
            data['total_cost'] = getattr(project_id, 'total_cost', 0)
            
            # Milestones (Giai đoạn)
            if hasattr(project_id, 'milestone_ids'):
                data['milestones'] = [
                    {
                        'name': m.name,
                        'deadline': str(m.date_deadline),
                        'state': m.state,
                        'progress': getattr(m, 'progress', 0)
                    }
                    for m in project_id.milestone_ids
                ]
            
            # Thành viên
            if hasattr(project_id, 'employee_ids') and project_id.employee_ids:
                data['team_members'] = [emp.name for emp in project_id.employee_ids]
            
            # Tasks
            if hasattr(project_id, 'task_ids') and project_id.task_ids:
                data['tasks'] = [
                    {
                        'name': t.name,
                        'progress': t.progress,
                        'state': t.state,
                        'deadline': str(t.date_deadline) if t.date_deadline else None,
                        'cost': getattr(t, 'total_cost', 0)
                    }
                    for t in project_id.task_ids
                ]
                data['task_count'] = len(project_id.task_ids)
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _call_ai_evaluation(self, evaluation_data):
        """Gọi AI để đánh giá"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('google.gemini.api_key', '')
        api_type = self.env['ir.config_parameter'].sudo().get_param('project_ai_analytics.api_type', 'gemini')
        api_url = self.env['ir.config_parameter'].sudo().get_param('project_ai_analytics.ai_base_url', '')
        
        if not api_key:
            return '<p>Vui lòng cấu hình API key trong Settings > Technical > Parameters > System Parameters</p>'
        
        system_prompt = """Bạn là Cố vấn Quản trị Dự án Thông minh.
Nhiệm vụ: Phân tích đánh giá SẮC BÉN, minh bạch rõ ràng.

QUY TẮC CỐT LÕI:
1. **Thông minh & Ngắn gọn**: Đi thẳng vào vấn đề.
2. **Cảnh báo chuẩn xác**: Cảnh báo ĐỎ nếu nguy cấp.
3. **Phân định rõ Điểm số (Tốt/Xấu) và Rủi ro (An toàn/Nguy hiểm)**: Người dùng cần biết chính xác họ đang ở mức nào.

CẤU TRÚC PHẢN HỒI (HTML):
- <h3>1. BÁO CÁO CHI TIẾT & CẢNH BÁO</h3>
  Tóm tắt tình trạng. Nếu nghiêm trọng, dùng thẻ <b style="color: red;">CẢNH BÁO</b>.

- <h3>2. ĐÁNH GIÁ MỨC ĐỘ HOÀN THÀNH</h3>
  - Tiến độ thực tế: ...%
  - Chất lượng kết quả: ...

- <h3>3. BẢNG ĐIỂM HIỆU SUẤT & RỦI RO (QUAN TRỌNG)</h3>
  Phải ghi rõ trạng thái (Tốt/Khá/TB/Kém) bên cạnh số điểm.
  
  - **Điểm Tiến độ (Time Score)**: X/100 (Càng cao càng TỐT). Cần ghi chú: (Tốt / Chậm trễ / Nghiêm trọng).
  - **Điểm Chất lượng (Quality Score)**: Y/100 (Càng cao càng TỐT). Cần ghi chú: (Xuất sắc / Đạt / Cần cải thiện).
  - **CHỈ SỐ RỦI RO (Risk Index)**: Z/100 (Càng cao càng NGUY HIỂM). 
    * 0-30: <span style="color: green">An toàn</span>
    * 31-70: <span style="color: orange">Cảnh báo</span>
    * 71-100: <span style="color: red">NGUY HIỂM</span>

- <h3>4. KHUYẾN NGHỊ HÀNH ĐỘNG</h3>
  - [Hành động 1]
  - [Hành động 2]

Hãy bắt đầu bằng dòng: "Điểm đánh giá: X/100" (Điểm trung bình trọng số: 40% Tiến độ + 40% Chất lượng - 20% Rủi ro)."""
        
        user_prompt = f"""Dữ liệu dự án:
{evaluation_data}

Yêu cầu: Đánh giá và phân loại rõ ràng (An toàn/Nguy hiểm)."""
        
        # Gọi API theo loại (Gemini hoặc OpenAI)
        if api_type == 'gemini':
            return self._call_gemini_evaluation(api_key, api_url, system_prompt, user_prompt)
        else:
            return self._call_openai_evaluation(api_key, api_url, system_prompt, user_prompt)
    
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
        # Danh sách các model để thử (theo thứ tự ưu tiên - mới nhất trước)
        models_to_try = [
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-latest',
            'gemini-1.5-pro',
            'gemini-pro',
        ]
        
        for model in models_to_try:
            if self._test_gemini_model(api_key, model):
                # Lưu model hoạt động vào system parameter
                self.env['ir.config_parameter'].sudo().set_param('project_ai_analytics.ai_model', model)
                return model
        
        return None
    
    
    def _call_gemini_evaluation(self, api_key, api_url, system_prompt, user_prompt):
        """Gọi Gemini API để đánh giá"""
        # Lấy model name từ system parameter
        model_name = self.env['ir.config_parameter'].sudo().get_param('project_ai_analytics.ai_model', 'gemini-1.5-flash')
        
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
                'temperature': 0.4,
                'maxOutputTokens': 8192,
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
                        return f'<div>{answer}</div>'
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
                        return self._call_gemini_evaluation(api_key, None, system_prompt, user_prompt)
            except:
                error_msg = str(e)
            return f'<p>Lỗi kết nối API: {error_msg}</p>'
        except Exception as e:
            return f'<p>Lỗi kết nối API: {str(e)}</p>'
    
    def _call_openai_evaluation(self, api_key, api_url, system_prompt, user_prompt):
        """Gọi OpenAI API để đánh giá"""
        # Nếu không có URL, dùng default
        if not api_url:
            api_url = 'https://api.openai.com/v1/chat/completions'
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 1500
        }
        
        try:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(api_url, data=data_bytes, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    return f'<div>{answer}</div>'
                else:
                    return '<p>Không nhận được phản hồi từ AI</p>'
        except Exception as e:
            return f'<p>Lỗi kết nối API: {str(e)}</p>'
    
    def _parse_ai_response(self, html_response):
        """Parse điểm số từ AI response"""
        import re
        # Tìm điểm số trong format "Điểm đánh giá: X/100" hoặc "X/100"
        patterns = [
            r'Điểm đánh giá:\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*/\s*100',
            r'điểm[:\s]+(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_response, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    if 0 <= score <= 100:
                        self.ai_score = score
                        return
                except:
                    pass
        
        # Nếu không tìm thấy, tính điểm dựa trên tiến độ
        if self.current_progress:
            self.ai_score = self.current_progress
        else:
            self.ai_score = 0.0
