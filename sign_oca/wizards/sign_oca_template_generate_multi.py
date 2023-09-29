# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SignOcaTemplateGenerateMulti(models.TransientModel):
    _name = "sign.oca.template.generate.multi"
    _description = "Generate signature requests"

    model = fields.Char(string="Model", readonly=True)
    model_id = fields.Many2one(
        comodel_name="ir.model",
        compute="_compute_model_id",
        required=True,
    )
    template_id = fields.Many2one(
        comodel_name="sign.oca.template",
        domain="['|', ('model_id', '=', False),('model_id', '=', model_id)]",
        required=True,
    )
    message = fields.Html()

    @api.depends("model")
    def _compute_model_id(self):
        ir_model = self.env["ir.model"]
        for item in self:
            if item.model:
                item.model_id = ir_model.search([("model", "=", item.model)])
            else:
                item.model_id = item.model_id

    def _prepare_sign_oca_request_vals_from_record(self, record):
        roles = self.mapped("template_id.item_ids.role_id").filtered(
            lambda x: x.partner_type != "empty"
        )
        return {
            "name": self.template_id.name,
            "template_id": self.template_id.id,
            "record_ref": "%s,%s" % (record._name, record.id),
            "signatory_data": self.template_id._get_signatory_data(),
            "data": self.template_id.data,
            "signer_ids": [
                (
                    0,
                    0,
                    {
                        "partner_id": role._get_partner_from_record(record),
                        "role_id": role.id,
                    },
                )
                for role in roles
            ],
        }

    def _prepare_sign_oca_request_vals(self):
        vals = []
        for item in self.env[self.model].browse(self.env.context.get("active_ids")):
            vals.append(self._prepare_sign_oca_request_vals_from_record(item))
        return vals

    def _generate(self):
        return self.env["sign.oca.request"].create(
            self._prepare_sign_oca_request_vals()
        )

    def generate(self):
        requests = self._generate()
        for request in requests:
            request.action_send(message=self.message)
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sign_oca.sign_oca_request_act_window"
        )
        action["domain"] = [("id", "in", requests.ids)]
        return action
