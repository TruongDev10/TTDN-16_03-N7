# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal


class ProjectPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        """Chuẩn bị giá trị cho portal layout"""
        values = super(ProjectPortal, self)._prepare_portal_layout_values()
        # Đếm số lượng dự án và công việc của khách hàng
        partner = request.env.user.partner_id
        project_count = request.env['project.project'].search_count([
            ('partner_id', '=', partner.id)
        ])
        task_count = request.env['project.task'].search_count([
            ('project_id.partner_id', '=', partner.id)
        ])
        values.update({
            'project_count': project_count,
            'task_count': task_count,
        })
        return values

    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, sortby=None, filterby=None, **kw):
        """Trang danh sách dự án của khách hàng"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        
        Project = request.env['project.project']
        domain = [('partner_id', '=', partner.id)]
        
        # Sắp xếp
        if not sortby:
            sortby = 'date'
        sortings = {
            'date': {'label': 'Ngày', 'order': 'date_start desc'},
            'name': {'label': 'Tên', 'order': 'name'},
            'state': {'label': 'Trạng thái', 'order': 'state'},
        }
        order = sortings.get(sortby, sortings['date'])['order']
        
        # Lọc
        if not filterby:
            filterby = 'all'
        filters = {
            'all': {'label': 'Tất cả', 'domain': []},
            'active': {'label': 'Đang thực hiện', 'domain': [('state', '=', 'active')]},
            'done': {'label': 'Hoàn thành', 'domain': [('state', '=', 'done')]},
        }
        domain += filters.get(filterby, filters['all'])['domain']
        
        # Phân trang
        project_count = Project.search_count(domain)
        pager = request.website.pager(
            url="/my/projects",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=project_count,
            page=page,
            step=self._items_per_page
        )
        projects = Project.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'projects': projects,
            'page_name': 'projects',
            'pager': pager,
            'sortby': sortby,
            'filterby': filterby,
            'sortings': sortings,
            'filters': filters,
        })
        return request.render("project_portal.portal_my_projects", values)

    @http.route(['/my/projects/<int:project_id>'], type='http', auth="user", website=True)
    def portal_project_page(self, project_id=None, access_token=None, **kw):
        """Trang chi tiết dự án"""
        try:
            project_sudo = self._document_check_access('project.project', project_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = {
            'project': project_sudo,
            'page_name': 'project',
        }
        return request.render("project_portal.portal_project_page", values)

    @http.route(['/my/tasks', '/my/tasks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, sortby=None, filterby=None, **kw):
        """Trang danh sách công việc của khách hàng"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        
        Task = request.env['project.task']
        domain = [('project_id.partner_id', '=', partner.id)]
        
        # Sắp xếp
        if not sortby:
            sortby = 'date'
        sortings = {
            'date': {'label': 'Ngày', 'order': 'date_deadline desc'},
            'name': {'label': 'Tên', 'order': 'name'},
            'state': {'label': 'Trạng thái', 'order': 'state'},
        }
        order = sortings.get(sortby, sortings['date'])['order']
        
        # Lọc
        if not filterby:
            filterby = 'all'
        filters = {
            'all': {'label': 'Tất cả', 'domain': []},
            'todo': {'label': 'Cần làm', 'domain': [('state', '=', 'todo')]},
            'in_progress': {'label': 'Đang làm', 'domain': [('state', '=', 'in_progress')]},
            'done': {'label': 'Hoàn thành', 'domain': [('state', '=', 'done')]},
        }
        domain += filters.get(filterby, filters['all'])['domain']
        
        # Phân trang
        task_count = Task.search_count(domain)
        pager = request.website.pager(
            url="/my/tasks",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        tasks = Task.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'tasks': tasks,
            'page_name': 'tasks',
            'pager': pager,
            'sortby': sortby,
            'filterby': filterby,
            'sortings': sortings,
            'filters': filters,
        })
        return request.render("project_portal.portal_my_tasks", values)

    @http.route(['/my/tasks/<int:task_id>'], type='http', auth="user", website=True)
    def portal_task_page(self, task_id=None, access_token=None, **kw):
        """Trang chi tiết công việc"""
        try:
            task_sudo = self._document_check_access('project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = {
            'task': task_sudo,
            'page_name': 'task',
        }
        return request.render("project_portal.portal_task_page", values)
