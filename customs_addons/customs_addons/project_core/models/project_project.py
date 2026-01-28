# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class ProjectProject(models.Model):
    _name = 'project.project'
    _description = 'Dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, name'

    # ========== THÔNG TIN CƠ BẢN ==========
    name = fields.Char(
        string='Tên dự án',
        required=True,
        tracking=True,
        help='Tên của dự án'
    )
    
    code = fields.Char(
        string='Mã dự án',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        tracking=True,
        help='Mã định danh duy nhất của dự án'
    )
    
    description = fields.Text(
        string='Mô tả',
        help='Mô tả chi tiết về dự án'
    )
    
    # ========== THÔNG TIN KHÁCH HÀNG ==========
    partner_id = fields.Many2one(
        'res.partner',
        string='Khách hàng',
        tracking=True,
        help='Khách hàng của dự án'
    )
    
    # ========== THỜI GIAN ==========
    date_start = fields.Date(
        string='Ngày bắt đầu',
        default=fields.Date.today,
        tracking=True,
        help='Ngày bắt đầu dự án'
    )
    
    date_end = fields.Date(
        string='Ngày kết thúc',
        tracking=True,
        help='Ngày kết thúc dự án'
    )
    
    # ========== TRẠNG THÁI ==========
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('active', 'Đang thực hiện'),
        ('on_hold', 'Tạm dừng'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string='Trạng thái', default='draft', tracking=True, required=True)
    
    # ========== TIẾN ĐỘ ==========
    progress = fields.Float(
        string='Tiến độ (%)',
        default=0.0,
        tracking=True,
        help='Tiến độ hoàn thành dự án (0-100%)'
    )
    
    # ========== QUAN HỆ ==========
    milestone_ids = fields.One2many(
        'project.milestone',
        'project_id',
        string='Milestone',
        help='Các milestone của dự án'
    )
    
    milestone_count = fields.Integer(
        string='Số lượng Milestone',
        compute='_compute_milestone_count',
        store=False
    )
    
    # ========== THÔNG TIN BỔ SUNG ==========
    user_id = fields.Many2one(
        'res.users',
        string='Người quản lý',
        default=lambda self: self.env.user,
        tracking=True,
        help='Người quản lý dự án'
    )
    
    tag_ids = fields.Many2many(
        'project.tag',
        'project_project_tag_rel',
        'project_id',
        'tag_id',
        string='Nhãn',
        help='Các nhãn phân loại dự án'
    )
    
    color = fields.Integer(
        string='Màu sắc',
        default=0,
        help='Màu sắc hiển thị (nếu có Gantt chart)'
    )
    
    # ========== COMPUTE & CONSTRAINTS ==========
    @api.depends('milestone_ids')
    def _compute_milestone_count(self):
        """Tính số lượng milestone của dự án"""
        for record in self:
            record.milestone_count = len(record.milestone_ids)
    
    # ========== ORM METHODS ==========
    @api.model
    def create(self, vals):
        """Tự động tạo mã dự án khi tạo mới"""
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('project.project') or 'New'
        return super(ProjectProject, self).create(vals)
    
    def action_set_active(self):
        """Chuyển trạng thái sang Đang thực hiện"""
        self.write({'state': 'active'})
    
    def action_set_on_hold(self):
        """Tạm dừng dự án"""
        self.write({'state': 'on_hold'})
    
    def action_set_done(self):
        """Hoàn thành dự án"""
        self.write({'state': 'done', 'progress': 100.0})
    
    def action_set_cancelled(self):
        """Hủy dự án"""
        self.write({'state': 'cancelled'})
    
    def action_view_milestones(self):
        """Mở view milestone của dự án"""
        action = {
            'name': 'Milestone',
            'type': 'ir.actions.act_window',
            'res_model': 'project.milestone',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
        return action
