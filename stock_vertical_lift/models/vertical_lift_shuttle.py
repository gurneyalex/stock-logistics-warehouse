# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import socket
import ssl

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class VerticalLiftShuttle(models.Model):
    _name = "vertical.lift.shuttle"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Vertical Lift Shuttle"

    name = fields.Char()
    mode = fields.Selection(
        [("pick", "Pick"), ("put", "Put"), ("inventory", "Inventory")],
        default="pick",
        required=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        required=True,
        domain="[('vertical_lift_kind', '=', 'shuttle')]",
        ondelete="restrict",
        help="The Shuttle source location for Pick operations "
        "and destination location for Put operations.",
    )
    hardware = fields.Selection(
        selection="_selection_hardware", default="simulation", required=True
    )
    server = fields.Char(help="hostname or IP address of the server")
    port = fields.Integer(
        help="network port of the server on which to send the message"
    )
    use_tls = fields.Boolean(
        help="set this if the server expects TLS wrapped communication"
    )

    _sql_constraints = [
        (
            "location_id_unique",
            "UNIQUE(location_id)",
            "You cannot have two shuttles using the same location.",
        )
    ]

    @api.model
    def _selection_hardware(self):
        return [("simulation", "Simulation")]

    @property
    def _model_for_mode(self):
        return {
            "pick": "vertical.lift.operation.pick",
            "put": "vertical.lift.operation.put",
            "inventory": "vertical.lift.operation.inventory",
        }

    @property
    def _screen_view_for_mode(self):
        return {
            "pick": (
                "stock_vertical_lift."
                "vertical_lift_operation_pick_screen_view"
            ),
            "put": (
                "stock_vertical_lift."
                "vertical_lift_operation_put_screen_view"
            ),
            "inventory": (
                "stock_vertical_lift."
                "vertical_lift_operation_inventory_screen_view"
            ),
        }

    def _hardware_send_message(self, payload):
        """default implementation for message sending

        If in hardware is 'simulation' then display a simple message.
        Otherwise defaults to connecting to server:port using a TCP socket
        (optionnally wrapped with TLS) and sending the payload, then waiting
        for a response and disconnecting.

        :param payload: a bytes object containing the payload

        """
        self.ensure_one()
        _logger.info('send %r', payload)
        if self.hardware == "simulation":
            self.env.user.notify_info(message=payload,
                                      title=_("Lift Simulation"))
            return True
        else:
            conn = self._hardware_get_server_connection()
            try:
                offset = 0
                while True:
                    size = conn.send(payload[offset:])
                    if not size:
                        break
                    offset += size
                response = self._hardware_recv_response(conn)
                _logger.info('recv %r', response)
                return self._check_server_response(payload, response)
            finally:
                self._hardware_release_server_connection(self, conn)

    def _hardware_recv_response(self, conn):
        """Default implementation expects the remote server to close()
        the socket after sending the reponse.
        Override to match the protocol implemented by the hardware.

        :param conn: a socket connected to the server
        :return: the response sent by the server, as a bytes object
        """
        response = b''
        chunk = True
        while chunk:
            chunk = conn.recv(1024)
            response += chunk
        return response

    def _check_server_response(self, payload, response):
        """Use this to check if the response is a success or a failure

        :param payload: the payload sent
        :param response: the response received
        :return: True if the response is a succes, False otherwise
        """
        return True

    def _hardware_release_server_connection(self, conn):
        conn.close()

    def _hardware_get_server_connection(self):
        """This implementation will yield a new connection to the server
        and close() it when exiting the context.
        Override to match the communication protocol of your hardware"""
        conn = socket.create_connection((self.server, self.port))
        if self.use_tls:
            ctx = ssl.create_default_context()
            self._hardware_update_tls_context(ctx)
            conntls = ctx.wrap_socket(conn, server_hostname=self.server)
            return conntls
        else:
            return conn

    def _hardware_update_tls_context(self, context):
        """Update the TLS context, e.g. to add a client certificate.

        This method does nothing, override to match your communication
        protocol."""
        pass

    def _operation_for_mode(self):
        model = self._model_for_mode[self.mode]
        record = self.env[model].search([("shuttle_id", "=", self.id)])
        if not record:
            record = self.env[model].create({"shuttle_id": self.id})
        return record

    def action_open_screen(self):
        self.ensure_one()
        assert self.mode in ("pick", "put", "inventory")
        screen_xmlid = self._screen_view_for_mode[self.mode]
        operation = self._operation_for_mode()
        operation.on_screen_open()
        return {
            "type": "ir.actions.act_window",
            "res_model": operation._name,
            "views": [[self.env.ref(screen_xmlid).id, "form"]],
            "res_id": operation.id,
            "target": "fullscreen",
            "flags": {
                "headless": True,
                "form_view_initial_mode": "edit",
                "no_breadcrumbs": True,
            },
        }

    def action_menu(self):
        menu_xmlid = "stock_vertical_lift.vertical_lift_shuttle_form_menu"
        return {
            "type": "ir.actions.act_window",
            "res_model": "vertical.lift.shuttle",
            "views": [[self.env.ref(menu_xmlid).id, "form"]],
            "name": _("Menu"),
            "target": "new",
            "res_id": self.id,
        }

    def action_manual_barcode(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "vertical.lift.shuttle.manual.barcode",
            "view_mode": "form",
            "name": _("Barcode"),
            "target": "new",
        }

    # TODO: should the mode be changed on all the shuttles at the same time?
    def switch_pick(self):
        self.mode = "pick"
        return self.action_open_screen()

    def switch_put(self):
        self.mode = "put"
        return self.action_open_screen()

    def switch_inventory(self):
        self.mode = "inventory"
        return self.action_open_screen()


class VerticalLiftShuttleManualBarcode(models.TransientModel):
    _name = "vertical.lift.shuttle.manual.barcode"
    _description = "Action to input a barcode"

    barcode = fields.Char(string="Barcode")

    @api.multi
    def button_save(self):
        active_id = self.env.context.get("active_id")
        model = self.env.context.get("active_model")
        record = self.env[model].browse(active_id).exists()
        if not record:
            return
        if self.barcode:
            record.on_barcode_scanned(self.barcode)
