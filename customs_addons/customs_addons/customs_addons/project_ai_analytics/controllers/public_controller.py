# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class ProjectPublicController(http.Controller):

    @http.route('/project/public/<int:project_id>', type='http', auth='public', website=True)
    def public_project_info(self, project_id=None, **kw):
        """Trang công khai thông tin dự án"""
        try:
            project = request.env['project.project'].sudo().browse(project_id)
            
            # Kiểm tra quyền công khai
            if not project.is_public_progress and not project.is_public_members:
                return request.not_found()
            
            # Lấy thông tin công khai
            public_data = {
                'project': project,
                'show_progress': project.is_public_progress,
                'show_members': project.is_public_members,
                'show_tasks': project.is_public_progress,
            }
            
            # Lấy đánh giá AI nếu công khai
            if project.is_public_progress and project.ai_evaluation_ids:
                public_data['latest_evaluation'] = project.ai_evaluation_ids.sorted('evaluation_date', reverse=True)[0]
            
            return request.render('project_ai_analytics.public_project_info', public_data)
        except:
            return request.not_found()
