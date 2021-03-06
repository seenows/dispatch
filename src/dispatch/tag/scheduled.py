"""
.. module: dispatch.tag.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from schedule import every

from dispatch.decorators import background_task
from dispatch.plugins.base import plugins
from dispatch.scheduler import scheduler
from dispatch.tag import service as tag_service
from dispatch.tag.models import TagCreate

log = logging.getLogger(__name__)


@scheduler.add(every(1).hour, name="tag-sync")
@background_task
def sync_tags(db_session=None):
    """Syncs tags from external sources."""
    for p in plugins.all(plugin_type="tag"):
        log.debug(f"Getting tags via: {p.slug}")
        for app in p.get():
            log.debug(f"Adding Tag. Tag: {app}")
            tag_in = TagCreate(**app)
            tag = tag_service.get_by_name(db_session=db_session, name=tag_in.name)

            if tag:
                tag_service.update(db_session=db_session, tag=tag, tag_in=tag_in)
            else:
                tag_service.create(db_session=db_session, tag_in=tag_in)
