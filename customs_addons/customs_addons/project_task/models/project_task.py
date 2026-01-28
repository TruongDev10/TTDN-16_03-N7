# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class ProjectTask(models.Model):
    _name = 'project.task'
    _description = 'Công việc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, date_deadline asc, priority desc, id desc'
    _parent_name = 'parent_id'
    _parent_store = True

    # ========== THÔNG TIN CƠ BẢN ==========
    name = fields.Char(
        string='Tên công việc',
        required=True,
        tracking=True,
        index=True,
        help='Tên của công việc'
    )
    
    description = fields.Html(
        string='Mô tả',
        help='Mô tả chi tiết về công việc'
    )
    
    # ========== QUAN HỆ VỚI DỰ ÁN ==========
    project_id = fields.Many2one(
        'project.project',
        string='Dự án',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True,
        help='Dự án chứa công việc này'
    )
    
    # ========== QUAN HỆ PARENT/CHILD (SUBTASK) ==========
    parent_id = fields.Many2one(
        'project.task',
        string='Công việc cha',
        ondelete='cascade',
        tracking=True,
        index=True,
        help='Công việc cha (nếu đây là subtask)'
    )
    
    child_ids = fields.One2many(
        'project.task',
        'parent_id',
        string='Công việc con',
        help='Các subtask của công việc này'
    )
    
    subtask_count = fields.Integer(
        string='Số lượng Subtask',
        compute='_compute_subtask_count',
        store=False
    )
    
    parent_path = fields.Char(
        index=True,
        unlink=False
    )
    
    # ========== THỜI GIAN ==========
    date_start = fields.Datetime(
        string='Ngày bắt đầu',
        default=fields.Datetime.now,
        tracking=True,
        help='Ngày và giờ bắt đầu công việc'
    )
    
    date_deadline = fields.Date(
        string='Ngày deadline',
        tracking=True,
        index=True,
        help='Ngày deadline của công việc'
    )
    
    date_end = fields.Datetime(
        string='Ngày kết thúc',
        compute='_compute_date_end',
        store=True,
        help='Ngày và giờ kết thúc công việc'
    )
    
    # ========== TRẠNG THÁI & WORKFLOW ==========
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('todo', 'Cần làm'),
        ('in_progress', 'Đang làm'),
        ('review', 'Đang xem xét'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string='Trạng thái', default='draft', tracking=True, required=True, index=True)
    
    # ========== ĐỘ ƯU TIÊN ==========
    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình thường'),
        ('2', 'Cao'),
        ('3', 'Rất cao')
    ], string='Độ ưu tiên', default='1', tracking=True)
    
    # ========== TIẾN ĐỘ ==========
    progress = fields.Float(
        string='Tiến độ (%)',
        default=0.0,
        tracking=True,
        help='Tiến độ hoàn thành công việc (0-100%)'
    )
    
    # ========== THỜI GIAN ƯỚC TÍNH ==========
    planned_hours = fields.Float(
        string='Giờ công dự kiến',
        default=0.0,
        tracking=True,
        help='Số giờ công dự kiến để hoàn thành công việc'
    )
    
    effective_hours = fields.Float(
        string='Giờ công thực tế',
        compute='_compute_effective_hours',
        store=False,
        help='Tổng số giờ công thực tế đã làm (từ timesheet)'
    )
    
    remaining_hours = fields.Float(
        string='Giờ công còn lại',
        compute='_compute_remaining_hours',
        store=False,
        help='Số giờ công còn lại để hoàn thành'
    )
    
    # ========== COMPUTE & CONSTRAINTS ==========
    @api.depends('child_ids')
    def _compute_subtask_count(self):
        """Tính số lượng subtask"""
        for record in self:
            record.subtask_count = len(record.child_ids)
    
    @api.depends('state')
    def _compute_date_end(self):
        """Tính ngày kết thúc dựa trên trạng thái"""
        for record in self:
            if record.state == 'done':
                record.date_end = fields.Datetime.now()
            else:
                record.date_end = False
    
    def _compute_effective_hours(self):
        """Tính giờ công thực tế từ timesheet (sẽ được implement trong project_timesheet)"""
        for record in self:
            # Placeholder: sẽ được tính từ account.analytic.line trong module project_timesheet
            record.effective_hours = 0.0
    
    def _compute_remaining_hours(self):
        """Tính giờ công còn lại"""
        for record in self:
            if record.planned_hours > 0:
                record.remaining_hours = record.planned_hours - record.effective_hours
            else:
                record.remaining_hours = 0.0
    
    # ========== THÔNG TIN BỔ SUNG ==========
    sequence = fields.Integer(
        string='Thứ tự',
        default=10,
        help='Thứ tự hiển thị'
    )
    
    tag_ids = fields.Many2many(
        'project.task.tag',
        'project_task_tag_rel',
        'task_id',
        'tag_id',
        string='Nhãn',
        help='Các nhãn phân loại công việc'
    )
    
    color = fields.Integer(
        string='Màu sắc',
        default=0,
        help='Màu sắc hiển thị (nếu có Gantt chart)'
    )
    
    is_subtask = fields.Boolean(
        string='Là Subtask',
        compute='_compute_is_subtask',
        store=True,
        help='Công việc này có phải là subtask không'
    )
    
    @api.depends('parent_id')
    def _compute_is_subtask(self):
        """Kiểm tra có phải subtask không"""
        for record in self:
            record.is_subtask = bool(record.parent_id)
    
    # ========== ORM METHODS ==========
    def action_set_todo(self):
        """Chuyển trạng thái sang Cần làm"""
        self.write({'state': 'todo'})
    
    def action_set_in_progress(self):
        """Chuyển trạng thái sang Đang làm"""
        self.write({'state': 'in_progress'})
    
    def action_set_review(self):
        """Chuyển trạng thái sang Đang xem xét"""
        self.write({'state': 'review'})
    
    def action_set_done(self):
        """Hoàn thành công việc"""
        self.write({
            'state': 'done',
            'progress': 100.0,
            'date_end': fields.Datetime.now()
        })
    
    def action_set_cancelled(self):
        """Hủy công việc"""
        self.write({'state': 'cancelled'})
    
    def action_view_subtasks(self):
        """Mở view subtask của công việc"""
        action = {
            'name': 'Subtask',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_parent_id': self.id,
                'default_project_id': self.project_id.id,
            },
        }
        return action
    
    @api.model
    def create(self, vals):
        """Xử lý khi tạo task mới"""
        # Nếu có parent_id, tự động set project_id từ parent
        if vals.get('parent_id') and not vals.get('project_id'):
            parent = self.env['project.task'].browse(vals['parent_id'])
            vals['project_id'] = parent.project_id.id
        return super(ProjectTask, self).create(vals)


class ProjectTaskTag(models.Model):
    _name = 'project.task.tag'
    _description = 'Nhãn Công việc'
    _order = 'name'

    name = fields.Char(
        string='Tên nhãn',
        required=True,
        translate=True
    )
    
    color = fields.Integer(
        string='Màu sắc',
        default=0
    )
