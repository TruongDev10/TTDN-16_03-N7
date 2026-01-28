# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # ========== DEADLINE THEO NGÀY ==========
    deadline_days_remaining = fields.Integer(
        string='Số ngày còn lại',
        compute='_compute_deadline_info',
        store=False,
        help='Số ngày còn lại đến deadline'
    )
    
    deadline_status = fields.Selection([
        ('on_time', 'Đúng hạn'),
        ('at_risk', 'Có nguy cơ'),
        ('overdue', 'Quá hạn')
    ], string='Trạng thái Deadline',
        compute='_compute_deadline_info',
        store=False,
        help='Trạng thái deadline'
    )
    
    # ========== CÔNG KHAI ==========
    is_public_progress = fields.Boolean(
        string='Công khai tiến độ',
        default=False,
        tracking=True,
        help='Cho phép công khai tiến độ cho khách hàng'
    )
    
    is_public_members = fields.Boolean(
        string='Công khai thành viên',
        default=False,
        tracking=True,
        help='Cho phép công khai danh sách thành viên'
    )
    
    # ========== AI EVALUATION ==========
    ai_evaluation_ids = fields.One2many(
        'project.ai.evaluation',
        'project_id',
        string='Đánh giá AI',
        help='Các đánh giá từ AI'
    )
    
    ai_evaluation_count = fields.Integer(
        string='Số lượng Đánh giá',
        compute='_compute_ai_evaluation_count',
        store=False
    )
    
    latest_ai_score = fields.Float(
        string='Điểm AI mới nhất',
        compute='_compute_latest_ai_score',
        store=False,
        help='Điểm đánh giá AI mới nhất'
    )
    
    @api.depends('date_end')
    def _compute_deadline_info(self):
        """Tính thông tin deadline"""
        today = fields.Date.today()
        for record in self:
            if record.date_end:
                delta = (record.date_end - today).days
                record.deadline_days_remaining = delta
                
                if delta < 0:
                    record.deadline_status = 'overdue'
                elif delta <= 7:
                    record.deadline_status = 'at_risk'
                else:
                    record.deadline_status = 'on_time'
            else:
                record.deadline_days_remaining = 0
                record.deadline_status = 'on_time'
    
    @api.depends('ai_evaluation_ids')
    def _compute_ai_evaluation_count(self):
        """Tính số lượng đánh giá"""
        for record in self:
            record.ai_evaluation_count = len(record.ai_evaluation_ids)
    
    @api.depends('ai_evaluation_ids', 'ai_evaluation_ids.ai_score')
    def _compute_latest_ai_score(self):
        """Tính điểm AI mới nhất"""
        for record in self:
            if record.ai_evaluation_ids:
                latest = record.ai_evaluation_ids.sorted('evaluation_date', reverse=True)[0]
                record.latest_ai_score = latest.ai_score if hasattr(latest, 'ai_score') else 0.0
            else:
                record.latest_ai_score = 0.0
    
    def action_create_ai_evaluation(self):
        """Tạo đánh giá AI mới"""
        for record in self:
            evaluation = self.env['project.ai.evaluation'].create({
                'name': f'Đánh giá {record.name}',
                'project_id': record.id,
            })
            evaluation.action_evaluate()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Đánh giá AI',
                'res_model': 'project.ai.evaluation',
                'res_id': evaluation.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def write(self, vals):
        # Kiểm tra điều kiện hoàn thành
        if vals.get('state') == 'done':
            # Validation logic removed based on user request ("AI is just a suggestion")
            pass

        return super(ProjectProject, self).write(vals)
