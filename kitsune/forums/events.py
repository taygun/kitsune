from django.contrib.sites.models import Site

from tidings.events import InstanceEvent, EventUnion
from tower import ugettext_lazy as _lazy

from kitsune.forums.models import Thread, Forum
from kitsune.sumo.email_utils import emails_with_users_and_watches


class NewPostEvent(InstanceEvent):
    """An event which fires when a thread receives a reply

    Firing this also notifies watchers of the containing forum.

    """
    event_type = 'thread reply'
    content_type = Thread

    def __init__(self, reply):
        super(NewPostEvent, self).__init__(reply.thread)
        # Need to store the reply for _mails
        self.reply = reply

    def fire(self, **kwargs):
        """Notify not only watchers of this thread but of the parent forum."""
        return EventUnion(self, NewThreadEvent(self.reply)).fire(**kwargs)

    def _mails(self, users_and_watches):
        c = {'post': self.reply.content,
             'post_html': self.reply.content_parsed,
             'author': self.reply.author.username,
             'host': Site.objects.get_current().domain,
             'thread': self.reply.thread.title,
             'forum': self.reply.thread.forum.name,
             'post_url': self.reply.get_absolute_url()}

        return emails_with_users_and_watches(
            subject=_lazy(u'Re: {forum} - {thread}'),
            text_template='forums/email/new_post.ltxt',
            html_template='forums/email/new_post.html',
            context_vars=c,
            users_and_watches=users_and_watches)


class NewThreadEvent(InstanceEvent):
    """An event which fires when a new thread is added to a forum"""

    event_type = 'forum thread'
    content_type = Forum

    def __init__(self, post):
        super(NewThreadEvent, self).__init__(post.thread.forum)
        # Need to store the post for _mails
        self.post = post

    def _mails(self, users_and_watches):
        c = {'post': self.post.content,
             'post_html': self.post.content_parsed,
             'author': self.post.author.username,
             'host': Site.objects.get_current().domain,
             'thread': self.post.thread.title,
             'forum': self.post.thread.forum.name,
             'post_url': self.post.thread.get_absolute_url()}

        return emails_with_users_and_watches(
            subject=_lazy(u'{forum} - {thread}'),
            text_template='forums/email/new_thread.ltxt',
            html_template='forums/email/new_thread.html',
            context_vars=c,
            users_and_watches=users_and_watches)
