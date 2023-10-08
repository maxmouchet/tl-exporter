import logging
from wsgiref.simple_server import make_server

from prometheus_client import (
    GC_COLLECTOR,
    PLATFORM_COLLECTOR,
    PROCESS_COLLECTOR,
    REGISTRY,
    make_wsgi_app,
)

from tl_exporter.collector import Collector
from tl_exporter.settings import Settings


def main() -> None:
    settings = Settings()
    logging.basicConfig(
        format=settings.log_format,
        level=logging.getLevelName(settings.log_level.upper()),
    )
    collector = Collector(
        settings.tl_base_url,
        settings.tl_username,
        settings.tl_password,
    )
    REGISTRY.register(collector)
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)
    app = make_wsgi_app()
    httpd = make_server(settings.host, settings.port, app)
    httpd.serve_forever()
