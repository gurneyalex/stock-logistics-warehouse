# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import os

from odoo import _, http
from odoo.exceptions import MissingError
from odoo.http import request

_logger = logging.getLogger(__name__)


class ZippcubeController(http.Controller):
    weight_keys = ("weight",)
    measures_keys = ("length", "width", "height")
    expected_keys = ("secret", "barcode") + weight_keys + measures_keys

    @http.route(
        "/stock/zipcube/<string:zippcube_device_name>/measurement",
        type="json",
        auth="none",
    )
    def measurement_legacy(self, zippcube_device_name):
        """For the misspelled zipcube (with just one 'p')"""
        return self.measurement(zippcube_device_name)

    @http.route(
        "/stock/zippcube/<string:zippcube_device_name>/measurement",
        type="json",
        auth="none",
    )
    def measurement(self, zippcube_device_name):
        data = request.jsonrequest
        _logger.info("/measurement, data received: f{data}")

        env = request.env(su=True)
        zippcube = env["zippcube.device"].search(
            [("name", "=", zippcube_device_name)], limit=1
        )
        if not zippcube:
            raise MissingError(
                _(f"No such Zippcube with name f{zippcube_device_name}.")
            )

        keys_missing = set(self.expected_keys) - set(data)
        if keys_missing:
            error_msg = _(f"Wrong data format: f{data}. Keys missing: f{keys_missing}.")
            _logger.error(error_msg)
            raise ValueError(error_msg)

        self._check_secret(data["secret"])
        # convert the float values passed as strings to floats
        data = self._convert_floats(data)
        zippcube._update_packaging_measures(data)
        return True

    def _convert_floats(self, data):
        for key in self.weight_keys + self.measures_keys:
            value = data[key]
            if isinstance(value, str):
                value = float(value.replace(",", "."))
                if key in self.measures_keys:
                    # lengths are in cm -> convert to mm
                    value *= 10
                data[key] = value
        return data

    def _check_secret(self, secret):
        if secret and secret == os.environ.get("ZIPPCUBE_SECRET"):
            return True
        else:
            _logger.error(
                "Zippcube secret mismatch: %r != %r",
                secret,
                os.environ.get("ZIPPCUBE_SECRET", ""),
            )
            raise http.AuthenticationError()
