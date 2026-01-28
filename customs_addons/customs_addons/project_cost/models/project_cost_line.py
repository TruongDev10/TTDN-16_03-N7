# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class ProjectCostLine(models.Model):
    _name = 'project.cost.line'
    _description = 'Dòng Chi phí'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # ========== THÔNG TIN CƠ BẢN ==========
    name = fields.Char(
        string='Mô tả',
        required=True,
        tracking=True,
        help='Mô tả chi phí'
    )
    
    date = fields.Date(
        string='Ngày',
        required=True,
        default=fields.Date.today,
        tracking=True,
        index=True,
        help='Ngày phát sinh chi phí'
    )
    
    # ========== QUAN HỆ ==========
    project_id = fields.Many2one(
        'project.project',
        string='Dự án',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True,
        help='Dự án phát sinh chi phí'
    )
    
    task_id = fields.Many2one(
        'project.task',
        string='Công việc',
        ondelete='cascade',
        tracking=True,
        index=True,
        help='Công việc phát sinh chi phí'
    )
    
    timesheet_id = fields.Many2one(
        'account.analytic.line',
        string='Timesheet',
        ondelete='set null',
        tracking=True,
        help='Timesheet liên quan (nếu chi phí được tính từ timesheet)'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân viên',
        tracking=True,
        help='Nhân viên liên quan đến chi phí'
    )
    
    # ========== CHI PHÍ ==========
    hours = fields.Float(
        string='Giờ công',
        default=0.0,
        tracking=True,
        help='Số giờ công (từ timesheet hoặc nhập thủ công)'
    )
    
    hourly_rate = fields.Float(
        string='Mức lương theo giờ',
        default=0.0,
        tracking=True,
        help='Mức lương theo giờ của nhân viên'
    )
    
    cost_amount = fields.Float(
        string='Chi phí',
        compute='_compute_cost_amount',
        store=True,
        tracking=True,
        help='Chi phí = Giờ công × Mức lương theo giờ'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id,
        help='Đơn vị tiền tệ'
    )
    
    # ========== TRẠNG THÁI ==========
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('invoiced', 'Đã xuất hóa đơn'),
        ('paid', 'Đã thanh toán')
    ], string='Trạng thái', default='draft', tracking=True, required=True)
    
    # ========== COMPUTE ==========
    @api.depends('hours', 'hourly_rate')
    def _compute_cost_amount(self):
        """Tính chi phí = giờ công × mức lương theo giờ"""
        for record in self:
            record.cost_amount = record.hours * record.hourly_rate
    
    # ========== ORM METHODS ==========
    @api.model
    def create(self, vals):
        """Xử lý khi tạo cost line mới"""
        # Nếu có timesheet_id, tự động lấy thông tin
        if vals.get('timesheet_id'):
            timesheet = self.env['account.analytic.line'].browse(vals['timesheet_id'])
            if not vals.get('hours'):
                vals['hours'] = timesheet.unit_amount
            if not vals.get('task_id'):
                vals['task_id'] = timesheet.task_id.id
            if not vals.get('project_id'):
                vals['project_id'] = timesheet.project_id.id
            if not vals.get('employee_id'):
                vals['employee_id'] = timesheet.employee_id.id
        
        # Nếu có employee_id, tự động lấy hourly_rate
        if vals.get('employee_id') and not vals.get('hourly_rate'):
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            vals['hourly_rate'] = employee.hourly_rate
        
        return super(ProjectCostLine, self).create(vals)
    
    def action_confirm(self):
        """Xác nhận chi phí"""
        self.write({'state': 'confirmed'})
    
    def action_set_invoiced(self):
        """Đánh dấu đã xuất hóa đơn"""
        self.write({'state': 'invoiced'})
    
    def action_set_paid(self):
        """Đánh dấu đã thanh toán"""
        self.write({'state': 'paid'})
