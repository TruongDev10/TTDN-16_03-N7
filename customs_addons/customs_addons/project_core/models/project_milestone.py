# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectMilestone(models.Model):
    _name = 'project.milestone'
    _description = 'Milestone'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_deadline asc, name'

    # ========== THÔNG TIN CƠ BẢN ==========
    name = fields.Char(
        string='Tên milestone',
        required=True,
        tracking=True,
        help='Tên của milestone'
    )
    
    description = fields.Text(
        string='Mô tả',
        help='Mô tả chi tiết về milestone'
    )
    
    # ========== QUAN HỆ ==========
    project_id = fields.Many2one(
        'project.project',
        string='Dự án',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Dự án chứa milestone này'
    )
    
    # ========== THỜI GIAN ==========
    date_deadline = fields.Date(
        string='Ngày deadline',
        required=True,
        tracking=True,
        help='Ngày deadline của milestone'
    )
    
    date_achieved = fields.Date(
        string='Ngày hoàn thành',
        tracking=True,
        help='Ngày thực tế hoàn thành milestone'
    )
    
    # ========== TRẠNG THÁI ==========
    state = fields.Selection([
        ('planned', 'Đã lên kế hoạch'),
        ('in_progress', 'Đang thực hiện'),
        ('achieved', 'Đã đạt được'),
        ('missed', 'Đã trễ hạn')
    ], string='Trạng thái', default='planned', tracking=True, required=True)
    
    # ========== COMPUTE ==========
    is_overdue = fields.Boolean(
        string='Quá hạn',
        compute='_compute_is_overdue',
        store=True,
        help='Milestone có quá hạn không'
    )
    
    @api.depends('date_deadline', 'state', 'date_achieved')
    def _compute_is_overdue(self):
        """Tính toán milestone có quá hạn không"""
        today = fields.Date.today()
        for record in self:
            if record.state not in ['achieved'] and record.date_deadline:
                record.is_overdue = record.date_deadline < today
            else:
                record.is_overdue = False
    
    # ========== ORM METHODS ==========
    def action_set_achieved(self):
        """Đánh dấu milestone đã đạt được"""
        self.write({
            'state': 'achieved',
            'date_achieved': fields.Date.today()
        })
    
    def action_set_in_progress(self):
        """Chuyển trạng thái sang Đang thực hiện"""
        self.write({'state': 'in_progress'})
