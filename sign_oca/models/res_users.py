# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, modules


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def sign_oca_request_user_count(self):
        requests = {}
        domain = [
            ("request_id.state", "=", "sent"),
            ("model", "!=", False),
            (
                "partner_id",
                "child_of",
                [self.env.user.partner_id.commercial_partner_id.id],
            ),
        ]
        signer_model = self.env["sign.oca.request.signer"]
        signer_groups = signer_model.read_group(domain, ["model"], ["model"])
        for signer_group in signer_groups:
            model = signer_group["model"]
            Model = self.env[model].with_user(self.env.user)
            signers = signer_model.search(signer_group.get("__domain"))
            if signers:
                total_records = Model.with_context(active_test=False).search_count(
                    [("id", "in", signers.mapped("res_id"))]
                )
                if total_records > 0:
                    record = self.env[model]
                    requests[model] = {
                        "name": record._description,
                        "model": model,
                        "icon": modules.module.get_module_icon(record._original_module),
                        "total_records": total_records,
                    }
        return list(requests.values())
