# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = ['project.project', 'portal.mixin']
    _name = 'project.project'

    # ========== PORTAL FIELDS ==========
    portal_access_token = fields.Char(
        string='Token truy cập Portal',
        copy=False,
        help='Token để khách hàng truy cập portal'
    )
    
    # ========== PORTAL METHODS ==========
    def _get_portal_return_action(self):
        """Trả về action để mở project từ portal"""
        return self.env.ref('project_portal.action_project_project_portal')
    
    def _compute_access_url(self):
        """Tính URL truy cập portal"""
        super(ProjectProject, self)._compute_access_url()
        for record in self:
            record.access_url = f'/my/projects/{record.id}?access_token={record._get_portal_access_token()}'
    
    def _get_portal_access_token(self):
        """Lấy hoặc tạo portal access token"""
        if not self.portal_access_token:
            self.portal_access_token = self._generate_portal_access_token()
        return self.portal_access_token
    
    def _generate_portal_access_token(self):
        """Tạo portal access token"""
        return self.env['ir.model.data']._generate_unique_id()
