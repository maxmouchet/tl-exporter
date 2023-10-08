import re
from collections.abc import Iterator

import chompjs
import httpx
from prometheus_client.metrics_core import CounterMetricFamily, GaugeMetricFamily

from tl_exporter.logger import logger


class Collector:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
    ):
        self.username = username
        self.password = password
        self.client = httpx.Client(base_url=base_url)

    def authenticate(self) -> None:
        logger.info("Authenticating...")
        self.client.post(
            "logon.cgi",
            data={
                "username": self.username,
                "password": self.password,
                "cpassword": "",
                "logon": "Login",
            },
        )

    def get(self, path: str) -> str:
        res = self.client.get(path)
        res.raise_for_status()
        if "logonInfo" in res.text:
            self.authenticate()
            res = self.client.get(path)
            res.raise_for_status()
        return res.text

    def collect(self) -> Iterator[CounterMetricFamily | GaugeMetricFamily]:
        logger.info("Starting collection")

        html = self.get("SystemInfoRpm.htm")
        device_info_m = re.search(r"var info_ds = ({.+?});", html, re.DOTALL)
        device_info = chompjs.parse_js_object(device_info_m.group(1))  # type: ignore

        html = self.get("PortStatisticsRpm.htm")
        device_stats_m = re.search(r"var all_info = ({.+?});", html, re.DOTALL)
        device_stats = chompjs.parse_js_object(device_stats_m.group(1))  # type: ignore

        version_metric = GaugeMetricFamily(
            "device_version", "Device Version", labels=["mac", "hardware", "firmware"]
        )
        version_metric.add_metric(
            [
                device_info["macStr"][0],
                device_info["hardwareStr"][0],
                device_info["firmwareStr"][0],
            ],
            1.0,
        )

        port_state_metric = GaugeMetricFamily(
            "port_state",
            "Port State (Disabled, Enabled)",
            labels=["mac", "port"],
        )
        link_state_metric = GaugeMetricFamily(
            "link_state",
            "Link State (Link Down, Auto, 10Half, 10Full, 100Half, 100Full, 1000Full)",
            labels=["mac", "port"],
        )
        tx_good_packets_metric = CounterMetricFamily(
            "tx_good_packets_total", "", labels=["mac", "port"]
        )
        tx_bad_packets_metric = CounterMetricFamily(
            "tx_bad_packets_total", "", labels=["mac", "port"]
        )
        rx_good_packets_metric = CounterMetricFamily(
            "rx_good_packets_total", "", labels=["mac", "port"]
        )
        rx_bad_packets_metric = CounterMetricFamily(
            "rx_bad_packets_total", "", labels=["mac", "port"]
        )

        for port in range(len(device_stats["pkts"]) // 4):
            labels = [device_info["macStr"][0], str(port)]
            port_state_metric.add_metric(labels, device_stats["state"][port])
            link_state_metric.add_metric(labels, device_stats["link_status"][port])
            tx_good_packets_metric.add_metric(labels, device_stats["pkts"][4 * port])
            tx_bad_packets_metric.add_metric(labels, device_stats["pkts"][4 * port + 1])
            rx_good_packets_metric.add_metric(
                labels, device_stats["pkts"][4 * port + 2]
            )
            rx_bad_packets_metric.add_metric(labels, device_stats["pkts"][4 * port + 3])

        yield version_metric
        yield port_state_metric
        yield link_state_metric
        yield tx_good_packets_metric
        yield tx_bad_packets_metric
        yield rx_good_packets_metric
        yield rx_bad_packets_metric
