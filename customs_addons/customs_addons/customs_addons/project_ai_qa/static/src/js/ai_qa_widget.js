/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class AIQAWidget extends Component {
    static template = "project_ai_qa.AIQAWidget";
    
    setup() {
        this.state = {
            question: "",
            answer: "",
            loading: false,
            history: []
        };
    }
    
    async askAI() {
        if (!this.state.question.trim()) {
            return;
        }
        
        this.state.loading = true;
        try {
            const response = await this.env.services.orm.call(
                "project.ai.qa",
                "create",
                [{
                    question: this.state.question,
                    project_id: this.props.record.resId || false,
                }]
            );
            
            if (response && response.length > 0) {
                const qa = await this.env.services.orm.read(
                    "project.ai.qa",
                    [response[0]],
                    ["answer", "state"]
                );
                
                if (qa && qa[0]) {
                    this.state.answer = qa[0].answer || "";
                }
            }
        } catch (error) {
            this.state.answer = `<p>Lỗi: ${error.message}</p>`;
        } finally {
            this.state.loading = false;
        }
    }
}

AIQAWidget.props = {
    record: Object,
};

registry.category("fields").add("ai_qa_widget", AIQAWidget);
